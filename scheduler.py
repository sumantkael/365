import subprocess
import sys
import os
import winreg
from pathlib import Path

TASK_NAME = "DayDailyWallpaper"
REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_VALUE_NAME = "365DailyWallpaperUpdate"

# Windows flags to completely eliminate any flashing CMD/terminal popup
CREATE_NO_WINDOW = 0x08000000

def _run_hidden_subprocess(cmd: list[str]) -> subprocess.CompletedProcess:
    """Runs a Windows command completely silently without any black console blinking or popping up."""
    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        startupinfo=startupinfo,
        creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )

def is_user_admin() -> bool:
    """Checks whether the current process possesses administrative privileges."""
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def request_admin_elevation():
    """
    Relaunches the current script or executable with Administrator rights via UAC prompt once,
    if higher privileges are needed.
    """
    if is_user_admin():
        return True
    try:
        import ctypes
        if getattr(sys, "frozen", False):
            exe = sys.executable
            params = " ".join(f'"{a}"' for a in sys.argv[1:])
        else:
            exe = sys.executable
            params = " ".join(f'"{a}"' for a in sys.argv)

        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            exe,
            params,
            None,
            1 # SW_SHOWNORMAL
        )
        if ret > 32:
            sys.exit(0) # Exit the unelevated parent process
    except Exception as e:
        print(f"Elevation error: {e}")
    return False

def get_update_command() -> str:
    """Returns the properly quoted command string to run the headless update."""
    if getattr(sys, "frozen", False):
        exe = sys.executable
        return f'"{exe}" --update'
    else:
        # Running from Python source
        # Use pythonw.exe to prevent console flashing
        python_exe = Path(sys.executable)
        pythonw_exe = python_exe.parent / "pythonw.exe"
        runner = pythonw_exe if pythonw_exe.exists() else python_exe
        main_script = (Path(__file__).parent / "main.py").resolve()
        return f'"{runner}" "{main_script}" --update'

def is_task_scheduled() -> bool:
    """Checks if the DayDailyWallpaper task exists in Windows Task Scheduler or Registry Startup."""
    cmd = ["schtasks", "/query", "/tn", TASK_NAME]
    try:
        res = _run_hidden_subprocess(cmd)
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

def register_daily_task(target_executable: str = None, force: bool = False) -> bool:
    """
    Registers bulletproof daily updates using dual mechanisms silently:
    1. Windows Task Scheduler: Runs daily at 00:01 AM and on user logon.
    2. Windows HKCU Run Registry Key: Guarantees trigger whenever the user logs in or starts PC.
    """
    # If already scheduled and not forced, return immediately to avoid spawning schtasks
    if not force and is_task_scheduled():
        return True

    cmd_str = target_executable or get_update_command()
    success = False

    # 1. Register with Windows Task Scheduler (using hidden subprocess)
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
        res1 = _run_hidden_subprocess(cmd_daily)

        # Logon trigger (handles waking up or logging on when PC was turned off overnight)
        cmd_logon = [
            "schtasks", "/create",
            "/tn", f"{TASK_NAME}_Logon",
            "/tr", cmd_str,
            "/sc", "onlogon",
            "/f"
        ]
        res2 = _run_hidden_subprocess(cmd_logon)

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
    """Deletes scheduled tasks from Windows Task Scheduler and optionally from Registry Run without flashing windows."""
    try:
        _run_hidden_subprocess(["schtasks", "/delete", "/tn", TASK_NAME, "/f"])
        _run_hidden_subprocess(["schtasks", "/delete", "/tn", f"{TASK_NAME}_Logon", "/f"])
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
