import urllib.request
from pathlib import Path

FONTS_DIR = Path(__file__).parent / "assets" / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# Wallpaper Typography: Geist & Instrument Serif
URLS = {
    # 1. Geist Sans
    "Geist-Variable.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/geist/Geist%5Bwght%5D.ttf",
    # 2. Geist Mono
    "GeistMono-Variable.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/geistmono/GeistMono%5Bwght%5D.ttf",
    # 3. Instrument Serif (Refined Editorial Luxury Serif from Google Fonts)
    "InstrumentSerif-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/InstrumentSerif-Regular.ttf",
    "InstrumentSerif-Italic.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/InstrumentSerif-Italic.ttf",
}

def download_fonts():
    for name, url in URLS.items():
        dest = FONTS_DIR / name
        if not dest.exists():
            print(f"Downloading {name}...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=20) as resp, open(dest, 'wb') as out:
                    out.write(resp.read())
                print(f"Downloaded {name} successfully.")
            except Exception as e:
                print(f"Failed to download {name}: {e}")

if __name__ == "__main__":
    download_fonts()
