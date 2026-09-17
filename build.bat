@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   Auto-Locating Python Installation on your PC...
echo ========================================================
echo.

set "PY_EXE="

:: 1. Check 'py' Windows launcher
where py >nul 2>nul
if !ERRORLEVEL! equ 0 (
    set "PY_EXE=py"
    goto :Found
)

:: 2. Check standard AppData Local Programs
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :Found
    )
)

:: 3. Check C:\Program Files\Python*
for /d %%D in ("C:\Program Files\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :Found
    )
)

:: 4. Check C:\Python*
for /d %%D in ("C:\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :Found
    )
)

:: 5. Check Conda / Miniforge / Miniconda in standard locations
if exist "%USERPROFILE%\anaconda3\python.exe" set "PY_EXE=%USERPROFILE%\anaconda3\python.exe" & goto :Found
if exist "%USERPROFILE%\miniconda3\python.exe" set "PY_EXE=%USERPROFILE%\miniconda3\python.exe" & goto :Found
if exist "%LOCALAPPDATA%\anaconda3\python.exe" set "PY_EXE=%LOCALAPPDATA%\anaconda3\python.exe" & goto :Found
if exist "%LOCALAPPDATA%\miniconda3\python.exe" set "PY_EXE=%LOCALAPPDATA%\miniconda3\python.exe" & goto :Found

:NotFound
echo [ERROR] Could not automatically locate a Python installation.
echo.
echo "python" in your terminal gave:
echo "Python was not found; run without arguments to install from the Microsoft Store..."
echo.
echo Please install Python (e.g. from https://www.python.org/downloads/ )
echo and make sure to check:
echo    [x] "Add python.exe to PATH"
echo.
pause
exit /b 1

:Found
echo [OK] Located Python: "!PY_EXE!"
"!PY_EXE!" --version
echo.

echo [1/6] Installing / Updating Pillow and PyInstaller...
"!PY_EXE!" -m pip install --upgrade pillow pyinstaller
if !ERRORLEVEL! neq 0 (
    echo.
    echo [ERROR] Pip installation failed.
    pause
    exit /b 1
)

echo.
echo [2/6] Downloading premium typography font (Plus Jakarta Sans)...
"!PY_EXE!" download_fonts.py

echo.
echo [3/6] Generating L'ÆVOR multi-resolution Windows app icon (.ico)...
"!PY_EXE!" generate_icon.py

echo.
echo [4/6] Running tests...
"!PY_EXE!" test_date.py
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Date tests failed.
    pause
    exit /b 1
)

echo.
echo [5/6] Generating test preview wallpapers...
"!PY_EXE!" test_render.py

echo.
echo [6/6] Compiling Day.exe using PyInstaller...
"!PY_EXE!" -m PyInstaller --clean --noconfirm day.spec
if !ERRORLEVEL! neq 0 (
    echo [ERROR] PyInstaller compilation failed.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   SUCCESS! The EXE file is ready at:
echo   %CD%\dist\Day.exe
echo ========================================================
echo.

:: Check for Inno Setup compiler
set "ISCC_EXE="
where iscc >nul 2>nul
if %ERRORLEVEL% equ 0 set "ISCC_EXE=iscc"
if exist "C:\Program Files\Inno Setup 7\iscc.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 7\iscc.exe"
if exist "C:\Program Files (x86)\Inno Setup 7\iscc.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 7\iscc.exe"
if exist "%LOCALAPPDATA%\Programs\Inno Setup 7\iscc.exe" set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 7\iscc.exe"
if exist "C:\Program Files\Inno Setup 6\iscc.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 6\iscc.exe"
if exist "C:\Program Files (x86)\Inno Setup 6\iscc.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\iscc.exe"
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\iscc.exe" set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 6\iscc.exe"

if not defined ISCC_EXE (
    echo.
    echo Inno Setup not found. Auto-downloading and installing Inno Setup...
    "!PY_EXE!" install_inno.py
    if exist "C:\Program Files\Inno Setup 7\iscc.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 7\iscc.exe"
    if exist "C:\Program Files (x86)\Inno Setup 7\iscc.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 7\iscc.exe"
    if exist "%LOCALAPPDATA%\Programs\Inno Setup 7\iscc.exe" set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 7\iscc.exe"
    if exist "C:\Program Files\Inno Setup 6\iscc.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 6\iscc.exe"
    if exist "C:\Program Files (x86)\Inno Setup 6\iscc.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\iscc.exe"
    if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\iscc.exe" set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 6\iscc.exe"
)

:: Read version from VERSION file if present, else default to 1.1.0
set "APP_VERSION=1.1.0"
if exist "VERSION" (
    set /p APP_VERSION=<VERSION
    set "APP_VERSION=!APP_VERSION: =!"
)

if defined ISCC_EXE (
    echo.
    echo ========================================================
    echo   Compiling Windows Setup Installer v!APP_VERSION! with Inno Setup...
    echo ========================================================
    "%ISCC_EXE%" /DMyAppVersion="!APP_VERSION!" installer.iss
    echo.
    echo Setup installer created successfully at:
    echo dist\installer\365-Setup-!APP_VERSION!.exe
) else (
    echo.
    echo [NOTE] Inno Setup compiler was not found.
    echo To compile the setup installer, please install Inno Setup:
    echo https://jrsoftware.org/isdl.php
)

echo.
pause
