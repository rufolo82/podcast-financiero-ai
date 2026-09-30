import html
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import dateutil.parser
from config import load_sources

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml, text/xml, */*'
}

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = re.sub(r'<[^>]+>', ' ', raw_html)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        dt = dateutil.parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None

def fetch_feed_articles(source: Dict[str, Any], max_age_hours: int = 48) -> List[Dict[str, Any]]:
    name = source.get("name", "Fuente")
    url = source.get("url", "")
    category = source.get("category", "General")
    articles = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.content, "xml")
        items = soup.find_all(["item", "entry"])
        now = datetime.now(timezone.utc)

        for item in items:
            title_tag = item.find(["title"])
            title = clean_html(title_tag.get_text()) if title_tag else ""
            if not title:
                continue

            desc_tag = item.find(["description", "summary", "content"])
            desc = clean_html(desc_tag.get_text()) if desc_tag else ""

            date_tag = item.find(["pubDate", "published", "updated", "dc:date"])
            date_str = date_tag.get_text() if date_tag else ""
            dt = parse_date(date_str)

            # Si tiene fecha y es más vieja que max_age_hours, la descartamos
            if dt:
                age_hours = (now - dt).total_seconds() / 3600
                if age_hours > max_age_hours:
                    continue

            articles.append({
                "source": name,
                "category": category,
                "title": title,
                "summary": desc[:500],
                "date": dt.isoformat() if dt else "Reciente"
            })

    except Exception as e:
        # Fallo silencioso con registro
        pass

    return articles

def collect_all_news(max_age_hours: int = 48) -> List[Dict[str, Any]]:
    sources = load_sources()
    all_articles = []
    seen_titles = set()

    for s in sources:
        if not s.get("enabled", True):
            continue
        arts = fetch_feed_articles(s, max_age_hours=max_age_hours)
        for a in arts:
            normalized_title = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]', '', a['title'].lower())
            if normalized_title and normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                all_articles.append(a)

    return all_articles

def format_articles_for_prompt(articles: List[Dict[str, Any]], max_chars: int = 40000) -> str:
    international = [a for a in articles if "España" not in a.get("category", "") and "IBEX" not in a.get("category", "")]
    national = [a for a in articles if "España" in a.get("category", "") or "IBEX" in a.get("category", "")]

    formatted_lines = []
    formatted_lines.append("=== NOTICIAS INTERNACIONALES (WALL STREET, FED, EUROPA, MACRO) ===")
    for a in international[:40]:
        formatted_lines.append(f"• [{a['source']}] {a['title']}")
        if a['summary']:
            formatted_lines.append(f"  Detalle: {a['summary']}")

    formatted_lines.append("\n=== NOTICIAS MERCADO ESPAÑOL (IBEX 35) ===")
    for a in national[:15]:
        formatted_lines.append(f"• [{a['source']}] {a['title']}")
        if a['summary']:
            formatted_lines.append(f"  Detalle: {a['summary']}")

    content_str = "\n".join(formatted_lines)
    return content_str[:max_chars]
