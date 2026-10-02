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
    """Configura las 2 tareas en el Programador de Tareas de Windows con soporte completo para batería, despertar, recuperación y encendido (AtLogOn)"""
    task_morning = "PodcastFinanciero_Manana"
    task_evening = "PodcastFinanciero_Noche"
    bat_path = BASE_DIR / "run_podcast.bat"

    try:
        import win32api
        target_path = win32api.GetShortPathName(str(bat_path))
    except Exception:
        target_path = str(bat_path)

    cmd_morning = f'schtasks /create /tn "{task_morning}" /tr "{target_path}" /sc daily /st {SCHEDULE_MORNING} /f'
    cmd_evening = f'schtasks /create /tn "{task_evening}" /tr "{target_path}" /sc daily /st {SCHEDULE_EVENING} /f'

    subprocess.run(cmd_morning, shell=True, capture_output=True, text=True)
    subprocess.run(cmd_evening, shell=True, capture_output=True, text=True)

    # Añadir disparadores múltiples (Hora exacta + Al iniciar sesión) y ajustes de energía
    ps_script = f"""
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun -ExecutionTimeLimit (New-TimeSpan -Hours 1)
    $tMorning = @(
        (New-ScheduledTaskTrigger -Daily -At "{SCHEDULE_MORNING}"),
        (New-ScheduledTaskTrigger -AtLogOn)
    )
    $tEvening = @(
        (New-ScheduledTaskTrigger -Daily -At "{SCHEDULE_EVENING}"),
        (New-ScheduledTaskTrigger -AtLogOn)
    )
    Set-ScheduledTask -TaskName "{task_morning}" -Trigger $tMorning -Settings $settings | Out-Null
    Set-ScheduledTask -TaskName "{task_evening}" -Trigger $tEvening -Settings $settings | Out-Null
    """
    res_ps = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
    if res_ps.returncode == 0:
        print(f"✅ Tarea {task_morning} ({SCHEDULE_MORNING} + Al encender) configurada.")
        print(f"✅ Tarea {task_evening} ({SCHEDULE_EVENING} + Al encender) configurada.")
        return True
    else:
        print(f"⚠️ Aviso al aplicar ajustes avanzados: {res_ps.stderr}")
        return False

def uninstall_windows_tasks():
    subprocess.run('schtasks /delete /tn "PodcastFinanciero_Manana" /f', shell=True, capture_output=True)
    subprocess.run('schtasks /delete /tn "PodcastFinanciero_Noche" /f', shell=True, capture_output=True)
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
