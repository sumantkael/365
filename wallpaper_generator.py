import math
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from date_calculator import DateStats

# Color palettes: Ultra-modern, refined contrast
PALETTES = {
    "dark": {
        "bg_top": (28, 28, 34),        # Spotlight source
        "bg_bottom": (11, 11, 13),     # Deep carbon ambient
        "primary": (255, 255, 255),    # Clean white
        "secondary": (160, 160, 172),  # Soft muted silver
        "accent": (216, 30, 31),       # Crimson Accent
        "dot_filled": (245, 245, 250), # Crisp solid filled dot
        "dot_empty": (52, 52, 62),     # Visible, clean hollow outline
        "dot_today": (216, 30, 31),    # Distinct crimson red highlight (#D81E1F)
    },
    "light": {
        "bg_top": (250, 250, 252),     # Clean linen ambient
        "bg_bottom": (238, 238, 242),  # Soft shadow floor
        "primary": (17, 17, 20),       # Deep obsidian
        "secondary": (115, 115, 126),  # Slate grey
        "accent": (216, 30, 31),       # Crimson Accent
        "dot_filled": (22, 22, 28),    # Dark filled dot
        "dot_empty": (205, 205, 214),  # Soft empty dot
        "dot_today": (216, 30, 31),    # Distinct crimson red highlight (#D81E1F)
    }
}

# Typography Cache
_FONT_CACHE = {}

def get_font(variant: str = "geist_sans", size: int = 14, bold: bool = False) -> ImageFont.ImageFont:
    """
    Loads font by key. Supported wallpaper fonts:
    - 'geist' / 'geist_sans' / 'geist_mono'
    - 'instrument_serif' / 'instrument_serif_italic'
    """
    key = (variant, size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    base_dir = Path(__file__).parent
    fonts_dir = base_dir / "assets" / "fonts"
    if not fonts_dir.exists():
        fonts_dir = Path(sys.executable).parent / "assets" / "fonts"

    filename_candidates = []
    if variant in ["instrument_serif", "instrument"]:
        filename_candidates = ["InstrumentSerif-Regular.ttf", "InstrumentSerif-Italic.ttf", "georgia.ttf"]
    elif variant in ["instrument_serif_italic", "instrument_italic"]:
        filename_candidates = ["InstrumentSerif-Italic.ttf", "InstrumentSerif-Regular.ttf", "georgiai.ttf"]
    elif variant == "geist_mono":
        filename_candidates = ["GeistMono-Variable.ttf", "Geist-Variable.ttf", "PlusJakartaSans-Bold.ttf"]
    else: # geist / geist_sans
        filename_candidates = ["Geist-Variable.ttf", "GeistMono-Variable.ttf", "PlusJakartaSans-Regular.ttf"]

    for fn in filename_candidates:
        fpath = fonts_dir / fn
        if fpath.exists():
            try:
                font = ImageFont.truetype(str(fpath), size)
                _FONT_CACHE[key] = font
                return font
            except Exception:
                continue

    # Fallback to Windows native fonts
    windows_fonts = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
    if "instrument" in variant:
        cand = [windows_fonts / "georgia.ttf", windows_fonts / "times.ttf"]
    elif variant == "geist_mono":
        cand = [windows_fonts / "consola.ttf", windows_fonts / "cascadiamono.ttf"]
    else:
        cand = [windows_fonts / ("segoeuib.ttf" if bold else "segoeui.ttf")]

    for fpath in cand:
        if fpath.exists():
            try:
                font = ImageFont.truetype(str(fpath), size)
                _FONT_CACHE[key] = font
                return font
            except Exception:
                continue

    font = ImageFont.load_default()
    _FONT_CACHE[key] = font
    return font

def _create_spotlight_texture(w: int, h: int, theme: str) -> Image.Image:
    """
    Creates premium Dark Carbon Spotlight or Linen Weave texture.
    """
    palette = PALETTES.get(theme, PALETTES["dark"])
    img = Image.new("RGB", (w, h), color=palette["bg_bottom"])
    draw = ImageDraw.Draw(img)

    if theme == "dark":
        # Dark Carbon Spotlight: Radial spotlight gradient from top center
        cx, cy = w // 2, 0
        top_color = palette["bg_top"]
        bottom_color = palette["bg_bottom"]

        steps = 28
        for s in range(steps, 0, -1):
            factor = s / steps
            rad_x = int((w * 0.7) * factor)
            rad_y = int((h * 0.65) * factor)
            r = int(bottom_color[0] + (top_color[0] - bottom_color[0]) * (1 - factor))
            g = int(bottom_color[1] + (top_color[1] - bottom_color[1]) * (1 - factor))
            b = int(bottom_color[2] + (top_color[2] - bottom_color[2]) * (1 - factor))
            draw.ellipse((cx - rad_x, cy - rad_y, cx + rad_x, cy + rad_y), fill=(r, g, b))

        # Subtle micro-carbon dot grid
        grid_step = max(32, w // 60)
        grid_color = (25, 25, 30)
        for gx in range(0, w, grid_step):
            for gy in range(0, h, grid_step):
                draw.point((gx, gy), fill=grid_color)

    else:
        # Linen Weave: Soft top-down subtle gradient with fine weave lines
        top_color = palette["bg_top"]
        bottom_color = palette["bg_bottom"]
        for y in range(0, h, 4):
            factor = y / h
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * factor)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * factor)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * factor)
            draw.rectangle((0, y, w, y + 4), fill=(r, g, b))

        # Soft linen cross-hatch texture lines
        weave_color = (230, 230, 235)
        grid_step = max(24, w // 80)
        for gx in range(0, w, grid_step):
            draw.line((gx, 0, gx, h), fill=weave_color, width=1)

    return img

def render_wallpaper(
    stats: DateStats,
    resolution: tuple[int, int] = (1920, 1080),
    mode: str = "both",
    theme: str = "light",
    show_text: bool = True,
    show_dots: bool = False,
    show_percentage: bool = True,
    wallpaper_font: str = "geist",
    fast_preview: bool = False
) -> Image.Image:
    """
    Renders wallpaper with customizable typography choice:
    - 'geist' (Geist Sans & Mono)
    - 'instrument_serif' (Instrument Serif Editorial Luxury & Geist Mono)
    """
    palette = PALETTES.get(theme, PALETTES["light"])
    target_width, target_height = resolution

    # 4x Supersampling for ultra-sharp desktop wallpapers, 1x for instant UI previews
    scale = 1 if fast_preview else 4
    w = target_width * scale
    h = target_height * scale

    # 1. Background Generation
    img = _create_spotlight_texture(w, h, theme)
    draw = ImageDraw.Draw(img)

    render_dots = show_dots or (mode == "dots")
    render_text = show_text if mode != "dots" else show_text

    pct_str = f"{stats.percentage_elapsed_exact:.1f}%"
    is_custom = getattr(stats, "date_mode", "year") == "custom"
    event_title = getattr(stats, "event_title", "")
    event_suffix = f"UNTIL {event_title.upper()}" if event_title else "UNTIL TARGET"

    if is_custom:
        if mode == "day_of_year":
            primary_text = f"DAY {stats.day_of_year}"
            secondary_text = f"OF {stats.total_days} {event_suffix} • {pct_str}" if show_percentage else f"OF {stats.total_days} {event_suffix}"
        elif mode == "days_remaining":
            primary_text = str(stats.days_remaining)
            secondary_text = f"DAYS {event_suffix} • {pct_str} OVER" if show_percentage else f"DAYS {event_suffix}"
        elif mode == "both":
            primary_text = f"{stats.days_remaining} DAYS"
            secondary_text = f"{event_suffix} • {pct_str} PASSED" if show_percentage else event_suffix
        elif mode == "dots":
            primary_text = f"{stats.days_remaining} DAYS {event_suffix}" if event_title else f"{stats.day_of_year} / {stats.total_days} DAYS"
            secondary_text = f"{pct_str} COMPLETED • {stats.days_remaining} DAYS LEFT" if show_percentage else f"{stats.days_remaining} DAYS LEFT"
        else:
            primary_text = f"{stats.days_remaining} DAYS"
            secondary_text = f"{event_suffix} • {pct_str}" if show_percentage else event_suffix
    else:
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

    # 2. Render Anti-Aliased Dot Matrix
    if render_dots:
        total_dots = stats.total_days
        display_dots = min(total_dots, 500)
        current_dot_idx = min(stats.day_of_year, display_dots)

        if display_dots <= 100:
            cols = 10
        elif display_dots <= 200:
            cols = 20
        else:
            cols = 25

        rows = math.ceil(display_dots / cols)

        dot_radius = int(5.5 * base_unit)
        dot_spacing_x = int(28 * base_unit)
        dot_spacing_y = int(28 * base_unit)

        if rows > 16:
            scaling = 16.0 / rows
            dot_radius = max(2, int(dot_radius * scaling))
            dot_spacing_x = max(10, int(dot_spacing_x * scaling))
            dot_spacing_y = max(10, int(dot_spacing_y * scaling))

        grid_width = (cols - 1) * dot_spacing_x
        grid_height = (rows - 1) * dot_spacing_y

        grid_offset_y = (h - grid_height) // 2
        if render_text:
            grid_offset_y += int(60 * base_unit)

        grid_offset_x = (w - grid_width) // 2
        stroke_width = max(2, int(2.2 * base_unit))

        for row in range(rows):
            start_idx = row * cols
            end_idx = min(start_idx + cols, display_dots)
            row_count = end_idx - start_idx
            
            row_width = (row_count - 1) * dot_spacing_x
            row_offset_x = (w - row_width) // 2
            cy = grid_offset_y + row * dot_spacing_y

            for col in range(row_count):
                i = start_idx + col
                cx = row_offset_x + col * dot_spacing_x

                bbox = (cx - dot_radius, cy - dot_radius, cx + dot_radius, cy + dot_radius)
                dot_num = i + 1

                if dot_num == current_dot_idx:
                    draw.ellipse(bbox, fill=palette["dot_today"])
                elif dot_num < current_dot_idx:
                    draw.ellipse(bbox, fill=palette["dot_filled"])
                else:
                    draw.ellipse(bbox, outline=palette["dot_empty"], width=stroke_width)

    # 3. Render Typography (Geist vs Instrument Serif)
    if render_text:
        is_serif = (wallpaper_font == "instrument_serif")

        if mode == "dots":
            font_main = get_font("instrument_serif" if is_serif else "geist_mono", int(32 * base_unit if is_serif else 28 * base_unit), bold=True)
            font_sub = get_font("instrument_serif" if is_serif else "geist_sans", int(16 * base_unit if is_serif else 14 * base_unit), bold=False)
            text_y = grid_offset_y - int(95 * base_unit)

            draw.text((w // 2, text_y), primary_text, font=font_main, fill=palette["primary"], anchor="mm")
            draw.text((w // 2, text_y + int(36 * base_unit)), secondary_text, font=font_sub, fill=palette["secondary"], anchor="mm")
        else:
            if is_serif:
                main_size = int(82 * base_unit if mode == "both" else 105 * base_unit)
                sub_size = int(24 * base_unit)
                font_main = get_font("instrument_serif", main_size, bold=False)
                font_sub = get_font("instrument_serif", sub_size, bold=False)
            else:
                main_size = int(68 * base_unit if mode == "both" else 88 * base_unit)
                sub_size = int(21 * base_unit)
                font_main = get_font("geist_mono", main_size, bold=True)
                font_sub = get_font("geist_sans", sub_size, bold=False)

            center_y = h // 2
            if render_dots:
                center_y = grid_offset_y - int(105 * base_unit)

            draw.text((w // 2, center_y - int(24 * base_unit)), primary_text, font=font_main, fill=palette["primary"], anchor="mm")
            draw.text((w // 2, center_y + int(46 * base_unit)), secondary_text, font=font_sub, fill=palette["secondary"], anchor="mm")

    # Downsample if supersampled
    if scale > 1:
        return img.resize((target_width, target_height), resample=Image.Resampling.LANCZOS)
    return img
