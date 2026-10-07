import base64
import json
import re
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import pytz
from config import (
    TTS_API_KEY,
    VOICE_ANA,
    VOICE_CARLOS,
    TTS_SPEAKING_RATE,
    OUTPUT_DIR
)

TTS_URL = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={TTS_API_KEY}"

def sanitize_text_for_speech(text: str) -> str:
    cleaned = text
    # Quitar marcas de formato markdown
    cleaned = re.sub(r'#{1,6}\s*', '', cleaned)
    cleaned = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', cleaned)
    cleaned = re.sub(r'`[^`]+`', '', cleaned)
    cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
    # Símbolos financieros a palabras
    cleaned = re.sub(r'(\d+)%', r'\1 por ciento', cleaned)
    cleaned = re.sub(r'%\b', ' por ciento', cleaned)
    cleaned = re.sub(r'\$(\d+([.,]\d+)?)', r'\1 dólares', cleaned)
    cleaned = re.sub(r'€(\d+([.,]\d+)?)', r'\1 euros', cleaned)
    cleaned = re.sub(r'(\d+([.,]\d+)?)\s*€', r'\1 euros', cleaned)
    cleaned = re.sub(r'(\d+([.,]\d+)?)\s*\$', r'\1 dólares', cleaned)
    # Quitar emojis y caracteres extraños
    cleaned = re.sub(r'[\U00010000-\U0010ffff]', '', cleaned)
    cleaned = re.sub(r'[-–—]{2,}', ', ', cleaned)
    # Normalizar espacios
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def parse_dialogue_turns(script_text: str) -> List[Dict[str, str]]:
    pattern = r'\[(ANA|CARLOS)\]:\s*'
    lines = script_text.split('\n')
    turns = []
    current_speaker = "ANA"
    current_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            if current_lines:
                text_block = sanitize_text_for_speech(" ".join(current_lines))
                if text_block:
                    turns.append({"speaker": current_speaker, "text": text_block})
                current_lines = []
            current_speaker = match.group(1).upper()
            remaining = line[match.end():].strip()
            if remaining:
                current_lines.append(remaining)
        else:
            current_lines.append(line)

    if current_lines:
        text_block = sanitize_text_for_speech(" ".join(current_lines))
        if text_block:
            turns.append({"speaker": current_speaker, "text": text_block})

    # Subdividir turnos que excedan 3000 caracteres (margen de seguridad para TTS)
    final_turns = []
    for turn in turns:
        t = turn["text"]
        sp = turn["speaker"]
        if len(t) <= 3000:
            final_turns.append(turn)
        else:
            # Dividir por oraciones
            sentences = re.split(r'(?<=[.!?])\s+', t)
            chunk = []
            curr_len = 0
            for s in sentences:
                if curr_len + len(s) > 2800 and chunk:
                    final_turns.append({"speaker": sp, "text": " ".join(chunk)})
                    chunk = [s]
                    curr_len = len(s)
                else:
                    chunk.append(s)
                    curr_len += len(s) + 1
            if chunk:
                final_turns.append({"speaker": sp, "text": " ".join(chunk)})

    return final_turns

def synthesize_turn(text: str, voice_name: str, fallback_voice: str | None = None) -> bytes:
    payload = {
        "input": {"text": text},
        "voice": {
            "languageCode": "es-ES",
            "name": voice_name
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": TTS_SPEAKING_RATE,
            "pitch": 0.0,
            "volumeGainDb": 0.0
        }
    }

    req = urllib.request.Request(
        TTS_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return base64.b64decode(data["audioContent"])
    except urllib.error.HTTPError as e:
        if fallback_voice and fallback_voice != voice_name:
            # Reintentar con voz alternativa
            payload["voice"]["name"] = fallback_voice
            req2 = urllib.request.Request(
                TTS_URL,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
            with urllib.request.urlopen(req2, timeout=20) as resp2:
                data2 = json.loads(resp2.read().decode("utf-8"))
                return base64.b64decode(data2["audioContent"])
        raise RuntimeError(f"Error sintetizando con {voice_name}: {e}")

def create_podcast_audio(script_text: str) -> Tuple[Path, int]:
    madrid_tz = pytz.timezone("Europe/Madrid")
    now = datetime.now(madrid_tz)
    timestamp = now.strftime("%Y-%m-%d_%H-%M")
    output_file = OUTPUT_DIR / f"Podcast_Financiero_{timestamp}.mp3"

    turns = parse_dialogue_turns(script_text)
    if not turns:
        raise ValueError("No se encontraron turnos de diálogo válidos en el guion.")

    audio_chunks: List[bytes] = []

    for idx, turn in enumerate(turns):
        speaker = turn["speaker"]
        text = turn["text"]
        
        if speaker == "CARLOS":
            voice = VOICE_CARLOS
            fallback = "es-ES-Neural2-F"
        else:
            voice = VOICE_ANA
            fallback = "es-ES-Neural2-A"

        audio_bytes = synthesize_turn(text, voice, fallback)
        audio_chunks.append(audio_bytes)
        time.sleep(0.15)  # Breve pausa para no saturar cuota por segundo

    # Concatenar todos los fragmentos MP3
    with open(output_file, "wb") as f_out:
        for chunk in audio_chunks:
            f_out.write(chunk)

    total_bytes = output_file.stat().st_size
    return output_file, total_bytes
