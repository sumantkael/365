# Day — Lightweight Minimalist Windows Wallpaper Utility

**Day** is a clean, native-feeling desktop wallpaper utility for Windows that visualizes the progression of the year:
- Day of year (e.g. `260`)
- Days remaining (e.g. `105 DAYS LEFT`)
- Both combined
- Dot visualization (each day represented as a dot; completed are solid, remaining are hollow)

No background daemon required — updates once a day via Windows Task Scheduler and terminates immediately.

## Requirements
- Python 3.9+
- Pillow (`pip install pillow`)

## Running Locally

1. **Install dependencies**:
   ```bash
   pip install pillow
   ```

2. **Open the Settings GUI**:
   ```bash
   python main.py
   ```

3. **Trigger a Headless Wallpaper Update**:
   ```bash
   python main.py --update
   ```

## Running Tests & Verifications

- **Unit tests for leap years & day calculations**:
  ```bash
  python test_date.py
  ```

- **Generate sample wallpapers for all modes**:
  ```bash
  python test_render.py
  ```

## Building Executable (PyInstaller)

```bash
pip install pyinstaller
pyinstaller day.spec
```
The compiled standalone executable will be located at `dist/Day.exe`.

## Building Windows Installer (Inno Setup)

Compile `installer.iss` with Inno Setup Compiler (`iscc`):
```bash
iscc installer.iss
```
This produces `dist/installer/Day-Setup-1.0.0.exe`, which installs `Day.exe`, configures shortcuts, sets up the scheduled task, and cleans up completely on uninstall.
