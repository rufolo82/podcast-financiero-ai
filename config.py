import os
import json
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TTS_API_KEY = os.getenv("TTS_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

VOICE_ANA = os.getenv("VOICE_ANA", "es-ES-Neural2-A")
VOICE_CARLOS = os.getenv("VOICE_CARLOS", "es-ES-Neural2-F")
TTS_SPEAKING_RATE = float(os.getenv("TTS_SPEAKING_RATE", "1.05"))

DESTINATION_EMAIL = os.getenv("DESTINATION_EMAIL", "rlm_1982@hotmail.com")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "Podcast Financiero AI")

SCHEDULE_MORNING = os.getenv("SCHEDULE_MORNING", "08:00")
SCHEDULE_EVENING = os.getenv("SCHEDULE_EVENING", "21:00")

OUTPUT_DIR = BASE_DIR / "podcasts"
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUT_DIR.mkdir(exist_ok=True)
SCRIPTS_DIR.mkdir(exist_ok=True)

SOURCES_FILE = BASE_DIR / "sources.json"

def load_sources():
    if SOURCES_FILE.exists():
        with open(SOURCES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
