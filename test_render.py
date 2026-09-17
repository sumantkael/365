from date_calculator import get_date_stats
from wallpaper_generator import render_wallpaper
from wallpaper_manager import get_screen_resolution
from pathlib import Path

def test_generate_all_modes():
    stats = get_date_stats()
    res = (1920, 1080)
    out_dir = Path("test_output")
    out_dir.mkdir(exist_ok=True)

    test_cases = [
        ("mode_a_day_dark", "day_of_year", "dark", True, False, True),
        ("mode_b_remaining_dark", "days_remaining", "dark", True, False, True),
        ("mode_c_both_dark", "both", "dark", True, False, True),
        ("mode_d_dots_dark", "dots", "dark", True, True, True),
        ("mode_a_day_light", "day_of_year", "light", True, False, True),
        ("mode_c_both_light", "both", "light", True, False, True),
        ("mode_d_dots_light", "dots", "light", True, True, True),
    ]

    for name, mode, theme, show_text, show_dots, show_percentage in test_cases:
        img = render_wallpaper(
            stats=stats,
            resolution=res,
            mode=mode,
            theme=theme,
            show_text=show_text,
            show_dots=show_dots,
            show_percentage=show_percentage
        )
        file_path = out_dir / f"{name}.png"
        img.save(file_path, "PNG")
        print(f"Generated test wallpaper: {file_path} (Resolution: {res})")

if __name__ == "__main__":
    test_generate_all_modes()
