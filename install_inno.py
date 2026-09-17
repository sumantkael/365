import json
import urllib.request
import subprocess
from pathlib import Path
import sys

DEST = Path(__file__).parent / "innosetup-installer.exe"

def download_and_install_inno():
    print("=" * 60)
    print("   DOWNLOADING INNO SETUP COMPILER FROM GITHUB...")
    print("=" * 60)

    # 1. Query GitHub API for latest release assets of jrsoftware/issrc
    api_url = "https://api.github.com/repos/jrsoftware/issrc/releases/latest"
    download_url = None
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            for asset in data.get("assets", []):
                name = asset.get("name", "")
                if name.startswith("innosetup-") and name.endswith(".exe"):
                    download_url = asset.get("browser_download_url")
                    print(f"Found Inno Setup release: {name}")
                    break
    except Exception as e:
        print(f"GitHub API query failed ({e}), falling back to direct release URLs...")

    # Fallbacks if API is rate-limited
    if not download_url:
        fallbacks = [
            "https://github.com/jrsoftware/issrc/releases/download/is-6_3_3/innosetup-6.3.3.exe",
            "https://github.com/jrsoftware/issrc/releases/download/is-6_3_2/innosetup-6.3.2.exe",
            "https://github.com/jrsoftware/issrc/releases/download/is-6_3_1/innosetup-6.3.1.exe",
            "https://github.com/jrsoftware/issrc/releases/download/is-6_3_0/innosetup-6.3.0.exe",
        ]
        download_url = fallbacks[0]

    # Download installer
    if not DEST.exists() or DEST.stat().st_size < 1000000:
        print(f"Downloading from: {download_url}")
        try:
            req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp, open(DEST, "wb") as out:
                out.write(resp.read())
            print(f"Downloaded installer ({DEST.stat().st_size} bytes)")
        except Exception as e:
            print(f"Download failed: {e}")
            return False

    print("\nRunning silent installation of Inno Setup...")
    try:
        cmd = [str(DEST), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-"]
        res = subprocess.run(cmd)
        print("Inno Setup installed successfully!")
        return True
    except Exception as e:
        print(f"Silent install failed: {e}")
        return False

if __name__ == "__main__":
    ok = download_and_install_inno()
    sys.exit(0 if ok else 1)
