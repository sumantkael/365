import sys
import os
from pathlib import Path
import ctypes
from ctypes import wintypes
from PIL import Image

# Import project modules
from settings import SettingsManager
from date_calculator import get_date_stats, parse_user_date
from wallpaper_generator import render_wallpaper

def capture_tkinter_window(root, output_path: Path):
    root.update()
    root.update_idletasks()
    
    hwnd = root.winfo_id()
    # Get client/window rect
    w = max(10, root.winfo_width())
    h = max(10, root.winfo_height())
    
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    
    hdc_screen = user32.GetDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
    hbmp = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
    gdi32.SelectObject(hdc_mem, hbmp)
    
    # PW_RENDERFULLCONTENT = 2
    user32.PrintWindow(hwnd, hdc_mem, 2)
    
    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ('biSize', wintypes.DWORD),
            ('biWidth', wintypes.LONG),
            ('biHeight', wintypes.LONG),
            ('biPlanes', wintypes.WORD),
            ('biBitCount', wintypes.WORD),
            ('biCompression', wintypes.DWORD),
            ('biSizeImage', wintypes.DWORD),
            ('biXPelsPerMeter', wintypes.LONG),
            ('biYPelsPerMeter', wintypes.LONG),
            ('biClrUsed', wintypes.DWORD),
            ('biClrImportant', wintypes.DWORD)
        ]

    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth = w
    bmi.biHeight = -h  # top-down
    bmi.biPlanes = 1
    bmi.biBitCount = 32
    bmi.biCompression = 0

    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(hdc_mem, hbmp, 0, h, buf, ctypes.byref(bmi), 0)

    img = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1).convert('RGB')
    img.save(str(output_path), 'PNG')
    print(f"Captured window: {output_path} ({w}x{h})")

    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(hwnd, hdc_screen)

def generate_app_screenshots(output_dir: Path):
    import time
    from ui import DaySettingsApp, DatePickerModal
    from datetime import date
    
    # 1. Dark Mode App
    sm = SettingsManager()
    sm.set("theme", "dark")
    sm.set("mode", "dots")
    sm.set("show_dots", True)
    sm.set("show_text", True)
    
    app_dark = DaySettingsApp()
    app_dark.lift()
    app_dark.attributes("-topmost", True)
    for _ in range(10):
        app_dark.update()
        app_dark.update_idletasks()
        time.sleep(0.04)
        
    capture_tkinter_window(app_dark, output_dir / "screenshot_app_dark.png")
    app_dark.destroy()

    # 2. Light Mode App
    sm.set("theme", "light")
    sm.set("mode", "both")
    sm.set("show_dots", False)
    sm.set("show_text", True)
    
    app_light = DaySettingsApp()
    app_light.lift()
    app_light.attributes("-topmost", True)
    for _ in range(10):
        app_light.update()
        app_light.update_idletasks()
        time.sleep(0.04)
        
    capture_tkinter_window(app_light, output_dir / "screenshot_app_light.png")
    
    # 3. DatePicker Modal Capture
    modal = DatePickerModal(app_light, initial_date=date(2027, 1, 21), theme_name="light")
    modal.lift()
    modal.attributes("-topmost", True)
    for _ in range(10):
        app_light.update()
        modal.update()
        time.sleep(0.04)
    capture_tkinter_window(modal, output_dir / "screenshot_datepicker_light.png")
    modal.destroy()
    app_light.destroy()

def generate_wallpaper_renders(output_dir: Path):
    stats_year = get_date_stats()
    res = (1920, 1080)
    
    # 1. Dark Dots Matrix
    img_dark_dots = render_wallpaper(
        stats=stats_year,
        resolution=res,
        mode="dots",
        theme="dark",
        show_text=True,
        show_dots=True,
        show_percentage=True,
        wallpaper_font="geist",
        fast_preview=False
    )
    img_dark_dots.save(output_dir / "wallpaper_dark_dots.png", "PNG")
    print(f"Generated: wallpaper_dark_dots.png")

    # 2. Light Dots Matrix
    img_light_dots = render_wallpaper(
        stats=stats_year,
        resolution=res,
        mode="dots",
        theme="light",
        show_text=True,
        show_dots=True,
        show_percentage=True,
        wallpaper_font="geist",
        fast_preview=False
    )
    img_light_dots.save(output_dir / "wallpaper_light_dots.png", "PNG")
    print(f"Generated: wallpaper_light_dots.png")

    # 3. Dark 'Both' Mode (Editorial Serif)
    img_dark_both = render_wallpaper(
        stats=stats_year,
        resolution=res,
        mode="both",
        theme="dark",
        show_text=True,
        show_dots=False,
        show_percentage=True,
        wallpaper_font="instrument_serif",
        fast_preview=False
    )
    img_dark_both.save(output_dir / "wallpaper_dark_editorial.png", "PNG")
    print(f"Generated: wallpaper_dark_editorial.png")

    # 4. Light Custom Countdown
    from datetime import date, timedelta
    custom_target = date.today() + timedelta(days=120)
    stats_custom = get_date_stats(
        date_mode="custom",
        custom_target_date=custom_target,
        custom_start_date=date.today() - timedelta(days=60),
        event_title="Product Launch"
    )
    img_light_custom = render_wallpaper(
        stats=stats_custom,
        resolution=res,
        mode="dots",
        theme="light",
        show_text=True,
        show_dots=True,
        show_percentage=True,
        wallpaper_font="geist",
        fast_preview=False
    )
    img_light_custom.save(output_dir / "wallpaper_light_countdown.png", "PNG")
    print(f"Generated: wallpaper_light_countdown.png")

if __name__ == "__main__":
    out = Path(__file__).parent / "screenshots"
    out.mkdir(exist_ok=True)
    print("Generating wallpaper renders...")
    generate_wallpaper_renders(out)
    print("Generating application UI captures...")
    generate_app_screenshots(out)
    print("All screenshots generated successfully in:", out.resolve())
