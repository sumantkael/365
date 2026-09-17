import ctypes
import os
from pathlib import Path
from settings import get_app_dir

SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

def get_screen_resolution() -> tuple[int, int]:
    """Gets the primary screen resolution using Windows API."""
    try:
        # Enable DPI awareness to get actual native pixels instead of scaled resolution
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    try:
        width = ctypes.windll.user32.GetSystemMetrics(0) # SM_CXSCREEN
        height = ctypes.windll.user32.GetSystemMetrics(1) # SM_CYSCREEN
        if width > 0 and height > 0:
            return (width, height)
    except Exception as e:
        print(f"Error querying screen resolution: {e}")

    # Fallback to standard Full HD if unavailable
    return (1920, 1080)

def get_wallpaper_cache_path() -> Path:
    """Returns absolute path where generated wallpaper image is saved."""
    return get_app_dir() / "current_wallpaper.png"

import winreg

def set_desktop_wallpaper(image_path: str | Path) -> bool:
    """Applies the image at image_path as the Windows desktop wallpaper."""
    abs_path = str(Path(image_path).resolve())
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Wallpaper image not found at {abs_path}")

    # Ensure Windows desktop style is set to Fill/Fit (WallpaperStyle="10" or "6", TileWallpaper="0")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "10") # 10 = Fill
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key)
    except Exception:
        pass

    # SystemParametersInfoW takes unicode string
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        abs_path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    return bool(result)
