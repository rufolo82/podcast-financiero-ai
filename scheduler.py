import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
import pytz
from config import SCHEDULE_MORNING, SCHEDULE_EVENING

BASE_DIR = Path(__file__).resolve().parent
PYTHON_EXE = sys.executable
MAIN_SCRIPT = BASE_DIR / "main.py"

def install_windows_tasks() -> bool:
    """Configura las 2 tareas en el Programador de Tareas de Windows + auto-arranque al encender el PC"""
    task_morning = "PodcastFinanciero_Manana"
    task_evening = "PodcastFinanciero_Noche"
    bat_path = BASE_DIR / "run_podcast.bat"

    try:
        import win32api
        target_path = win32api.GetShortPathName(str(bat_path))
    except Exception:
        target_path = str(bat_path)

    # 1. Tareas programadas a las 08:00 y 21:00 con repetición cada 30 min durante 2 horas por si el equipo estaba suspendido
    cmd_morning = f'schtasks /create /tn "{task_morning}" /tr "{target_path}" /sc daily /st {SCHEDULE_MORNING} /ri 30 /du 02:00 /f'
    cmd_evening = f'schtasks /create /tn "{task_evening}" /tr "{target_path}" /sc daily /st {SCHEDULE_EVENING} /ri 30 /du 02:00 /f'

    subprocess.run(cmd_morning, shell=True, capture_output=True, text=True)
    subprocess.run(cmd_evening, shell=True, capture_output=True, text=True)

    # 2. Desbloquear modo batería y despertar en PowerShell
    ps_script = f"""
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun -ExecutionTimeLimit (New-TimeSpan -Hours 1)
    Set-ScheduledTask -TaskName "{task_morning}" -Settings $settings | Out-Null
    Set-ScheduledTask -TaskName "{task_evening}" -Settings $settings | Out-Null
    """
    res_ps = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)

    # 3. Crear lanzador silencioso en la carpeta de Inicio de Windows (Startup) por si se enciende el PC dentro de la ventana
    appdata = os.getenv("APPDATA", "")
    if appdata:
        startup_dir = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if startup_dir.exists():
            vbs_file = startup_dir / "PodcastFinanciero_AutoCheck.vbs"
            vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\nWshShell.Run """{target_path}""", 0, False\n'
            with open(vbs_file, "w", encoding="utf-8") as f:
                f.write(vbs_content)

    if res_ps.returncode == 0:
        print(f"✅ Tarea {task_morning} ({SCHEDULE_MORNING} + reintento cada 30m) configurada.")
        print(f"✅ Tarea {task_evening} ({SCHEDULE_EVENING} + reintento cada 30m) configurada.")
        print("✅ Auto-comprobación invisible al encender Windows configurada.")
        return True
    else:
        print(f"⚠️ Aviso al aplicar ajustes avanzados: {res_ps.stderr}")
        return False

def uninstall_windows_tasks():
    subprocess.run('schtasks /delete /tn "PodcastFinanciero_Manana" /f', shell=True, capture_output=True)
    subprocess.run('schtasks /delete /tn "PodcastFinanciero_Noche" /f', shell=True, capture_output=True)
    appdata = os.getenv("APPDATA", "")
    if appdata:
        vbs_file = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "PodcastFinanciero_AutoCheck.vbs"
        if vbs_file.exists():
            vbs_file.unlink()
    print("Tareas de Windows eliminadas.")

def run_loop_scheduler(job_callback):
    """Ejecuta un bucle continuo comprobando la hora en zona Europe/Madrid"""
    print(f"Iniciando scheduler en bucle. Horarios configurados: {SCHEDULE_MORNING} y {SCHEDULE_EVENING} (Madrid)...")
    executed_today = set()
    madrid_tz = pytz.timezone("Europe/Madrid")

    while True:
        now = datetime.now(madrid_tz)
        current_time_str = now.strftime("%H:%M")
        current_date_str = now.strftime("%Y-%m-%d")

        key_morning = f"{current_date_str}_{SCHEDULE_MORNING}"
        key_evening = f"{current_date_str}_{SCHEDULE_EVENING}"

        if current_time_str == SCHEDULE_MORNING and key_morning not in executed_today:
            print(f"\n[HORA PROGRAMADA: {SCHEDULE_MORNING}] Iniciando podcast matutino...")
            job_callback()
            executed_today.add(key_morning)

        elif current_time_str == SCHEDULE_EVENING and key_evening not in executed_today:
            print(f"\n[HORA PROGRAMADA: {SCHEDULE_EVENING}] Iniciando podcast nocturno...")
            job_callback()
            executed_today.add(key_evening)

        if len(executed_today) > 10:
            executed_today = {k for k in executed_today if k.startswith(current_date_str)}

        time.sleep(25)
