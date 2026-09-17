# 365 — by L’ÆVOR STUDIO: Release v1.1.0

## Release Title
```text
365 v1.1.0 — Automatic Daily Refresh, Year Progress (%) & Dynamic Builds
```

## Tag / Version
- **Tag**: `v1.1.0`
- **Target**: `main` / `master`
- **Release Name**: `365 v1.1.0 — Intelligent Daily Refresh & Year Progress`

---

## Release Description (Markdown)

```markdown
# 365 — by L’ÆVOR STUDIO (v1.1.0)
*An ultra-minimal, typography-driven daily desktop wallpaper utility for Windows.*

We are thrilled to present **v1.1.0** of **365**. This release introduces our most requested quality-of-life upgrade: **true zero-touch daily wallpaper updates**, alongside a refined **Year Progress (%)** indicator and a fully dynamic build pipeline.

---

### ✨ What's New in v1.1.0

#### 1. 🔄 True Zero-Touch Daily Refresh
Previously, users had to launch the application and click "Apply" to roll over to the next day. With v1.1.0, **365 manages everything automatically behind the scenes**:
- **Dual-Trigger System**:
  - **Windows Task Scheduler**: Silently refreshes your wallpaper at `00:01 AM` every night.
  - **Windows Startup / Logon Trigger**: If your PC was turned off, sleeping, or in hibernation over midnight, the wallpaper instantly and seamlessly catches up the moment you log in.
- **One-Click Activation**: Simply clicking **"Apply Wallpaper"** in the settings UI now automatically registers and verifies your background refresh tasks. No manual Windows configuration required.
- **Silent & Zero Background Resource Usage**: Runs completely offline, updates in milliseconds, and closes immediately. It consumes **0% CPU and 0 MB RAM** while you work.

#### 2. 📊 Minimalist Year Progress (%) Indicator
Stay mindful of time with a subtle, clean year percentage counter (e.g. `29%`, `71%`, `72%`):
- Cleanly integrated into the typographic hierarchy without cluttering the screen.
- Supported across all wallpaper modes:
  - **Both**: `DAY 105 • 260 DAYS LEFT • 29%`
  - **Day of Year**: `105 • OF 365 • 29%`
  - **Days Left**: `260 • DAYS LEFT • 29% OVER`
  - **Dots Matrix**: `105 / 365 • 260 DAYS REMAINING • 29%`
- Fully toggleable with a new **"Show Progress (%)"** checkbox in the settings window (enabled by default).
- Header in the settings app now displays your exact year completion rate in real time.

#### 3. 🔴 Dynamic Daily Matrix Updates
In Dots Matrix mode, the active **crimson red highlight (`#D81E1F`)** now automatically steps forward to today's date each morning, turning elapsed days into solid white markers and maintaining a pristine visual timeline of your year.

#### 4. ⚙️ Dynamic Versioning & Build Pipeline
- Centralized `VERSION` management: The build script and Inno Setup compiler now dynamically read the release version.
- Produces clean versioned installer artifacts: `dist/installer/365-Setup-1.1.0.exe`.
- Cleaner Windows uninstallation registry handling.

---

### 📦 Assets & Downloads

| File | Type | Description |
| :--- | :--- | :--- |
| **`365-Setup-1.1.0.exe`** | Windows Installer | Recommended. Full installer with Start Menu shortcuts and automatic scheduler setup. |
| **`Day.exe`** | Portable Executable | Standalone binary. Run directly without installation. |

---

### 🚀 Getting Started

1. Download and run **`365-Setup-1.1.0.exe`**.
2. Customize your preferred layout (Day of Year, Days Left, Both, or Dots Matrix) and theme (Dark/Light).
3. Click **"Apply Wallpaper"**.
4. That's it! Your wallpaper will automatically update every midnight and whenever you turn on your PC.

---

*Designed and crafted by **L’ÆVOR STUDIO**.*
*Follow us: [instagram.com/leavorstudio](https://www.instagram.com/leavorstudio/)*
```
