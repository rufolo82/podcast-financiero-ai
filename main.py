import argparse
import sys
from datetime import datetime
import pytz

# Asegurar codificación utf-8 en consola de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import (
    GEMINI_API_KEY,
    TTS_API_KEY,
    VOICE_ANA,
    VOICE_CARLOS,
    OUTPUT_DIR,
    DESTINATION_EMAIL
)
from rss_fetcher import collect_all_news, format_articles_for_prompt
from script_generator import generate_podcast_script
from tts_synthesizer import create_podcast_audio, synthesize_turn
from email_notifier import send_podcast_email
from scheduler import install_windows_tasks, run_loop_scheduler

def run_workflow():
    print("=" * 60)
    print("🚀 INICIANDO WORKFLOW DE PODCAST FINANCIERO")
    madrid_tz = pytz.timezone("Europe/Madrid")
    now = datetime.now(madrid_tz)
    print(f"⏰ Fecha y hora (Madrid): {now.strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

    # 1. Recolección de noticias
    print("\n📡 1/4. Recopilando noticias financieras frescas (últimas 24-48h)...")
    articles = collect_all_news(max_age_hours=48)
    if not articles:
        print("⚠️ No se encontraron noticias recientes en las fuentes.")
        return

    print(f"✅ Se obtuvieron {len(articles)} artículos únicos y recientes.")
    formatted_content = format_articles_for_prompt(articles)

    # 2. Generación del guión con Gemini
    print("\n🧠 2/4. Generando guion conversacional dinámico con Gemini AI...")
    try:
        script = generate_podcast_script(formatted_content)
        word_count = len(script.split())
        print(f"✅ Guion creado exitosamente (~{word_count} palabras).")
    except Exception as e:
        print(f"❌ Error generando guion: {e}")
        return

    # 3. Síntesis de voz con Google Studio Voices
    print(f"\n🎙️ 3/4. Sintetizando audio con Google Studio Voices:")
    print(f"   • Ana:    {VOICE_ANA} (Estudio)")
    print(f"   • Carlos: {VOICE_CARLOS} (Estudio)")
    try:
        mp3_path, file_size = create_podcast_audio(script)
        size_mb = file_size / (1024 * 1024)
        print(f"✅ MP3 generado con éxito: {mp3_path.name} ({size_mb:.2f} MB)")
        print(f"📁 Guardado en: {mp3_path}")
    except Exception as e:
        print(f"❌ Error generando audio TTS: {e}")
        return

    # 4. Envío por correo
    print(f"\n📧 4/4. Procesando notificación por correo para {DESTINATION_EMAIL}...")
    send_podcast_email(mp3_path, script)

    print("\n🎉 WORKFLOW COMPLETADO EXITOSAMENTE.")
    print("=" * 60)

def test_tts_voices():
    print("🎙️ Probando síntesis rápida con las mejores voces de Google...")
    sample_ana = "Hola, soy Ana. Bienvenidos a este análisis de los mercados financieros internacionales."
    sample_carlos = "Y yo soy Carlos. Hoy Wall Street y el Banco Central Europeo concentran la atención de los inversores."

    ana_audio = synthesize_turn(sample_ana, VOICE_ANA)
    carlos_audio = synthesize_turn(sample_carlos, VOICE_CARLOS)

    test_file = OUTPUT_DIR / "test_voces_estudio.mp3"
    with open(test_file, "wb") as f:
        f.write(ana_audio)
        f.write(carlos_audio)

    print(f"✅ Audio de prueba generado exitosamente: {test_file}")
    print(f"   Voz Ana: {VOICE_ANA}")
    print(f"   Voz Carlos: {VOICE_CARLOS}")

def test_rss():
    print("📡 Probando descarga de fuentes RSS...")
    news = collect_all_news(max_age_hours=48)
    print(f"Total noticias encontradas: {len(news)}")
    for i, a in enumerate(news[:10], 1):
        print(f"{i}. [{a['source']}] {a['title']}")

def main():
    parser = argparse.ArgumentParser(description="Workflow de Podcast Financiero Automatizado")
    parser.add_argument("--run", action="store_true", help="Ejecutar el workflow completo ahora")
    parser.add_argument("--test-tts", action="store_true", help="Probar las voces de Google Studio")
    parser.add_argument("--test-rss", action="store_true", help="Probar recolección de noticias RSS")
    parser.add_argument("--schedule-install", action="store_true", help="Instalar tareas automáticas a las 08:00 y 21:00 en Windows")
    parser.add_argument("--schedule-run", action="store_true", help="Ejecutar el planificador continuo en primer plano")
    parser.add_argument("--sync-cloud", action="store_true", help="Sincronizar código y configuración con GitHub Actions en la nube")

    args = parser.parse_args()

    if args.test_tts:
        test_tts_voices()
    elif args.test_rss:
        test_rss()
    elif args.schedule_install:
        install_windows_tasks()
    elif args.schedule_run:
        run_loop_scheduler(run_workflow)
    elif args.sync_cloud:
        from cloud_deployer import deploy_to_github_cloud
        deploy_to_github_cloud()
    else:
        # Por defecto si no se pasa argumento o se pasa --run
        run_workflow()

if __name__ == "__main__":
    main()
