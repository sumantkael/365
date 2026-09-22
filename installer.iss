#ifndef MyAppVersion
#define MyAppVersion "1.2.0"
#endif

[Setup]
AppId={{D37B4A4B-4E38-4394-813F-725B02AC17B9}
AppName=365 by L’ÆVOR STUDIO
AppVersion={#MyAppVersion}
AppPublisher=L’ÆVOR STUDIO
AppPublisherURL=https://www.instagram.com/leavorstudio/
AppSupportURL=https://www.instagram.com/leavorstudio/
AppUpdatesURL=https://www.instagram.com/leavorstudio/
DefaultDirName={autopf}\365
DefaultGroupName=365 by L’ÆVOR STUDIO
SetupIconFile=assets\app_icon.ico
UninstallDisplayName=365 by L’ÆVOR STUDIO
UninstallDisplayIcon={app}\Day.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist\installer
OutputBaseFilename=365-Setup-{#MyAppVersion}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest

[Files]
Source: "dist\Day.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "VERSION"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\fonts\*"; DestDir: "{autofonts}"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{autoprograms}\365 by L’ÆVOR STUDIO"; Filename: "{app}\Day.exe"
Name: "{autodesktop}\365 by L’ÆVOR STUDIO"; Filename: "{app}\Day.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\Day.exe"; Parameters: "--setup-scheduler"; Flags: runhidden
Filename: "{app}\Day.exe"; Parameters: "--update"; Flags: runhidden
Filename: "{app}\Day.exe"; Description: "{cm:LaunchProgram,365 by L’ÆVOR STUDIO}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "schtasks"; Parameters: "/delete /tn DayDailyWallpaper /f"; Flags: runhidden
Filename: "schtasks"; Parameters: "/delete /tn DayDailyWallpaper_Logon /f"; Flags: runhidden
Filename: "reg"; Parameters: "delete ""HKCU\Software\Microsoft\Windows\CurrentVersion\Run"" /v ""365DailyWallpaperUpdate"" /f"; Flags: runhidden
