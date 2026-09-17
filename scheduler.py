import subprocess
import sys
from pathlib import Path

TASK_NAME = "DayDailyWallpaper"

def is_task_scheduled() -> bool:
    """Checks if the DayDailyWallpaper task exists in Windows Task Scheduler."""
    cmd = ["schtasks", "/query", "/tn", TASK_NAME]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.returncode == 0
    except Exception:
        return False

def register_daily_task(target_executable: str = None) -> bool:
    """
    Registers a scheduled task that executes daily at 00:01 AM and on user logon.
    If target_executable is not given, determines the current executable or python script.
    """
    if not target_executable:
        if getattr(sys, "frozen", False):
            # Running as compiled PyInstaller exe
            target_executable = f'"{sys.executable}" --update'
        else:
            # Running as python script
            main_script = Path(__file__).parent / "main.py"
            # Use pythonw if possible to avoid console popup
            python_exe = sys.executable
            target_executable = f'"{python_exe}" "{main_script.resolve()}" --update'

    # Unregister any existing one first
    unregister_daily_task()

    # Create daily schedule at 00:01 AM
    cmd_daily = [
        "schtasks", "/create",
        "/tn", TASK_NAME,
        "/tr", target_executable,
        "/sc", "daily",
        "/st", "00:01",
        "/f"
    ]
    
    # Also create a logon trigger so if PC was sleeping or off at 00:01, it updates on login
    cmd_logon = [
        "schtasks", "/create",
        "/tn", f"{TASK_NAME}_Logon",
        "/tr", target_executable,
        "/sc", "onlogon",
        "/f"
    ]
    try:
        res1 = subprocess.run(cmd_daily, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        res2 = subprocess.run(cmd_logon, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res1.returncode == 0
    except Exception as e:
        print(f"Failed to register task: {e}")
        return False

def unregister_daily_task() -> bool:
    """Deletes the scheduled tasks from Windows Task Scheduler."""
    subprocess.run(["schtasks", "/delete", "/tn", TASK_NAME, "/f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["schtasks", "/delete", "/tn", f"{TASK_NAME}_Logon", "/f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return True
