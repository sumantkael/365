from PIL import Image
from pathlib import Path
import shutil

SOURCE_IMG = Path(r"C:\Users\User\.gemini\antigravity-ide\brain\e46ee1ba-ccff-4725-85fa-e42faac989ac\.user_uploaded\media_1789606576491.png")
ASSETS_DIR = Path(__file__).parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

APP_PNG = ASSETS_DIR / "app_icon.png"
APP_ICO = ASSETS_DIR / "app_icon.ico"

def create_icons():
    if not SOURCE_IMG.exists():
        print(f"Source image not found at {SOURCE_IMG}")
        return

    # 1. Copy source PNG
    shutil.copyfile(SOURCE_IMG, APP_PNG)
    print(f"Saved {APP_PNG}")

    # 2. Convert to multi-size Windows .ICO (16, 24, 32, 48, 64, 128, 256)
    img = Image.open(SOURCE_IMG)
    # Ensure RGB / RGBA
    img = img.convert("RGBA")
    
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(APP_ICO, format="ICO", sizes=icon_sizes)
    print(f"Generated multi-resolution Windows icon: {APP_ICO}")

if __name__ == "__main__":
    create_icons()
