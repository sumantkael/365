# 365 — by L’ÆVOR STUDIO

**365** is an ultra-minimal, typography-driven Windows desktop wallpaper utility designed by **L’ÆVOR STUDIO**. It visually transforms your desktop background into an intentional daily reminder of time, showing the progression of the year:

- **Mode A**: Day of Year (e.g. `260`)
- **Mode B**: Days Remaining (e.g. `105 DAYS LEFT`)
- **Mode C**: Both Combined
- **Mode D**: Year-in-Dots Matrix (Each row individually centered, past days filled, future days hollow, and today's date highlighted in crimson `#D81E1F`)

---

## Key Features

- **Zero Background Resource Usage**: Runs completely offline and consumes zero background RAM/CPU. Windows Task Scheduler silently refreshes the wallpaper at `00:01 AM` (and upon PC logon) and terminates immediately.
- **Vector-Crisp Visuals**: Rendered with 4x Supersampling Anti-Aliasing (SSAA) and Lanczos resampling to produce silky-smooth, SVG-quality dots with zero pixelation.
- **Plus Jakarta Sans Typography**: Bundled modern sans-serif typography for pure minimalist luxury aesthetics.
- **Consistent Monochromatic Dark UI**: Sleek settings window with live wallpaper preview, mode toggles, and an instant "Apply Wallpaper" action.
- **Real Windows Installation**: Packages into an official setup wizard (`365-Setup-1.0.0.exe`) with Start Menu/Desktop shortcuts, Control Panel integration, and clean uninstallation.

---

## Quick Start for Development

### 1. Requirements
- Windows 10 or Windows 11
- Python 3.9+
- Pillow (`pip install pillow`)

### 2. Run the App GUI
```cmd
python main.py
```

### 3. Run Silent Background Update
```cmd
python main.py --update
```

### 4. Run Unit Tests
```cmd
python test_date.py
```

---

## One-Click Build & Distribution

To build both the standalone executable and the official Windows installer:

```cmd
build.bat
```

This automated script:
1. Downloads the **Plus Jakarta Sans** font family.
2. Converts the **365** emblem into a multi-resolution Windows `.ico` asset.
3. Runs leap-year and date calculation unit tests.
4. Compiles the standalone executable: `dist\Day.exe` (wearing the 365 icon).
5. Compiles the official Windows installer: `dist\installer\365-Setup-1.0.0.exe`.

---

## Links & Branding

- **Studio**: [L’ÆVOR STUDIO](https://www.instagram.com/leavorstudio/)
- **Product**: 365 by L’ÆVOR STUDIO
