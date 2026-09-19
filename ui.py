import sys
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from settings import SettingsManager
from date_calculator import get_date_stats
from wallpaper_generator import render_wallpaper
from wallpaper_manager import get_screen_resolution, set_desktop_wallpaper, get_wallpaper_cache_path
from scheduler import is_task_scheduled, register_daily_task, unregister_daily_task

# Modern Monochromatic UI Palette (Consistent, High-End Dark Aesthetic)
UI_THEME = {
    "bg": "#0D0D0E",              # Seamless deep background
    "card": "#161618",            # Elevated subtle dark card
    "border": "#222226",          # Micro-border
    "text_main": "#F4F4F6",       # Crisp white
    "text_muted": "#8A8A93",      # Muted silver
    "text_dim": "#55555C",        # Subtle label grey
    "accent": "#D81E1F",          # L'ÆVOR Red accent
    "btn_bg": "#1C1C20",          # Button dark
    "btn_hover": "#26262B",       # Button hover
    "btn_active": "#FFFFFF",      # Primary Apply button
    "btn_active_fg": "#0A0A0B",
}

import threading

# Enable Per-Monitor DPI Awareness before Tk initializes for crisp rendering on high-DPI displays
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1) # PROCESS_SYSTEM_DPI_AWARE or 2 for PER_MONITOR
except Exception:
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

class DaySettingsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("365 — by L’ÆVOR STUDIO")
        
        # Responsive, comfortable default size that works across 1080p, 1440p and 4K displays
        self.geometry("640x780")
        self.minsize(580, 700)
        
        # Consistent Deep Dark Background across the entire window
        self.configure(bg=UI_THEME["bg"])

        self.font_family = self._load_ui_fonts()
        self._set_app_icon()

        self.settings = SettingsManager()
        self.stats = get_date_stats()

        # Variables
        self.mode_var = tk.StringVar(value=self.settings.get("mode", "both"))
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "dark"))
        self.show_text_var = tk.BooleanVar(value=self.settings.get("show_text", True))
        self.show_dots_var = tk.BooleanVar(value=self.settings.get("show_dots", False))
        self.show_percentage_var = tk.BooleanVar(value=self.settings.get("show_percentage", True))
        self.auto_update_var = tk.BooleanVar(value=self.settings.get("auto_update", True))

        # Auto-ensure daily background refresh asynchronously to NEVER freeze app startup
        if self.auto_update_var.get():
            threading.Thread(target=register_daily_task, daemon=True).start()

        self.preview_image_tk = None
        self._build_ui()
        self.update_preview()

        # Auto-refresh date & percentage periodically (every 60 seconds)
        self._schedule_periodic_refresh()

    def _load_ui_fonts(self):
        """Register Plus Jakarta Sans font with Windows GDI so Tkinter can use it."""
        try:
            import ctypes
            base_dir = Path(__file__).parent
            for f in ["PlusJakartaSans-Bold.ttf", "PlusJakartaSans-Regular.ttf", "PlusJakartaSans-Medium.ttf"]:
                font_path = base_dir / "assets" / "fonts" / f
                if font_path.exists():
                    ctypes.windll.gdi32.AddFontResourceW(str(font_path))
            return "Plus Jakarta Sans"
        except Exception:
            return "Segoe UI"

    def _set_app_icon(self):
        """Sets L'ÆVOR icon for the Tkinter title bar and taskbar."""
        base_dir = Path(__file__).parent
        ico_path = base_dir / "assets" / "app_icon.ico"
        png_path = base_dir / "assets" / "app_icon.png"

        try:
            if ico_path.exists():
                self.iconbitmap(str(ico_path))
            elif png_path.exists():
                icon_img = ImageTk.PhotoImage(file=str(png_path))
                self.iconphoto(True, icon_img)
        except Exception:
            pass

    def _build_ui(self):
        # 1. Header Frame
        header = tk.Frame(self, bg=UI_THEME["bg"])
        header.pack(fill="x", padx=28, pady=(22, 10))

        title = tk.Label(
            header,
            text="365",
            font=(self.font_family, 24, "bold"),
            fg=UI_THEME["text_main"],
            bg=UI_THEME["bg"]
        )
        title.pack(anchor="w")

        self.subtitle_lbl = tk.Label(
            header,
            text=f"Year {self.stats.year} • Day {self.stats.day_of_year} of {self.stats.total_days} • {self.stats.percentage_elapsed_exact:.1f}% Completed • {self.stats.days_remaining} remaining",
            font=(self.font_family, 10),
            fg=UI_THEME["text_muted"],
            bg=UI_THEME["bg"]
        )
        self.subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # 2. Bottom Action Bar (Docked first to guarantee visibility)
        bottom_bar = tk.Frame(self, bg=UI_THEME["bg"])
        bottom_bar.pack(fill="x", padx=28, pady=(10, 22), side="bottom")

        # L'ÆVOR attribution
        credit = tk.Label(
            bottom_bar,
            text="MADE BY L’ÆVOR STUDIO",
            font=(self.font_family, 9, "bold"),
            fg=UI_THEME["text_dim"],
            bg=UI_THEME["bg"],
            cursor="hand2"
        )
        credit.pack(side="left", pady=10)
        credit.bind("<Button-1>", lambda e: webbrowser.open("https://www.instagram.com/leavorstudio/"))
        credit.bind("<Enter>", lambda e: credit.config(fg=UI_THEME["text_main"]))
        credit.bind("<Leave>", lambda e: credit.config(fg=UI_THEME["text_dim"]))

        # Action Buttons
        apply_btn = tk.Button(
            bottom_bar,
            text="Apply Wallpaper",
            font=(self.font_family, 10, "bold"),
            bg=UI_THEME["btn_active"],
            fg=UI_THEME["btn_active_fg"],
            activebackground="#E2E2E6",
            activeforeground="#000000",
            relief="flat",
            padx=20,
            pady=9,
            cursor="hand2",
            command=self.apply_wallpaper
        )
        apply_btn.pack(side="right")

        preview_btn = tk.Button(
            bottom_bar,
            text="Refresh",
            font=(self.font_family, 9),
            bg=UI_THEME["btn_bg"],
            fg=UI_THEME["text_main"],
            activebackground=UI_THEME["btn_hover"],
            activeforeground="#FFFFFF",
            relief="flat",
            padx=14,
            pady=9,
            cursor="hand2",
            command=self.update_preview
        )
        preview_btn.pack(side="right", padx=(0, 10))

        # 3. Wallpaper Preview Card
        preview_card = tk.Frame(self, bg=UI_THEME["card"], bd=1, relief="flat", highlightthickness=1, highlightbackground=UI_THEME["border"])
        preview_card.pack(fill="x", padx=28, pady=10)

        self.preview_canvas = tk.Label(preview_card, bg="#000000")
        self.preview_canvas.pack(padx=4, pady=4, fill="both", expand=True)

        # 4. Settings Card (Enclosed in a clean matching dark card)
        controls_card = tk.Frame(self, bg=UI_THEME["card"], bd=1, relief="flat", highlightthickness=1, highlightbackground=UI_THEME["border"])
        controls_card.pack(fill="both", expand=True, padx=28, pady=(10, 5))

        inner = tk.Frame(controls_card, bg=UI_THEME["card"])
        inner.pack(fill="both", expand=True, padx=18, pady=14)

        # Section 1: Mode
        mode_hdr = tk.Label(inner, text="WALLPAPER MODE", font=(self.font_family, 8, "bold"), fg=UI_THEME["text_dim"], bg=UI_THEME["card"])
        mode_hdr.pack(anchor="w", pady=(0, 6))

        modes_row = tk.Frame(inner, bg=UI_THEME["card"])
        modes_row.pack(fill="x", pady=(0, 14))

        modes = [
            ("Day of Year", "day_of_year"),
            ("Days Left", "days_remaining"),
            ("Both", "both"),
            ("Dots Matrix", "dots"),
        ]
        for text, val in modes:
            rb = tk.Radiobutton(
                modes_row,
                text=text,
                value=val,
                variable=self.mode_var,
                command=self.on_setting_changed,
                bg=UI_THEME["card"],
                fg=UI_THEME["text_main"],
                selectcolor=UI_THEME["bg"],
                activebackground=UI_THEME["card"],
                activeforeground="#FFFFFF",
                font=(self.font_family, 9),
                bd=0
            )
            rb.pack(side="left", padx=(0, 14))

        # Section 2: Theme & Visuals
        visual_hdr = tk.Label(inner, text="THEME & VISUALS", font=(self.font_family, 8, "bold"), fg=UI_THEME["text_dim"], bg=UI_THEME["card"])
        visual_hdr.pack(anchor="w", pady=(0, 6))

        visual_row = tk.Frame(inner, bg=UI_THEME["card"])
        visual_row.pack(fill="x", pady=(0, 14))

        dark_rb = tk.Radiobutton(
            visual_row, text="Dark Theme", value="dark",
            variable=self.theme_var, command=self.on_setting_changed,
            bg=UI_THEME["card"], fg=UI_THEME["text_main"], selectcolor=UI_THEME["bg"],
            activebackground=UI_THEME["card"], font=(self.font_family, 9), bd=0
        )
        dark_rb.pack(side="left", padx=(0, 14))

        light_rb = tk.Radiobutton(
            visual_row, text="Light Theme", value="light",
            variable=self.theme_var, command=self.on_setting_changed,
            bg=UI_THEME["card"], fg=UI_THEME["text_main"], selectcolor=UI_THEME["bg"],
            activebackground=UI_THEME["card"], font=(self.font_family, 9), bd=0
        )
        light_rb.pack(side="left", padx=(0, 22))

        text_cb = tk.Checkbutton(
            visual_row, text="Show Text", variable=self.show_text_var,
            command=self.on_setting_changed, bg=UI_THEME["card"], fg=UI_THEME["text_main"],
            selectcolor=UI_THEME["bg"], activebackground=UI_THEME["card"], font=(self.font_family, 9), bd=0
        )
        text_cb.pack(side="left", padx=(0, 14))

        dots_cb = tk.Checkbutton(
            visual_row, text="Show Dots", variable=self.show_dots_var,
            command=self.on_setting_changed, bg=UI_THEME["card"], fg=UI_THEME["text_main"],
            selectcolor=UI_THEME["bg"], activebackground=UI_THEME["card"], font=(self.font_family, 9), bd=0
        )
        dots_cb.pack(side="left", padx=(0, 14))

        pct_cb = tk.Checkbutton(
            visual_row, text="Show Progress (%)", variable=self.show_percentage_var,
            command=self.on_setting_changed, bg=UI_THEME["card"], fg=UI_THEME["text_main"],
            selectcolor=UI_THEME["bg"], activebackground=UI_THEME["card"], font=(self.font_family, 9), bd=0
        )
        pct_cb.pack(side="left")

        # Section 3: Daily Task Scheduler Toggle
        sched_frame = tk.Frame(inner, bg=UI_THEME["bg"], bd=0)
        sched_frame.pack(fill="x", pady=(4, 0), ipady=6, ipadx=8)

        sched_cb = tk.Checkbutton(
            sched_frame,
            text="Enable automatic daily wallpaper update (via Windows Task Scheduler)",
            variable=self.auto_update_var,
            command=self.on_scheduler_toggled,
            bg=UI_THEME["bg"],
            fg=UI_THEME["text_main"],
            selectcolor=UI_THEME["card"],
            activebackground=UI_THEME["bg"],
            font=(self.font_family, 9),
            bd=0
        )
        sched_cb.pack(side="left", padx=8)

    def on_setting_changed(self):
        self.settings.update(
            mode=self.mode_var.get(),
            theme=self.theme_var.get(),
            show_text=self.show_text_var.get(),
            show_dots=self.show_dots_var.get(),
            show_percentage=self.show_percentage_var.get()
        )
        self.update_preview()

    def _schedule_periodic_refresh(self):
        """Silently refreshes date calculations and stats every 60 seconds without hanging."""
        self.update_preview()
        self.after(60000, self._schedule_periodic_refresh)

    def on_scheduler_toggled(self):
        enabled = self.auto_update_var.get()
        self.settings.set("auto_update", enabled)
        def _bg_task():
            if enabled:
                ok = register_daily_task()
                if not ok:
                    self.after(0, lambda: messagebox.showwarning("Auto-Refresh", "Could not register daily background tasks. You may need to run with appropriate permissions."))
            else:
                unregister_daily_task()
        threading.Thread(target=_bg_task, daemon=True).start()

    def update_preview(self):
        # Refresh current stats in case date changed while app was open
        self.stats = get_date_stats()
        
        # Update header subtitle if widget exists
        if hasattr(self, "subtitle_lbl"):
            self.subtitle_lbl.config(
                text=f"Year {self.stats.year} • Day {self.stats.day_of_year} of {self.stats.total_days} • {self.stats.percentage_elapsed_exact:.1f}% Completed • {self.stats.days_remaining} remaining"
            )

        # Generate fast preview image (480 x 270 is 16:9) with fast_preview=True to keep UI snappy
        preview_img = render_wallpaper(
            stats=self.stats,
            resolution=(480, 270),
            mode=self.mode_var.get(),
            theme=self.theme_var.get(),
            show_text=self.show_text_var.get(),
            show_dots=self.show_dots_var.get(),
            show_percentage=self.show_percentage_var.get(),
            fast_preview=True
        )
        self.preview_image_tk = ImageTk.PhotoImage(preview_img)
        self.preview_canvas.configure(image=self.preview_image_tk)

    def apply_wallpaper(self):
        # Always ensure auto-update is active if the user has auto-update enabled
        if self.auto_update_var.get():
            threading.Thread(target=register_daily_task, daemon=True).start()

        self.stats = get_date_stats()
        resolution = get_screen_resolution()
        
        # High quality 4x SSAA render for the actual desktop wallpaper
        wallpaper_img = render_wallpaper(
            stats=self.stats,
            resolution=resolution,
            mode=self.mode_var.get(),
            theme=self.theme_var.get(),
            show_text=self.show_text_var.get(),
            show_dots=self.show_dots_var.get(),
            show_percentage=self.show_percentage_var.get(),
            fast_preview=False
        )
        cache_path = get_wallpaper_cache_path()
        wallpaper_img.save(cache_path, "PNG")
        
        success = set_desktop_wallpaper(cache_path)
        if success:
            messagebox.showinfo("Success", "Desktop wallpaper updated successfully!\n\nAutomatic daily refresh is active.")
        else:
            messagebox.showerror("Error", "Failed to update desktop wallpaper.")
