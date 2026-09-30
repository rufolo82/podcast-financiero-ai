import json
import urllib.request
import re
import time
from datetime import datetime
import pytz
from config import GEMINI_API_KEY, GEMINI_MODEL, SCRIPTS_DIR

DIAS_SEMANA = {
    0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
    4: "viernes", 5: "sábado", 6: "domingo"
}

MESES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

def get_current_date_madrid():
    madrid_tz = pytz.timezone("Europe/Madrid")
    now = datetime.now(madrid_tz)
    dia_semana = DIAS_SEMANA[now.weekday()]
    mes = MESES[now.month]
    fecha_completa = f"{dia_semana}, {now.day} de {mes} de {now.year}"
    hora = now.strftime("%H:%M")
    return now, fecha_completa, hora, dia_semana

def build_prompt(news_content: str, fecha_completa: str, hora: str, dia_semana: str) -> str:
    return f"""Eres un equipo de producción de podcasts financieros de primer nivel. Tu objetivo es crear el guion para un episodio conversacional, completo y dinámico entre dos presentadores: Ana (voz principal) y Carlos (analista experto).

FECHA Y HORA DE EMISIÓN: {fecha_completa}, a las {hora} horas (horario de Madrid).
DÍA DE LA SEMANA: {dia_semana}

REGLAS ESTRICTAS DE FORMATO Y CONTENIDO:

1. **SIN INTRODUCCIÓN VACÍA**: No incluyas saludos genéricos de cortesía ("Hola", "Buenos días", "Bienvenidos al podcast"). El guion debe empezar DIRECTAMENTE con la primera frase de fecha y el análisis.

2. **FECHA EXACTA EN LA PRIMERA FRASE**: La PRIMERA intervención de Ana debe comenzar explícitamente diciendo: "Hoy, {fecha_completa}, a las {hora} horas...". No uses expresiones ambiguas como "esta semana", "estos días" o "recientemente".

3. **DISTRIBUCIÓN GEOGRÁFICA (70-80% INTERNACIONAL)**:
   - Prioriza Wall Street (S&P 500, Nasdaq, Dow Jones), la Reserva Federal (Fed), datos macroeconómicos de EEUU, inflación, tipos de interés y deuda soberana.
   - Mercados europeos (Eurostoxx 50, DAX, CAC 40), BCE y energía/materias primas.
   - Solo menciona el IBEX 35 o bolsa española brevemente si hay algo realmente notable (máximo 20-25%).

4. **SOLO NOTICIAS FRESCAS Y SIN REPETIR**:
   - Utiliza exclusivamente noticias de las últimas 24-48 horas.
   - Cada noticia, cifra o empresa se analiza UNA SOLA VEZ con profundidad. Avanza siempre con ritmo.

5. **DURACIÓN Y EXTENSIÓN OBLIGATORIA (5 A 7 MINUTOS)**:
   - El guion DEBE tener una extensión de entre 900 y 1200 palabras para alcanzar los 5 a 6 minutos de emisión hablada.
   - Profundiza con contexto en cada noticia relevante para asegurar esa extensión y calidad de análisis.
   - CADA intervención DEBE comenzar obligatoriamente con la etiqueta `[ANA]:` o `[CARLOS]:` al principio de la línea.
   - Alterna intervenciones con frecuencia (cada 2-4 frases) para mantener dinamismo radiofónico.
   - Escribe los números y magnitudes para lectura fonética: "por ciento" en vez de "%", "dólares" o "euros" en vez de símbolos $, €, y números en palabras ("ciento siete dólares", "cinco coma dos").

6. **CIERRE COMPLETO Y REDONDO**:
   - El episodio debe terminar con un apunte analítico conclusivo completo de Carlos o Ana sobre la clave del mercado a vigilar en las próximas horas.
   - NUNCA dejes una frase a medias. Debe terminar en punto final rotundo.

NOTICIAS RECIENTES RECOPILADAS:
{news_content}
"""

def is_script_complete(script_text: str) -> tuple[bool, str]:
    cleaned = script_text.strip()
    words = cleaned.split()
    word_count = len(words)

    if word_count < 750:
        return False, f"Demasiado corto ({word_count} palabras, mínimo 750)."

    # Comprobar que termine en signo de puntuación de cierre
    if not re.search(r'[.!?]["\']?$', cleaned):
        return False, "La última frase quedó cortada sin punto final."

    # Comprobar que contenga intervenciones de ambos
    if "[ANA]:" not in cleaned or "[CARLOS]:" not in cleaned:
        return False, "Faltan etiquetas de los presentadores [ANA] o [CARLOS]."

    return True, "OK"

def generate_podcast_script(news_content: str, max_retries: int = 3) -> str:
    now, fecha_completa, hora, dia_semana = get_current_date_madrid()
    prompt = build_prompt(news_content, fecha_completa, hora, dia_semana)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.45,
            "maxOutputTokens": 8192
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    last_error = ""
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                if "error" in res_data:
                    last_error = f"Error Gemini API: {res_data['error']}"
                    continue

                candidates = res_data.get("candidates", [])
                if not candidates or "content" not in candidates[0]:
                    last_error = "Respuesta sin candidatos válidos de Gemini."
                    continue

                script_text = candidates[0]["content"]["parts"][0]["text"].strip()
                is_valid, reason = is_script_complete(script_text)

                if is_valid:
                    timestamp_str = now.strftime("%Y-%m-%d_%H-%M")
                    script_path = SCRIPTS_DIR / f"guion_{timestamp_str}.txt"
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(script_text)
                    return script_text
                else:
                    print(f"⚠️ Intento {attempt} descartado: {reason}. Reintentando...")
                    time.sleep(2)
        except Exception as e:
            last_error = str(e)
            time.sleep(2)

    raise RuntimeError(f"Fallo al generar guión válido tras {max_retries} intentos: {last_error}")
