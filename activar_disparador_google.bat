@echo off
chcp 65001 >nul
echo ==============================================================================
echo 🚀 COPIANDO CÓDIGO DEL DISPARADOR Y ABRIENDO GOOGLE APPS SCRIPT
echo ==============================================================================
echo.
powershell -NoProfile -Command "Get-Content -Raw '%~dp0disparador_google_apps_script.js' | Set-Clipboard"
echo ✅ ¡Código copiado automáticamente al portapapeles!
echo.
echo Abriendo Google Apps Script en tu navegador...
start https://script.google.com/home/start
echo.
echo ==============================================================================
echo 📋 PASOS (Solo te llevará 30 segundos):
echo 1. En la página web que se acaba de abrir, pulsa arriba a la izquierda en:
echo    '+ Nuevo proyecto'
echo 2. Pulsa Ctrl+A para seleccionar el código vacío y luego Ctrl+V para PEGAR el código.
echo 3. Pulsa el icono del Disquete (Guardar) o Ctrl+S.
echo 4. En el desplegable de arriba donde dice 'myFunction', selecciona:
echo    'configurarHorariosPuntuales'
echo 5. Pulsa el botón '▶ Ejecutar'.
echo    (Si te pide Revisar permisos, pulsa tu cuenta rlm1982@gmail.com -> Opciones avanzadas -> Ir a (no seguro) -> Permitir).
echo ==============================================================================
echo.
pause
