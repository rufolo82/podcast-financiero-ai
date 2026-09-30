# 🎙️ Podcast Financiero Automatizado (Google Studio AI)

Sistema profesional en Python para generar y enviar podcasts financieros diarios con voces hiperrealistas de **Google Cloud TTS (Studio Voices)** y análisis impulsado por **Gemini 2.5 Flash**.

---

## 🚀 Principales Mejoras frente al script anterior de Google Apps Script

| Característica | Script anterior (Google Apps Script) | Nueva Versión Local (Python + Neural2) |
|---|---|---|
| **Calidad y Coste de Voces** | `es-ES-Standard-A` y `B` (voces robóticas antiguas, baja frecuencia) | **`es-ES-Neural2-A` y `es-ES-Neural2-F`** (Redes neuronales profundas de Google, **100% GRATIS** hasta 1.000.000 caracteres/mes) |
| **Fuentes RSS** | Regex básico quitando HTML sobre XML crudo, sin fechas | **Parser RSS inteligente** que extrae titular, fecha exacta, resumen y filtra noticias frescas (< 48h) |
| **Reglas de Mercado** | Mezcla no balanceada | **75% Internacional** (Wall Street, Fed, BCE, tipos) + **25% Nacional** (IBEX 35), sin introducciones vacías |
| **Límites de Ejecución** | Máximo 6 minutos en Google Apps Script (riesgo de timeout y caída) | **Sin límites**: corre de forma local y estable |
| **Entrega** | Enlace a Drive con permisos | **Audio MP3 adjunto directamente al correo** para escucharlo en un clic desde el móvil o PC |
| **Programación** | Triggers de Google Apps Script (imprecisos, ventanas de 1h) | **Programador de Tareas nativo de Windows**: exactamente a las **08:00** y a las **21:00** |

---

## 📁 Estructura del Proyecto

```text
Podcast Financiero/
├── .env                  # Claves API (Gemini, Google Cloud TTS) y configuración SMTP
├── .env.example          # Plantilla de configuración
├── config.py             # Carga y validación de variables de entorno
├── sources.json          # Fuentes financieras RSS configuradas
├── rss_fetcher.py        # Descarga, filtrado de frescura y estructuración de noticias
├── script_generator.py   # Generación del guión conversacional con Gemini 2.5 Flash
├── tts_synthesizer.py    # Síntesis con Google Studio Voices y ensamblado en MP3
├── email_notifier.py     # Envío de email con el guión formateado y el MP3 adjunto
├── scheduler.py          # Automatizador para Windows (08:00 y 21:00)
├── main.py               # Punto de entrada CLI
├── run_podcast.bat       # Lanzador automático para Windows Task Scheduler
├── podcasts/             # Archivos MP3 generados
└── scripts/              # Historial de guiones generados
```

---

## ⚡ Comandos Rápidos

Abre la terminal en esta carpeta y ejecuta:

### 1. Ejecutar el flujo completo ahora mismo
```powershell
python main.py --run
```
*(Recolecta noticias, redacta el guión con Gemini, sintetiza el audio con Google Studio y procesa el correo)*.

### 2. Probar las voces Google Studio de Ana y Carlos
```powershell
python main.py --test-tts
```

### 3. Probar la descarga de fuentes RSS
```powershell
python main.py --test-rss
```

### 4. Configurar la ejecución automática a las 08:00 y 21:00
```powershell
python main.py --schedule-install
```
*(Crea automáticamente las 2 tareas en el Programador de Tareas de Windows)*.

---

## 📧 Configuración del Envío de Correo (SMTP)

En el archivo `.env`, completa los datos de tu servidor de correo emisor:

```ini
DESTINATION_EMAIL=rlm_1982@hotmail.com

# Para usar una cuenta de Gmail emisora:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_cuenta@gmail.com
SMTP_PASSWORD=tu_contraseña_de_aplicacion_de_16_caracteres
SENDER_NAME=Podcast Financiero AI
```

> **Nota para Gmail**: Para obtener la contraseña de aplicación, entra en tu cuenta de Google -> *Seguridad* -> *Verificación en dos pasos* -> *Contraseñas de aplicaciones* y genera una para este script.
