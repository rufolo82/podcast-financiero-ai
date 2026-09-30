import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
import pytz
from config import (
    DESTINATION_EMAIL,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SENDER_NAME
)

def send_podcast_email(mp3_path: Path, script_text: str) -> bool:
    madrid_tz = pytz.timezone("Europe/Madrid")
    now = datetime.now(madrid_tz)
    date_str = now.strftime("%d/%m/%Y a las %H:%M")
    subject = f"📈 Tu Podcast Financiero está listo - {date_str}"

    if not SMTP_USER or not SMTP_PASSWORD:
        print("\n⚠️ AVISO DE CORREO:")
        print(f"El podcast ha sido generado con éxito en: {mp3_path}")
        print("Para recibirlo automáticamente en tu bandeja de entrada:")
        print("Configura SMTP_USER y SMTP_PASSWORD en el archivo .env")
        print(f"Destino configurado: {DESTINATION_EMAIL}\n")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg['To'] = DESTINATION_EMAIL
    msg['Subject'] = subject

    # Formatear el guion para HTML con estilo elegante
    formatted_script_html = script_text.replace("\n", "<br>")
    formatted_script_html = formatted_script_html.replace(
        "[ANA]:", "<br><b style='color: #1a73e8;'>[ANA]:</b>"
    ).replace(
        "[CARLOS]:", "<br><b style='color: #e37400;'>[CARLOS]:</b>"
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #202124;">
        <div style="max-width: 650px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
          <h2 style="color: #1a73e8; margin-top: 0;">🎧 Episodio Diario de Noticias Financieras</h2>
          <p><b>Fecha de emisión:</b> {date_str} (horario de Madrid)</p>
          <p>Tu podcast de audio MP3 de alta fidelidad está <b>adjunto directamente a este correo</b> para que lo escuches al instante.</p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
          <h3 style="color: #333;">📜 Guion Completo:</h3>
          <div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px; font-size: 14px;">
            {formatted_script_html}
          </div>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
          <p style="font-size: 12px; color: #777;">Generado automáticamente por tu Podcast Financiero Workflow con voces Google Studio.</p>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(body_html, 'html'))

    # Adjuntar MP3 si existe y su tamaño es razonable para email (< 25MB)
    if mp3_path.exists():
        part = MIMEBase('audio', 'mpeg')
        with open(mp3_path, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{mp3_path.name}"')
        msg.attach(part)

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [DESTINATION_EMAIL], msg.as_string())
        server.quit()
        print(f"✅ Email enviado con éxito a {DESTINATION_EMAIL} con el MP3 adjunto.")
        return True
    except Exception as e:
        print(f"❌ Error al enviar email vía SMTP: {e}")
        return False
