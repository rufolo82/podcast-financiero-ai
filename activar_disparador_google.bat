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
echo 📋 PASOS PARA ACTUALIZAR (Solo 20 segundos):
echo 1. En la página web que se acaba de abrir, abre tu proyecto existente
echo    (o pulsa '+ Nuevo proyecto' si no lo ves).
echo 2. Pulsa Ctrl+A para seleccionar el código anterior y pulsa Ctrl+V para PEGAR.
echo 3. Pulsa el icono de Guardar (Ctrl+S).
echo 4. En el desplegable de arriba donde dice 'myFunction', selecciona:
echo    'configurarHorariosPuntuales'
echo 5. Pulsa el botón '▶ Ejecutar'.
echo    (Esto eliminará de inmediato el viejo horario de las 7 y activará las 8:00 y 20:00).
echo ==============================================================================
echo.
pause
