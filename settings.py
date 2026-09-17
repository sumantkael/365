import json
import os
from pathlib import Path

DEFAULT_SETTINGS = {
    "mode": "both",        # "day_of_year", "days_remaining", "both", "dots"
    "theme": "dark",       # "dark", "light"
    "show_text": True,
    "show_dots": False,
    "show_percentage": True,
    "auto_update": True,
}

def get_app_dir() -> Path:
    """Returns directory path for Day application data in %APPDATA%/Day."""
    appdata = os.getenv("APPDATA")
    if appdata:
        base_dir = Path(appdata) / "Day"
    else:
        base_dir = Path.home() / ".day"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def get_settings_file() -> Path:
    return get_app_dir() / "settings.json"

class SettingsManager:
    def __init__(self):
        self.file_path = get_settings_file()
        self.data = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception:
                # If corrupted, fallback to defaults
                self.data = dict(DEFAULT_SETTINGS)
        else:
            self.save()

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def update(self, **kwargs):
        self.data.update(kwargs)
        self.save()
