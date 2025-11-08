# Azhar YouTube Video Downloader — README

A Tkinter desktop app for Windows to download YouTube videos or audio with live progress, pause/resume, and a clean animated UI. Uses yt-dlp for fetching and FFmpeg for merging.

## Features

- URL sanitizer (watch/shorts/youtu.be → canonical watch URL)
- Quality presets:
  - Best Available, 4K, 2K, 1080p, 720p, 480p, 360p, 144p
  - Audio Only (M4A)
- Live stats: percent, total size, downloaded, speed
- Pause, Resume (keeps .part), and Cancel
- Error guidance (missing yt-dlp, missing/old FFmpeg)
- Animated gradient background, shimmer progress, hover/ripple buttons
- Optional glow replaced with a breathing 5‑point star that cycles colors and shows “Azhar”
- Output folder: “Azhar Youtube Video Downloader” next to the app

## Screenshots

Place screenshots under docs/ and reference them here:

![Main UI](docs/screenshot-1.png)
![Progress](docs/screenshot-2.png)

## How it works

- Invokes yt-dlp via subprocess and parses stdout to update progress without freezing the UI.  
- For mixed streams, restores last video totals during merge so stats remain meaningful.  
- “Audio Only” uses bestaudio[ext=m4a] and skips merging.

## Project layout

Azhar-YouTube-Video-Downloader/
├─ YTDByAzharV4Complete.py
├─ yt-dlp.exe
├─ ffmpeg.exe
├─ logo.png
├─ azhar.ico
├─ dist/
│ ├─ AzharYTD.exe
│ ├─ yt-dlp.exe
│ ├─ ffmpeg.exe
│ ├─ azhar.ico
│ ├─ AzharYTD.iss
│ └─ Output/
│ └─ AzharYTD-Setup.exe
└─ docs/
├─ screenshot-1.png
└─ screenshot-2.png



## Quick start (dev)

git clone https://github.com/<your-user>/<your-repo>.git
cd <your-repo>
pip install yt-dlp

Ensure ffmpeg.exe is present or on PATH
python YTDByAzharV4Complete.py



## Build EXE — side‑by‑side (no code changes)

pyinstaller --onefile --noconsole --name "AzharYTD" --icon "azhar.ico" YTDByAzharV4Complete.py


undefined
copy /y yt-dlp.exe dist
copy /y ffmpeg.exe dist\



Ship the folder containing:
dist\AzharYTD.exe + yt-dlp.exe + ffmpeg.exe



## Build EXE — embedded binaries (already used)

pyinstaller --onefile --noconsole --name "AzharYTD" --icon "azhar.ico" ^
--add-binary "yt-dlp.exe;." --add-binary "ffmpeg.exe;." ^
YTDByAzharV4Complete.py


> If code does not point to extracted copies, still ship tools side‑by‑side or use the installer below.

## Windows installer (Inno Setup in dist/)

When AzharYTD.iss is inside dist/ with the files, use:

[Setup]
AppId={{B4B4C6C8-6F2E-4B2C-9A5E-2C9B7A1DAZHR}
AppName=Azhar YouTube Downloader
AppVersion=1.0.0
DefaultDirName={autopf}\Azhar\YouTubeDownloader
DefaultGroupName=Azhar Tools
OutputBaseFilename=AzharYTD-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=azhar.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "AzharYTD.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "yt-dlp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "azhar.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Azhar YouTube Downloader"; Filename: "{app}\AzharYTD.exe"; IconFilename: "{app}\azhar.ico"
Name: "{commondesktop}\Azhar YouTube Downloader"; Filename: "{app}\AzharYTD.exe"; IconFilename: "{app}\azhar.ico"

[Run]
Filename: "{app}\AzharYTD.exe"; Description: "Launch Azhar YouTube Downloader"; Flags: nowait postinstall skipifsilent


Compile to produce:
dist\Output\AzharYTD-Setup.exe



## Icon from PNG (Pillow)

pip install pillow
python - << "PY"
from PIL import Image
Image.open("logo.png").convert("RGBA").save(
"azhar.ico",
sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
)
print("Saved azhar.ico")
PY



## Usage

- Paste a YouTube URL  
- Select quality (e.g., 1080p or Audio Only)  
- Click DOWNLOAD; use Pause/Resume; Cancel removes partial file  
- Output appears at:
Azhar Youtube Video Downloader<Video Title> [Quality].mp4



## Troubleshooting

- “yt-dlp not found” → ensure `yt-dlp.exe` is beside the EXE or install via the Inno Setup installer.  
- “FFmpeg not found” → ensure `ffmpeg.exe` is beside the EXE or included in the installer.  
- SmartScreen → unsigned apps warn; “More info → Run anyway” or sign the installer.  
- EXE size → onefile bundles Python; this is expected.

## Roadmap

- Output folder picker  
- Playlist/batch downloads  
- Theme toggle (Light/Dark)  
- Auto-update for yt-dlp

## License

MIT — see `LICENSE`.

## Credits

- yt-dlp (MIT)  
- FFmpeg (LGPL/GPL)  
- Tkinter/ttk