import urllib.request
from pathlib import Path

FONTS_DIR = Path(__file__).parent / "assets" / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# Clean, modern Plus Jakarta Sans font from Google Fonts / Tokotype repo
URLS = {
    "PlusJakartaSans-Bold.ttf": "https://raw.githubusercontent.com/tokotype/PlusJakartaSans/master/fonts/ttf/PlusJakartaSans-Bold.ttf",
    "PlusJakartaSans-Regular.ttf": "https://raw.githubusercontent.com/tokotype/PlusJakartaSans/master/fonts/ttf/PlusJakartaSans-Regular.ttf",
    "PlusJakartaSans-Medium.ttf": "https://raw.githubusercontent.com/tokotype/PlusJakartaSans/master/fonts/ttf/PlusJakartaSans-Medium.ttf"
}

def download_fonts():
    for name, url in URLS.items():
        dest = FONTS_DIR / name
        if not dest.exists():
            print(f"Downloading {name}...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as resp, open(dest, 'wb') as out:
                    out.write(resp.read())
                print(f"Downloaded {name} successfully.")
            except Exception as e:
                print(f"Failed to download {name}: {e}")

if __name__ == "__main__":
    download_fonts()
