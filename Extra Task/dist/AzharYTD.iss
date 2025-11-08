; AzharYTD.iss - Inno Setup script
; Input files: dist\AzharYTD.exe (from PyInstaller), yt-dlp.exe, ffmpeg.exe, azhar.ico (optional)

[Setup]
AppId={{B4B4C6C8-6F2E-4B2C-9A5E-2C9B7A1DAZHR}
AppName=Azhar YouTube Downloader
AppVersion=1.0.0
AppPublisher=Azhar
DefaultDirName={autopf}\Azhar\YouTubeDownloader
DefaultGroupName=Azhar Tools
OutputBaseFilename=AzharYTD-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=azhar.ico
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\AzharYTD.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\yt-dlp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\azhar.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Azhar YouTube Downloader"; Filename: "{app}\AzharYTD.exe"; IconFilename: "{app}\azhar.ico"
Name: "{commondesktop}\Azhar YouTube Downloader"; Filename: "{app}\AzharYTD.exe"; IconFilename: "{app}\azhar.ico"

[Run]
Filename: "{app}\AzharYTD.exe"; Description: "Launch Azhar YouTube Downloader"; Flags: nowait postinstall skipifsilent
