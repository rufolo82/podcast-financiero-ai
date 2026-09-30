import smtplib
from email.mime.text import MIMEText
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import (
    DESTINATION_EMAIL,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SENDER_NAME
)

def test_smtp_connection():
    print("=" * 50)
    print("📧 PRUEBA DE CONEXIÓN DE CORREO SMTP")
    print("=" * 50)
    print(f"Servidor:     {SMTP_HOST}:{SMTP_PORT}")
    print(f"Remitente:    {SMTP_USER or '(NO CONFIGURADO)'}")
    print(f"Destinatario: {DESTINATION_EMAIL}")
    print(f"Contraseña:   {'********' if SMTP_PASSWORD else '(NO CONFIGURADA)'}")
    print("-" * 50)

    if not SMTP_USER or not SMTP_PASSWORD:
        print("❌ Error: SMTP_USER o SMTP_PASSWORD están vacíos en el archivo .env.")
        print("Por favor, rellénalos y vuelve a ejecutar este test.")
        return

    print("Conectando con el servidor de correo...")
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
        server.ehlo()
        server.starttls()
        server.ehlo()
        print("Autenticando credenciales...")
        server.login(SMTP_USER, SMTP_PASSWORD)

        msg = MIMEText("¡Hola! Esta es una prueba de verificación. Tu configuración de correo para el Podcast Financiero funciona correctamente.", "plain", "utf-8")
        msg['Subject'] = "✅ Prueba de conexión - Podcast Financiero AI"
        msg['From'] = f"{SENDER_NAME} <{SMTP_USER}>"
        msg['To'] = DESTINATION_EMAIL

        print(f"Enviando correo de prueba a {DESTINATION_EMAIL}...")
        server.sendmail(SMTP_USER, [DESTINATION_EMAIL], msg.as_string())
        server.quit()
        print("\n🎉 ¡ÉXITO! Correo de prueba enviado correctamente.")
        print(f"Revisa tu bandeja de entrada en {DESTINATION_EMAIL}.")
    except Exception as e:
        print(f"\n❌ Fallo en la conexión SMTP: {e}")

if __name__ == "__main__":
    test_smtp_connection()
