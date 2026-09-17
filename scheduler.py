import subprocess
import sys
import os
import winreg
from pathlib import Path

TASK_NAME = "DayDailyWallpaper"
REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_VALUE_NAME = "365DailyWallpaperUpdate"

def get_update_command() -> str:
    """Returns the properly quoted command string to run the headless update."""
    if getattr(sys, "frozen", False):
        exe = sys.executable
        return f'"{exe}" --update'
    else:
        # Running from Python source
        # Try using pythonw.exe to prevent any console window flashing
        python_exe = Path(sys.executable)
        pythonw_exe = python_exe.parent / "pythonw.exe"
        runner = pythonw_exe if pythonw_exe.exists() else python_exe
        main_script = (Path(__file__).parent / "main.py").resolve()
        return f'"{runner}" "{main_script}" --update'

def is_task_scheduled() -> bool:
    """Checks if the DayDailyWallpaper task exists in Windows Task Scheduler or Registry Startup."""
    cmd = ["schtasks", "/query", "/tn", TASK_NAME]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            return True
    except Exception:
        pass

    # Also check Registry Run key
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, REG_VALUE_NAME)
            return True
    except Exception:
        pass

    return False

def register_daily_task(target_executable: str = None) -> bool:
    """
    Registers bulletproof daily updates using dual mechanisms:
    1. Windows Task Scheduler: Runs daily at 00:01 AM and on user logon.
    2. Windows HKCU Run Registry Key: Guarantees trigger whenever the user logs in or starts PC.
    """
    cmd_str = target_executable or get_update_command()
    success = False

    # 1. Register with Windows Task Scheduler
    try:
        unregister_daily_task(clean_registry=False)

        # Daily midnight trigger
        cmd_daily = [
            "schtasks", "/create",
            "/tn", TASK_NAME,
            "/tr", cmd_str,
            "/sc", "daily",
            "/st", "00:01",
            "/f"
        ]
        res1 = subprocess.run(cmd_daily, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Logon trigger (handles waking up or logging on when PC was turned off overnight)
        cmd_logon = [
            "schtasks", "/create",
            "/tn", f"{TASK_NAME}_Logon",
            "/tr", cmd_str,
            "/sc", "onlogon",
            "/f"
        ]
        res2 = subprocess.run(cmd_logon, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if res1.returncode == 0 or res2.returncode == 0:
            success = True
    except Exception as e:
        print(f"Schtasks registration notice: {e}")

    # 2. Register with HKCU Run (Guaranteed user-level startup trigger without admin rights)
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, REG_VALUE_NAME, 0, winreg.REG_SZ, cmd_str)
            success = True
    except Exception as e:
        print(f"Registry startup registration notice: {e}")

    return success

def unregister_daily_task(clean_registry: bool = True) -> bool:
    """Deletes scheduled tasks from Windows Task Scheduler and optionally from Registry Run."""
    try:
        subprocess.run(["schtasks", "/delete", "/tn", TASK_NAME, "/f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["schtasks", "/delete", "/tn", f"{TASK_NAME}_Logon", "/f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        pass

    if clean_registry:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, REG_VALUE_NAME)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Registry unregister error: {e}")

    return True
