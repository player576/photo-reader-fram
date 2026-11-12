; Inno Setup 6
#define MyAppName "Fram"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "AIDanil Studio"
[Setup]
AppId={{8E6DB5CE-AB28-4A1C-9E16-1A1C4C0E9D3A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Fram
DefaultGroupName=Fram
OutputDir=installer
OutputBaseFilename=Fram-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительные задачи:"
[Files]
Source: "dist\Fram\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Fram"; Filename: "{app}\Fram.exe"
Name: "{autodesktop}\Fram"; Filename: "{app}\Fram.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\Fram.exe"; Description: "Запустить Fram"; Flags: postinstall nowait skipifsilent
