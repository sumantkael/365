import math
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from date_calculator import DateStats

# Color palettes: ultra-minimal, modern, no gradients
PALETTES = {
    "dark": {
        "bg": (15, 15, 17),            # Deep obsidian/graphite
        "primary": (255, 255, 255),    # Clean white
        "secondary": (150, 150, 158),  # Soft muted silver
        "dot_filled": (245, 245, 250), # Crisp solid filled dot
        "dot_empty": (55, 55, 64),     # Visible, clean hollow outline
        "dot_today": (216, 30, 31),    # Distinct crimson red highlight (#D81E1F)
    },
    "light": {
        "bg": (246, 246, 248),         # Clean off-white
        "primary": (17, 17, 19),       # Near-black
        "secondary": (120, 120, 128),  # Balanced grey
        "dot_filled": (20, 20, 24),    # Dark filled dot
        "dot_empty": (200, 200, 208),  # Soft empty dot
        "dot_today": (216, 30, 31),    # Distinct crimson red highlight (#D81E1F)
    }
}

def get_system_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Loads bundled Plus Jakarta Sans or clean system sans-serif fallback."""
    base_dir = Path(__file__).parent
    font_file = "PlusJakartaSans-Bold.ttf" if bold else "PlusJakartaSans-Regular.ttf"
    bundled_font = base_dir / "assets" / "fonts" / font_file

    if not bundled_font.exists():
        bundled_font = Path(sys.executable).parent / "assets" / "fonts" / font_file

    if bundled_font.exists():
        try:
            return ImageFont.truetype(str(bundled_font), size)
        except Exception:
            pass

    # Windows System Fonts fallback
    windows_fonts = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
    candidates = []
    if bold:
        candidates = [
            windows_fonts / "segoeuib.ttf",
            windows_fonts / "arialbd.ttf",
            windows_fonts / "calibrib.ttf",
        ]
    else:
        candidates = [
            windows_fonts / "segoeui.ttf",
            windows_fonts / "arial.ttf",
            windows_fonts / "calibri.ttf",
        ]

    for font_path in candidates:
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except Exception:
                continue

    return ImageFont.load_default()

def render_wallpaper(
    stats: DateStats,
    resolution: tuple[int, int] = (1920, 1080),
    mode: str = "both",
    theme: str = "dark",
    show_text: bool = True,
    show_dots: bool = False,
    show_percentage: bool = True,
    fast_preview: bool = False
) -> Image.Image:
    """
    Renders wallpaper. Uses 4x SSAA for final wallpaper, or 1x direct drawing for fast UI preview.
    """
    palette = PALETTES.get(theme, PALETTES["dark"])
    target_width, target_height = resolution

    # 4x Supersampling for ultra-sharp wallpapers, 1x for instant UI previews
    scale = 1 if fast_preview else 4
    w = target_width * scale
    h = target_height * scale

    img = Image.new("RGB", (w, h), color=palette["bg"])
    draw = ImageDraw.Draw(img)

    render_dots = show_dots or (mode == "dots")
    render_text = show_text if mode != "dots" else show_text

    pct_str = f"{stats.percentage_elapsed}%"

    if mode == "day_of_year":
        primary_text = str(stats.day_of_year)
        secondary_text = f"OF {stats.total_days} • {pct_str}" if show_percentage else f"OF {stats.total_days}"
    elif mode == "days_remaining":
        primary_text = str(stats.days_remaining)
        secondary_text = f"DAYS LEFT • {pct_str} OVER" if show_percentage else "DAYS LEFT"
    elif mode == "both":
        primary_text = f"DAY {stats.day_of_year}"
        secondary_text = f"{stats.days_remaining} DAYS LEFT • {pct_str}" if show_percentage else f"{stats.days_remaining} DAYS LEFT"
    elif mode == "dots":
        primary_text = f"{stats.day_of_year} / {stats.total_days}"
        secondary_text = f"{stats.days_remaining} DAYS REMAINING • {pct_str}" if show_percentage else f"{stats.days_remaining} DAYS REMAINING"
    else:
        primary_text = str(stats.day_of_year)
        secondary_text = f"{stats.days_remaining} DAYS LEFT • {pct_str}" if show_percentage else f"{stats.days_remaining} DAYS LEFT"

    base_unit = (target_height / 1080.0) * scale

    # 1. Render Anti-Aliased Dot Matrix
    if render_dots:
        total_dots = stats.total_days
        # Use 25 columns so 365 = 14 rows x 25 + 15 (last row has 15 dots, perfectly balanced and never an isolated dot)
        cols = 25
        rows = math.ceil(total_dots / cols)

        dot_radius = int(5.5 * base_unit)
        dot_spacing_x = int(28 * base_unit)
        dot_spacing_y = int(28 * base_unit)

        grid_width = (cols - 1) * dot_spacing_x
        grid_height = (rows - 1) * dot_spacing_y

        grid_offset_y = (h - grid_height) // 2
        if render_text:
            grid_offset_y += int(60 * base_unit)

        grid_offset_x = (w - grid_width) // 2

        stroke_width = max(2, int(2.2 * base_unit))

        for row in range(rows):
            start_idx = row * cols
            end_idx = min(start_idx + cols, total_dots)
            row_count = end_idx - start_idx
            
            # Row width based on actual number of dots in this row
            row_width = (row_count - 1) * dot_spacing_x
            row_offset_x = (w - row_width) // 2
            cy = grid_offset_y + row * dot_spacing_y

            for col in range(row_count):
                i = start_idx + col
                cx = row_offset_x + col * dot_spacing_x

                bbox = (cx - dot_radius, cy - dot_radius, cx + dot_radius, cy + dot_radius)
                day_num = i + 1

                if day_num == stats.day_of_year:
                    # Today's date: Distinct crimson red highlight (#D81E1F)
                    draw.ellipse(bbox, fill=palette["dot_today"])
                elif day_num < stats.day_of_year:
                    # Past elapsed days: Solid filled
                    draw.ellipse(bbox, fill=palette["dot_filled"])
                else:
                    # Future remaining days: Crisp hollow outline
                    draw.ellipse(bbox, outline=palette["dot_empty"], width=stroke_width)

    # 2. Render Typography (Plus Jakarta Sans)
    if render_text:
        if mode == "dots":
            font_main = get_system_font(int(28 * base_unit), bold=True)
            font_sub = get_system_font(int(14 * base_unit), bold=False)
            text_y = grid_offset_y - int(95 * base_unit)

            draw.text(
                (w // 2, text_y),
                primary_text,
                font=font_main,
                fill=palette["primary"],
                anchor="mm"
            )
            draw.text(
                (w // 2, text_y + int(36 * base_unit)),
                secondary_text,
                font=font_sub,
                fill=palette["secondary"],
                anchor="mm"
            )
        else:
            if mode == "both":
                main_size = int(68 * base_unit)
                sub_size = int(22 * base_unit)
            else:
                main_size = int(88 * base_unit)
                sub_size = int(24 * base_unit)

            font_main = get_system_font(main_size, bold=True)
            font_sub = get_system_font(sub_size, bold=False)

            center_y = h // 2
            if render_dots:
                center_y = grid_offset_y - int(105 * base_unit)

            draw.text(
                (w // 2, center_y - int(24 * base_unit)),
                primary_text,
                font=font_main,
                fill=palette["primary"],
                anchor="mm"
            )
            draw.text(
                (w // 2, center_y + int(46 * base_unit)),
                secondary_text,
                font=font_sub,
                fill=palette["secondary"],
                anchor="mm"
            )

    # Downsample if supersampled; return directly if fast preview
    if scale > 1:
        return img.resize((target_width, target_height), resample=Image.Resampling.LANCZOS)
    return img
