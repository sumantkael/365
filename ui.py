import sys
import calendar
import webbrowser
from datetime import date, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading

from settings import SettingsManager
from date_calculator import get_date_stats, parse_user_date
from wallpaper_generator import render_wallpaper
from wallpaper_manager import get_screen_resolution, set_desktop_wallpaper, get_wallpaper_cache_path
from scheduler import is_task_scheduled, register_daily_task, unregister_daily_task
from updater import check_for_update, RELEASES_URL, get_current_version

# Precision High-End Light & Dark Mode Aesthetics
THEMES = {
    "light": {
        "bg": "#F7F8FA",              # Clean architectural canvas
        "card": "#FFFFFF",            # Elevated white card
        "card_hover": "#F1F3F6",
        "border": "#E4E6EB",          # Crisp subtle border
        "text_main": "#111215",       # Deep black/charcoal
        "text_muted": "#5E636E",      # Balanced slate
        "text_dim": "#8C929D",        # Subtle label grey
        "accent": "#D81E1F",          # Crimson Accent
        "btn_bg": "#ECEEF2",
        "btn_hover": "#DFE2E8",
        "btn_active": "#111215",
        "btn_active_fg": "#FFFFFF",
        "input_bg": "#FAFAFC",
        "input_border": "#D2D6DC",
        "cal_active_bg": "#D81E1F",
        "cal_active_fg": "#FFFFFF",
        "status_ok": "#16A34A",
        "status_err": "#DC2626",
    },
    "dark": {
        "bg": "#0D0D10",              # Carbon deep obsidian
        "card": "#151518",            # Elevated micro-card
        "card_hover": "#1C1C22",
        "border": "#24242C",          # Crisp subtle border
        "text_main": "#F8F8FA",       # Crisp white
        "text_muted": "#8E8E9B",      # Silver slate
        "text_dim": "#585864",        # Subdued meta label
        "accent": "#D81E1F",          # Crimson Accent
        "btn_bg": "#1A1A20",
        "btn_hover": "#25252E",
        "btn_active": "#FFFFFF",
        "btn_active_fg": "#0B0B0E",
        "input_bg": "#101013",
        "input_border": "#282832",
        "cal_active_bg": "#D81E1F",
        "cal_active_fg": "#FFFFFF",
        "status_ok": "#4ADE80",
        "status_err": "#F87171",
    }
}

# DPI Awareness
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class DatePickerModal(tk.Toplevel):
    """
    Sleek OpenSourceUI-inspired Date Picker Card popup.
    Features Month/Year navigation, interactive day grid, and quick presets.
    """
    def __init__(self, parent, initial_date: date = None, on_select=None, theme_name="light"):
        super().__init__(parent)
        self.on_select = on_select
        self.theme = THEMES.get(theme_name, THEMES["light"])
        self.selected_date = initial_date or (date.today() + timedelta(days=30))
        self.view_year = self.selected_date.year
        self.view_month = self.selected_date.month

        self.title("Select Target Date")
        self.resizable(False, False)
        self.configure(bg=self.theme["card"])
        self.transient(parent)
        self.grab_set()

        self._build_card()

        # Fit card content neatly and center on parent
        self.update_idletasks()
        req_w = self.winfo_reqwidth() + 16
        req_h = self.winfo_reqheight() + 16
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        x = px + (pw - req_w) // 2
        y = py + (ph - req_h) // 2
        self.geometry(f"{req_w}x{req_h}+{max(10, x)}+{max(10, y)}")

    def _build_card(self):
        # Header with Month, Year & Arrows
        hdr = tk.Frame(self, bg=self.theme["card"])
        hdr.pack(fill="x", padx=16, pady=(16, 10))

        prev_btn = tk.Button(
            hdr, text="◀", font=("Segoe UI", 9, "bold"),
            bg=self.theme["btn_bg"], fg=self.theme["text_main"],
            activebackground=self.theme["btn_hover"], activeforeground=self.theme["text_main"],
            relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
            command=self._prev_month
        )
        prev_btn.pack(side="left")

        self.month_lbl = tk.Label(
            hdr, text="", font=("Geist Sans", 11, "bold"),
            bg=self.theme["card"], fg=self.theme["text_main"]
        )
        self.month_lbl.pack(side="left", expand=True)

        next_btn = tk.Button(
            hdr, text="▶", font=("Segoe UI", 9, "bold"),
            bg=self.theme["btn_bg"], fg=self.theme["text_main"],
            activebackground=self.theme["btn_hover"], activeforeground=self.theme["text_main"],
            relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
            command=self._next_month
        )
        next_btn.pack(side="right")

        # Days of week header
        days_hdr = tk.Frame(self, bg=self.theme["card"])
        days_hdr.pack(fill="x", padx=16, pady=(0, 6))
        for col, d in enumerate(["MO", "TU", "WE", "TH", "FR", "SA", "SU"]):
            lbl = tk.Label(
                days_hdr, text=d, font=("Geist Mono", 8, "bold"),
                bg=self.theme["card"], fg=self.theme["text_dim"], width=4
            )
            lbl.grid(row=0, column=col, padx=3, pady=2)

        # 6x7 Calendar Grid Frame
        self.grid_frame = tk.Frame(self, bg=self.theme["card"])
        self.grid_frame.pack(padx=16, pady=(0, 10))

        # Presets Bar
        presets_bar = tk.Frame(self, bg=self.theme["bg"], bd=1, relief="flat")
        presets_bar.pack(fill="x", side="bottom", padx=12, pady=12)

        presets = [
            ("+1 Mo", 30),
            ("+3 Mo", 90),
            ("+6 Mo", 180),
            ("+1 Yr", 365),
            ("2027", (date(2027, 1, 1) - date.today()).days),
        ]
        for name, days_add in presets:
            btn = tk.Button(
                presets_bar, text=name, font=("Geist Mono", 8),
                bg=self.theme["btn_bg"], fg=self.theme["text_muted"],
                activebackground=self.theme["btn_hover"], activeforeground=self.theme["text_main"],
                relief="flat", padx=6, pady=3, cursor="hand2",
                command=lambda d=days_add: self._select_preset_days(d)
            )
            btn.pack(side="left", padx=3, pady=4, expand=True)

        self._render_calendar_days()

    def _prev_month(self):
        if self.view_month == 1:
            self.view_month = 12
            self.view_year -= 1
        else:
            self.view_month -= 1
        self._render_calendar_days()

    def _next_month(self):
        if self.view_month == 12:
            self.view_month = 1
            self.view_year += 1
        else:
            self.view_month += 1
        self._render_calendar_days()

    def _select_preset_days(self, days_offset: int):
        target = date.today() + timedelta(days=days_offset)
        self._select_date(target)

    def _select_date(self, chosen: date):
        self.selected_date = chosen
        if self.on_select:
            self.on_select(chosen)
        self.destroy()

    def _render_calendar_days(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdatescalendar(self.view_year, self.view_month)
        month_name = calendar.month_name[self.view_month]
        self.month_lbl.config(text=f"{month_name.upper()} {self.view_year}")

        today = date.today()

        for r, week in enumerate(month_days):
            for c, d in enumerate(week):
                is_curr_month = (d.month == self.view_month)
                is_selected = (d == self.selected_date)
                is_today = (d == today)

                if is_selected:
                    bg_color = self.theme["cal_active_bg"]
                    fg_color = self.theme["cal_active_fg"]
                    weight = "bold"
                elif is_curr_month:
                    bg_color = self.theme["card"]
                    fg_color = self.theme["text_main"] if not is_today else self.theme["accent"]
                    weight = "bold" if is_today else "normal"
                else:
                    bg_color = self.theme["card"]
                    fg_color = self.theme["text_dim"]
                    weight = "normal"

                cell = tk.Button(
                    self.grid_frame,
                    text=str(d.day),
                    font=("Geist Mono", 9, weight),
                    bg=bg_color,
                    fg=fg_color,
                    activebackground=self.theme["card_hover"],
                    activeforeground=self.theme["text_main"],
                    relief="flat",
                    bd=0,
                    width=4,
                    height=1,
                    cursor="hand2",
                    command=lambda dt=d: self._select_date(dt)
                )
                cell.grid(row=r, column=c, padx=3, pady=2)


class DaySettingsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("365 — by L’ÆVOR STUDIO")

        self.settings = SettingsManager()
        # Default UI appearance is clean Light Mode
        self.current_theme_name = self.settings.get("theme", "light")
        self.theme = THEMES.get(self.current_theme_name, THEMES["light"])

        self.configure(bg=self.theme["bg"])
        self._load_ui_fonts()
        self._set_app_icon()

        # State Variables
        self.date_mode_var = tk.StringVar(value=self.settings.get("date_mode", "year"))
        self.target_date_str_var = tk.StringVar(value=self.settings.get("target_date", ""))
        self.target_title_var = tk.StringVar(value=self.settings.get("target_title", ""))
        self.mode_var = tk.StringVar(value=self.settings.get("mode", "both"))
        self.theme_var = tk.StringVar(value=self.current_theme_name)
        self.wallpaper_font_var = tk.StringVar(value=self.settings.get("wallpaper_font", "geist"))
        self.show_text_var = tk.BooleanVar(value=self.settings.get("show_text", True))
        self.show_dots_var = tk.BooleanVar(value=self.settings.get("show_dots", False))
        self.show_percentage_var = tk.BooleanVar(value=self.settings.get("show_percentage", True))
        self.auto_update_var = tk.BooleanVar(value=self.settings.get("auto_update", True))

        self.stats = self._calculate_current_stats()

        if self.auto_update_var.get():
            threading.Thread(target=register_daily_task, daemon=True).start()

        self.preview_image_tk = None
        self._build_ui()
        self._on_date_mode_changed()
        self.update_preview()

        # Auto-size window perfectly to content with comfortable padding
        self._auto_size_window()

        # Check for updates in the background without blocking UI
        threading.Thread(target=self._check_for_updates_silently, daemon=True).start()

        # Periodic 60s background refresh
        self.after(60000, self._schedule_periodic_refresh)

    def _auto_size_window(self):
        """Calculates natural content dimensions and sets geometry so user never needs to resize."""
        self.update_idletasks()
        req_w = max(640, self.winfo_reqwidth())
        req_h = self.winfo_reqheight() + 10
        self.geometry(f"{req_w}x{req_h}")
        self.minsize(580, req_h)

    def _load_ui_fonts(self):
        """Registers Geist and Pixel fonts with Windows GDI."""
        try:
            import ctypes
            base_dir = Path(__file__).parent
            fonts = [
                "Geist-Variable.ttf", "GeistMono-Variable.ttf", "Silkscreen-Bold.ttf",
                "PlusJakartaSans-Bold.ttf", "PlusJakartaSans-Regular.ttf"
            ]
            for f in fonts:
                font_path = base_dir / "assets" / "fonts" / f
                if font_path.exists():
                    ctypes.windll.gdi32.AddFontResourceW(str(font_path))
        except Exception:
            pass

    def _set_app_icon(self):
        base_dir = Path(__file__).parent
        ico_path = base_dir / "assets" / "app_icon.ico"
        png_path = base_dir / "assets" / "app_icon.png"
        try:
            if ico_path.exists():
                self.iconbitmap(str(ico_path))
            elif png_path.exists():
                img = ImageTk.PhotoImage(file=str(png_path))
                self.iconphoto(True, img)
        except Exception:
            pass

    def _calculate_current_stats(self):
        date_mode = self.date_mode_var.get() if hasattr(self, "date_mode_var") else self.settings.get("date_mode", "year")
        target_str = self.target_date_str_var.get() if hasattr(self, "target_date_str_var") else self.settings.get("target_date", "")
        title_str = self.target_title_var.get() if hasattr(self, "target_title_var") else self.settings.get("target_title", "")
        
        parsed_target = None
        parsed_start = None
        if date_mode == "custom" and target_str:
            parsed_target = parse_user_date(target_str)
            start_str = self.settings.get("target_start_date", "")
            if start_str:
                parsed_start = parse_user_date(start_str)

        return get_date_stats(
            date_mode=date_mode,
            custom_target_date=parsed_target,
            custom_start_date=parsed_start,
            event_title=title_str
        )

    def _build_ui(self):
        t = self.theme

        # 1. Header Frame with balanced spacing
        header = tk.Frame(self, bg=t["bg"])
        header.pack(fill="x", padx=28, pady=(22, 12))

        top_hdr_row = tk.Frame(header, bg=t["bg"])
        top_hdr_row.pack(fill="x")

        title = tk.Label(top_hdr_row, text="365", font=("Geist Sans", 26, "bold"), fg=t["text_main"], bg=t["bg"])
        title.pack(side="left")

        # Update Notification Pill (Initially hidden, revealed if new version available)
        self.update_banner_frame = tk.Frame(top_hdr_row, bg=t["bg"])

        self.subtitle_lbl = tk.Label(header, text="", font=("Geist Mono", 9), fg=t["text_muted"], bg=t["bg"])
        self.subtitle_lbl.pack(anchor="w", pady=(3, 0))

        # 2. Bottom Action Bar (Docked first to guarantee clean layout)
        bottom_bar = tk.Frame(self, bg=t["bg"])
        bottom_bar.pack(fill="x", padx=28, pady=(12, 20), side="bottom")

        credit = tk.Label(
            bottom_bar, text="MADE BY L’ÆVOR STUDIO", font=("Geist Sans", 8, "bold"),
            fg=t["text_dim"], bg=t["bg"], cursor="hand2"
        )
        credit.pack(side="left", pady=10)
        credit.bind("<Button-1>", lambda e: webbrowser.open("https://www.instagram.com/leavorstudio/"))

        apply_btn = tk.Button(
            bottom_bar, text="Apply Wallpaper", font=("Geist Sans", 10, "bold"),
            bg=t["btn_active"], fg=t["btn_active_fg"], relief="flat", padx=22, pady=9,
            cursor="hand2", command=self.apply_wallpaper
        )
        apply_btn.pack(side="right")

        preview_btn = tk.Button(
            bottom_bar, text="Refresh", font=("Geist Sans", 9),
            bg=t["btn_bg"], fg=t["text_main"], relief="flat", padx=15, pady=9,
            cursor="hand2", command=self.update_preview
        )
        preview_btn.pack(side="right", padx=(0, 10))

        # 3. Wallpaper Preview Card
        preview_card = tk.Frame(self, bg=t["card"], bd=1, relief="flat", highlightthickness=1, highlightbackground=t["border"])
        preview_card.pack(fill="x", padx=28, pady=(0, 14))

        self.preview_canvas = tk.Label(preview_card, bg="#000000")
        self.preview_canvas.pack(padx=6, pady=6, fill="both", expand=True)

        # 4. Settings Card (Enclosed in a clean card container)
        controls_card = tk.Frame(self, bg=t["card"], bd=1, relief="flat", highlightthickness=1, highlightbackground=t["border"])
        controls_card.pack(fill="x", padx=28, pady=(0, 4))

        inner = tk.Frame(controls_card, bg=t["card"])
        inner.pack(fill="x", padx=20, pady=16)

        # Mode Selection
        type_hdr = tk.Label(inner, text="TRACKING CALENDAR", font=("Geist Sans", 8, "bold"), fg=t["text_dim"], bg=t["card"])
        type_hdr.pack(anchor="w", pady=(0, 6))

        type_row = tk.Frame(inner, bg=t["card"])
        type_row.pack(fill="x", pady=(0, 10))

        rb_year = tk.Radiobutton(
            type_row, text="Year Calendar (365 Days)", value="year",
            variable=self.date_mode_var, command=self._on_date_mode_changed,
            bg=t["card"], fg=t["text_main"], selectcolor=t["bg"],
            activebackground=t["card"], font=("Geist Sans", 9, "bold"), bd=0
        )
        rb_year.pack(side="left", padx=(0, 20))

        rb_custom = tk.Radiobutton(
            type_row, text="Custom Target Date / Countdown", value="custom",
            variable=self.date_mode_var, command=self._on_date_mode_changed,
            bg=t["card"], fg=t["text_main"], selectcolor=t["bg"],
            activebackground=t["card"], font=("Geist Sans", 9, "bold"), bd=0
        )
        rb_custom.pack(side="left")

        # Custom Target Date Frame with Interactive Date Picker Button
        self.custom_date_frame = tk.Frame(inner, bg=t["bg"], bd=1, relief="flat", highlightthickness=1, highlightbackground=t["border"])

        inputs_row = tk.Frame(self.custom_date_frame, bg=t["bg"])
        inputs_row.pack(fill="x", padx=14, pady=(12, 6))

        date_input_col = tk.Frame(inputs_row, bg=t["bg"])
        date_input_col.pack(side="left", fill="x", expand=True, padx=(0, 12))

        date_lbl_row = tk.Frame(date_input_col, bg=t["bg"])
        date_lbl_row.pack(fill="x", pady=(0, 4))

        lbl_date = tk.Label(date_lbl_row, text="TARGET DATE (e.g. 21st Jan 2027):", font=("Geist Sans", 7, "bold"), fg=t["text_dim"], bg=t["bg"])
        lbl_date.pack(side="left")

        picker_btn = tk.Button(
            date_lbl_row, text="📅 Choose on Calendar", font=("Geist Sans", 7, "bold"),
            bg=t["btn_bg"], fg=t["accent"], activebackground=t["btn_hover"], activeforeground=t["text_main"],
            relief="flat", bd=0, padx=6, pady=1, cursor="hand2", command=self._open_date_picker
        )
        picker_btn.pack(side="right")

        self.date_entry = tk.Entry(
            date_input_col, textvariable=self.target_date_str_var,
            bg=t["input_bg"], fg=t["text_main"], insertbackground=t["text_main"],
            relief="flat", font=("Geist Mono", 9), bd=5, highlightthickness=1, highlightbackground=t["border"]
        )
        self.date_entry.pack(fill="x")
        self.date_entry.bind("<KeyRelease>", self._on_target_input_changed)

        title_input_col = tk.Frame(inputs_row, bg=t["bg"])
        title_input_col.pack(side="left", fill="x", expand=True)

        lbl_title = tk.Label(title_input_col, text="EVENT TITLE (e.g. Exam, Launch):", font=("Geist Sans", 7, "bold"), fg=t["text_dim"], bg=t["bg"])
        lbl_title.pack(anchor="w", pady=(0, 4))

        self.title_entry = tk.Entry(
            title_input_col, textvariable=self.target_title_var,
            bg=t["input_bg"], fg=t["text_main"], insertbackground=t["text_main"],
            relief="flat", font=("Geist Sans", 9), bd=5, highlightthickness=1, highlightbackground=t["border"]
        )
        self.title_entry.pack(fill="x")
        self.title_entry.bind("<KeyRelease>", self._on_target_input_changed)

        self.date_status_lbl = tk.Label(self.custom_date_frame, text="", font=("Geist Mono", 8), fg=t["text_muted"], bg=t["bg"])
        self.date_status_lbl.pack(anchor="w", padx=14, pady=(2, 10))

        # Wallpaper Styles
        mode_hdr = tk.Label(inner, text="WALLPAPER DISPLAY STYLE", font=("Geist Sans", 8, "bold"), fg=t["text_dim"], bg=t["card"])
        mode_hdr.pack(anchor="w", pady=(8, 6))

        modes_row = tk.Frame(inner, bg=t["card"])
        modes_row.pack(fill="x", pady=(0, 12))

        modes = [
            ("Day Progress", "day_of_year"),
            ("Days Left", "days_remaining"),
            ("Both", "both"),
            ("Dots Matrix", "dots"),
        ]
        for text, val in modes:
            rb = tk.Radiobutton(
                modes_row, text=text, value=val, variable=self.mode_var,
                command=self.on_setting_changed, bg=t["card"], fg=t["text_main"],
                selectcolor=t["bg"], activebackground=t["card"], font=("Geist Sans", 9), bd=0
            )
            rb.pack(side="left", padx=(0, 16))

        # Theme & Visual Controls
        visual_hdr = tk.Label(inner, text="WALLPAPER THEME & ELEMENTS", font=("Geist Sans", 8, "bold"), fg=t["text_dim"], bg=t["card"])
        visual_hdr.pack(anchor="w", pady=(6, 6))

        visual_row = tk.Frame(inner, bg=t["card"])
        visual_row.pack(fill="x", pady=(0, 12))

        dark_rb = tk.Radiobutton(
            visual_row, text="Dark Spotlight", value="dark",
            variable=self.theme_var, command=self._on_theme_changed,
            bg=t["card"], fg=t["text_main"], selectcolor=t["bg"],
            activebackground=t["card"], font=("Geist Sans", 9), bd=0
        )
        dark_rb.pack(side="left", padx=(0, 14))

        light_rb = tk.Radiobutton(
            visual_row, text="Linen Weave", value="light",
            variable=self.theme_var, command=self._on_theme_changed,
            bg=t["card"], fg=t["text_main"], selectcolor=t["bg"],
            activebackground=t["card"], font=("Geist Sans", 9), bd=0
        )
        light_rb.pack(side="left", padx=(0, 24))

        text_cb = tk.Checkbutton(
            visual_row, text="Show Text", variable=self.show_text_var,
            command=self.on_setting_changed, bg=t["card"], fg=t["text_main"],
            selectcolor=t["bg"], activebackground=t["card"], font=("Geist Sans", 9), bd=0
        )
        text_cb.pack(side="left", padx=(0, 14))

        dots_cb = tk.Checkbutton(
            visual_row, text="Show Dots", variable=self.show_dots_var,
            command=self.on_setting_changed, bg=t["card"], fg=t["text_main"],
            selectcolor=t["bg"], activebackground=t["card"], font=("Geist Sans", 9), bd=0
        )
        dots_cb.pack(side="left", padx=(0, 14))

        pct_cb = tk.Checkbutton(
            visual_row, text="Progress (%)", variable=self.show_percentage_var,
            command=self.on_setting_changed, bg=t["card"], fg=t["text_main"],
            selectcolor=t["bg"], activebackground=t["card"], font=("Geist Sans", 9), bd=0
        )
        pct_cb.pack(side="left")

        # Section: Wallpaper Typography (Only Two Clean Options)
        font_hdr = tk.Label(inner, text="WALLPAPER TYPOGRAPHY", font=("Geist Sans", 8, "bold"), fg=t["text_dim"], bg=t["card"])
        font_hdr.pack(anchor="w", pady=(6, 6))

        font_row = tk.Frame(inner, bg=t["card"])
        font_row.pack(fill="x", pady=(0, 12))

        geist_font_rb = tk.Radiobutton(
            font_row, text="Geist (Modern Clean)", value="geist",
            variable=self.wallpaper_font_var, command=self.on_setting_changed,
            bg=t["card"], fg=t["text_main"], selectcolor=t["bg"],
            activebackground=t["card"], font=("Geist Sans", 9, "bold"), bd=0
        )
        geist_font_rb.pack(side="left", padx=(0, 18))

        serif_font_rb = tk.Radiobutton(
            font_row, text="Instrument Serif (Editorial Luxury)", value="instrument_serif",
            variable=self.wallpaper_font_var, command=self.on_setting_changed,
            bg=t["card"], fg=t["text_main"], selectcolor=t["bg"],
            activebackground=t["card"], font=("Geist Sans", 9, "bold"), bd=0
        )
        serif_font_rb.pack(side="left")

        # Scheduler Bar
        sched_frame = tk.Frame(inner, bg=t["bg"], bd=1, relief="flat", highlightthickness=1, highlightbackground=t["border"])
        sched_frame.pack(fill="x", pady=(4, 0), ipady=6, ipadx=8)

        sched_cb = tk.Checkbutton(
            sched_frame, text="Enable automatic daily wallpaper update (silent Windows background refresh)",
            variable=self.auto_update_var, command=self.on_scheduler_toggled,
            bg=t["bg"], fg=t["text_main"], selectcolor=t["card"], activebackground=t["bg"], font=("Geist Sans", 9), bd=0
        )
        sched_cb.pack(side="left", padx=8)

    def _open_date_picker(self):
        curr = parse_user_date(self.target_date_str_var.get())
        DatePickerModal(
            self,
            initial_date=curr,
            on_select=self._on_date_picked,
            theme_name=self.current_theme_name
        )

    def _on_date_picked(self, chosen: date):
        formatted = chosen.strftime("%d %B %Y")
        self.target_date_str_var.set(formatted)
        self._on_target_input_changed()

    def _on_theme_changed(self):
        theme_name = self.theme_var.get()
        self.settings.set("theme", theme_name)
        self.on_setting_changed()

    def _on_date_mode_changed(self):
        mode = self.date_mode_var.get()
        if mode == "custom":
            self.custom_date_frame.pack(fill="x", pady=(0, 10), after=self.custom_date_frame.master.winfo_children()[1])
            self._validate_and_display_custom_date()
        else:
            self.custom_date_frame.pack_forget()

        self.settings.set("date_mode", mode)
        self.update_preview()
        # Readjust window height smoothly
        self._auto_size_window()

    def _on_target_input_changed(self, event=None):
        self._validate_and_display_custom_date()
        self.settings.update(
            target_date=self.target_date_str_var.get(),
            target_title=self.target_title_var.get()
        )
        self.update_preview()

    def _validate_and_display_custom_date(self):
        target_str = self.target_date_str_var.get().strip()
        t = self.theme
        if not target_str:
            self.date_status_lbl.config(
                text="Type any date (e.g. 21st Jan 2027) or click 'Choose on Calendar'",
                fg=t["text_muted"]
            )
            return

        parsed = parse_user_date(target_str)
        if parsed:
            today = date.today()
            delta = (parsed - today).days
            if delta >= 0:
                self.date_status_lbl.config(
                    text=f"✓ Target: {parsed.strftime('%B %d, %Y')} • {delta} days remaining from today",
                    fg=t["status_ok"]
                )
                if not self.settings.get("target_start_date"):
                    self.settings.set("target_start_date", today.isoformat())
            else:
                self.date_status_lbl.config(
                    text=f"Notice: {parsed.strftime('%B %d, %Y')} is in the past ({abs(delta)} days ago)",
                    fg=t["status_err"]
                )
        else:
            self.date_status_lbl.config(
                text="Unable to recognize format. Try '21 Jan 2027', '21/01/2027' or select from Calendar",
                fg=t["status_err"]
            )

    def on_setting_changed(self):
        self.settings.update(
            mode=self.mode_var.get(),
            theme=self.theme_var.get(),
            wallpaper_font=self.wallpaper_font_var.get(),
            show_text=self.show_text_var.get(),
            show_dots=self.show_dots_var.get(),
            show_percentage=self.show_percentage_var.get(),
            date_mode=self.date_mode_var.get(),
            target_date=self.target_date_str_var.get(),
            target_title=self.target_title_var.get()
        )
        self.update_preview()

    def _schedule_periodic_refresh(self):
        self.update_preview()
        self.after(60000, self._schedule_periodic_refresh)

    def on_scheduler_toggled(self):
        enabled = self.auto_update_var.get()
        self.settings.set("auto_update", enabled)
        def _bg_task():
            if enabled:
                ok = register_daily_task(force=True)
                if not ok:
                    self.after(0, lambda: messagebox.showwarning("Auto-Refresh", "Could not register daily background tasks."))
            else:
                unregister_daily_task()
        threading.Thread(target=_bg_task, daemon=True).start()

    def update_preview(self):
        self.stats = self._calculate_current_stats()
        
        if hasattr(self, "subtitle_lbl"):
            if self.stats.date_mode == "custom":
                event_txt = f" for {self.stats.event_title}" if self.stats.event_title else ""
                self.subtitle_lbl.config(
                    text=f"Countdown{event_txt} • {self.stats.days_remaining} days left • {self.stats.percentage_elapsed_exact:.1f}% Completed"
                )
            else:
                self.subtitle_lbl.config(
                    text=f"Year {self.stats.year} • Day {self.stats.day_of_year} of {self.stats.total_days} • {self.stats.percentage_elapsed_exact:.1f}% Completed • {self.stats.days_remaining} remaining"
                )

        preview_img = render_wallpaper(
            stats=self.stats,
            resolution=(480, 270),
            mode=self.mode_var.get(),
            theme=self.theme_var.get(),
            show_text=self.show_text_var.get(),
            show_dots=self.show_dots_var.get(),
            show_percentage=self.show_percentage_var.get(),
            wallpaper_font=self.wallpaper_font_var.get(),
            fast_preview=True
        )
        self.preview_image_tk = ImageTk.PhotoImage(preview_img)
        self.preview_canvas.configure(image=self.preview_image_tk)

    def apply_wallpaper(self):
        self.on_setting_changed()

        if self.auto_update_var.get():
            threading.Thread(target=register_daily_task, daemon=True).start()

        self.stats = self._calculate_current_stats()
        resolution = get_screen_resolution()
        
        wallpaper_img = render_wallpaper(
            stats=self.stats,
            resolution=resolution,
            mode=self.mode_var.get(),
            theme=self.theme_var.get(),
            show_text=self.show_text_var.get(),
            show_dots=self.show_dots_var.get(),
            show_percentage=self.show_percentage_var.get(),
            wallpaper_font=self.wallpaper_font_var.get(),
            fast_preview=False
        )
        cache_path = get_wallpaper_cache_path()
        wallpaper_img.save(cache_path, "PNG")
        
        success = set_desktop_wallpaper(cache_path)
        if success:
            messagebox.showinfo("Success", "Desktop wallpaper updated successfully!\n\nAutomatic daily refresh is active.")
        else:
            messagebox.showerror("Error", "Failed to update desktop wallpaper.")

    def _check_for_updates_silently(self):
        """Runs on background daemon thread to silently check GitHub for new releases."""
        update_info = check_for_update(timeout=4.0)
        if update_info:
            self.after(0, lambda: self._show_update_notification(update_info))

    def _show_update_notification(self, update_info: dict):
        """Displays an elegant, non-intrusive update pill next to the title."""
        t = self.theme
        new_ver = update_info.get("latest_version", "")
        url = update_info.get("download_url", RELEASES_URL)

        # Clear any prior widgets in banner
        for w in self.update_banner_frame.winfo_children():
            w.destroy()

        pill_frame = tk.Frame(self.update_banner_frame, bg=t["card"], bd=1, relief="flat", highlightthickness=1, highlightbackground=t["border"])
        pill_frame.pack(side="left", padx=14)

        msg_lbl = tk.Label(
            pill_frame,
            text=f"✦ Update v{new_ver} Available",
            font=("Geist Sans", 8, "bold"),
            fg=t["accent"],
            bg=t["card"],
            padx=8,
            pady=4
        )
        msg_lbl.pack(side="left")

        dl_btn = tk.Button(
            pill_frame,
            text="Download",
            font=("Geist Sans", 8, "bold"),
            bg=t["accent"],
            fg="#FFFFFF",
            activebackground="#B71819",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=lambda: webbrowser.open(url)
        )
        dl_btn.pack(side="left", padx=(0, 4), pady=2)

        self.update_banner_frame.pack(side="left")

if __name__ == "__main__":
    app = DaySettingsApp()
    app.mainloop()
