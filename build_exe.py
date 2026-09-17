import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_cmd(cmd, step_name):
    print(f"\n--- {step_name} ---")
    print(f"Running: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"\n[ERROR] {step_name} failed with exit code {res.returncode}")
        input("\nPress Enter to exit...")
        sys.exit(res.returncode)

def main():
    print("=" * 60)
    print("   DAY WALLPAPER UTILITY - BUILD SCRIPT")
    print("=" * 60)
    print(f"Python: {sys.executable} ({sys.version})")

    cwd = Path(__file__).parent.resolve()
    os.chdir(cwd)

    # 1. Install / update Pillow and PyInstaller
    run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", "pillow", "pyinstaller"], "1. Installing Dependencies")

    # 2. Run unit tests
    run_cmd([sys.executable, "test_date.py"], "2. Running Unit Tests")

    # 3. Generate sample wallpapers
    run_cmd([sys.executable, "test_render.py"], "3. Generating Test Wallpapers")

    # 4. PyInstaller build
    run_cmd([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", "day.spec"], "4. Compiling Day.exe with PyInstaller")

    exe_path = cwd / "dist" / "Day.exe"
    if exe_path.exists():
        print("\n" + "=" * 60)
        print("  SUCCESS! Day.exe HAS BEEN CREATED:")
        print(f"  {exe_path}")
        print("=" * 60)
    else:
        print(f"\n[WARNING] Could not locate {exe_path}")

    # Check for Inno Setup (iscc)
    iscc = shutil.which("iscc")
    if iscc:
        print("\n--- 5. Compiling Inno Setup Installer ---")
        subprocess.run([iscc, "installer.iss"])
        installer_path = cwd / "dist" / "installer" / "Day-Setup-1.0.0.exe"
        if installer_path.exists():
            print(f"Installer ready at: {installer_path}")
    else:
        print("\n[NOTE] Inno Setup compiler ('iscc') not in PATH.")
        print("You can run dist\\Day.exe directly as a standalone portable application.")

    print("\nAll done!")
    input("Press Enter to close this window...")

if __name__ == "__main__":
    main()
