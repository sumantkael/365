import sys
import argparse
from date_calculator import get_date_stats
from settings import SettingsManager
from wallpaper_generator import render_wallpaper
from wallpaper_manager import get_screen_resolution, set_desktop_wallpaper, get_wallpaper_cache_path
from scheduler import register_daily_task, is_task_scheduled

def update_wallpaper_headless() -> bool:
    """Headless wallpaper generation and application (called by Windows Task Scheduler)."""
    settings = SettingsManager()
    
    date_mode = settings.get("date_mode", "year")
    custom_target = None
    custom_start = None
    if date_mode == "custom":
        from date_calculator import parse_user_date
        target_str = settings.get("target_date", "")
        start_str = settings.get("target_start_date", "")
        custom_target = parse_user_date(target_str)
        custom_start = parse_user_date(start_str)

    stats = get_date_stats(
        date_mode=date_mode,
        custom_target_date=custom_target,
        custom_start_date=custom_start,
        event_title=settings.get("target_title", "")
    )
    resolution = get_screen_resolution()

    wallpaper_img = render_wallpaper(
        stats=stats,
        resolution=resolution,
        mode=settings.get("mode", "both"),
        theme=settings.get("theme", "light"),
        show_text=settings.get("show_text", True),
        show_dots=settings.get("show_dots", False),
        show_percentage=settings.get("show_percentage", True),
        wallpaper_font=settings.get("wallpaper_font", "geist")
    )

    cache_path = get_wallpaper_cache_path()
    wallpaper_img.save(cache_path, "PNG")
    return set_desktop_wallpaper(cache_path)

def main():
    parser = argparse.ArgumentParser(description="Day - Minimalist Daily Wallpaper Utility")
    parser.add_argument("--update", action="store_true", help="Perform headless wallpaper update and exit")
    parser.add_argument("--setup-scheduler", action="store_true", help="Ensure Windows Task Scheduler task is registered")
    args = parser.parse_args()

    if args.update:
        success = update_wallpaper_headless()
        sys.exit(0 if success else 1)

    if args.setup_scheduler:
        ok = register_daily_task()
        sys.exit(0 if ok else 1)

    # If no flags passed, launch settings GUI
    from ui import DaySettingsApp
    app = DaySettingsApp()
    app.mainloop()

if __name__ == "__main__":
    main()
