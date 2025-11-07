import subprocess
import threading
import re
import os
from tkinter import *
from tkinter import ttk, messagebox
from urllib.parse import urlparse, parse_qs

def to_watch_url(url: str) -> str:
    """
    Extracts the YouTube video ID from various URL formats
    and returns a clean, standard watch URL.
    """
    video_id = None
    
    if "watch?" in url:
        try: q = parse_qs(urlparse(url).query); video_id = q["v"][0]
        except: pass
    elif "/shorts/" in url:
        try: video_id = url.split("/shorts/")[1].split("?")[0]
        except: pass
    elif "youtu.be/" in url:
        try: video_id = url.split("youtu.be/")[1].split("?")[0]
        except: pass
    if not video_id and "v=" in url:
        try: q = parse_qs(urlparse(url).query); video_id = q["v"][0]
        except: pass

    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

# -----------------------------------------------------------------
# THE 4K/2K FIX IS HERE
# -----------------------------------------------------------------
FORMAT_CODES = {
    # These will now download the TRUE 4K/2K/Best files
    'Best Available': 'bestvideo+bestaudio/best',
    '4K (2160p)': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
    '2K (1440p)': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
    
    # This is your key for the working "Audio Only" fix
    'Audio Only': 'bestaudio[ext=m4a]', 
    
    # These are unchanged and will stay compatible
    '1080p': 'bestvideo[height<=1080][vcodec^=avc]+bestaudio[acodec^=mp4a]/best[height<=1080][vcodec^=avc]',
    '720p': 'bestvideo[height<=720][vcodec^=avc]+bestaudio[acodec^=mp4a]/best[height<=720][vcodec^=avc]',
    '480p': 'bestvideo[height<=480][vcodec^=avc]+bestaudio[acodec^=mp4a]/best[height<=480][vcodec^=avc]',
    '360p': 'bestvideo[height<=360][vcodec^=avc]+bestaudio[acodec^=mp4a]/best[height<=360][vcodec^=avc]',
    '144p': 'bestvideo[height<=144][vcodec^=avc]+bestaudio[acodec^=mp4a]/best[height<=144][vcodec^=avc]'
}

# --- Functions to update the GUI from the download thread ---

def update_progress(percent_float):
    """Updates the progress bar and percentage label."""
    bar['value'] = percent_float
    percent_label.config(text=f"{percent_float:.1f}%")
    root.update_idletasks()

def download_complete():
    """Called when the download finishes successfully."""
    messagebox.showinfo("Success", "Download complete!")
    bar['value'] = 0
    percent_label.config(text="0.0%")
    download_button.config(state="normal") # Re-enable the button

def download_error(error_message):
    """Called if the download fails."""
    messagebox.showerror("Error", f"Download failed:\n{error_message}")
    bar['value'] = 0
    percent_label.config(text="0.0%")
    download_button.config(state="normal") # Re-enable the button

# -----------------------------------------------------------------
# START_DOWNLOAD FUNCTION 
# -----------------------------------------------------------------
def start_download(url, format_code, selected_quality): # selected_quality is the text
    """
    Runs the yt-dlp download in a new thread and captures its output.
    """
    
    # Create the folder if it doesn't exist
    DOWNLOAD_FOLDER = "Azhar Youtube Video Downloader"
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    try:
        # --- STEP 1: Get the video title ---
        get_title_cmd = [
            'yt-dlp',
            '--get-filename', # Get the safe filename
            '-o', '%(title)s', # Only the title
            url
        ]
        title_process = subprocess.run(get_title_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        title = title_process.stdout.strip()
        
        if not title:
            root.after(0, download_error, "Could not get video title.")
            return

        # --- STEP 2: Find a unique filename ---
        ext = '.m4a' if selected_quality == 'Audio Only' else '.mp4'
        
        # Get a clean tag from the dropdown
        quality_tag = selected_quality.split(" ")[0] 
        if selected_quality == 'Audio Only':
            quality_tag = 'Audio'
        if selected_quality == 'Best Available':
            base_name = title
        else:
            base_name = f"{title} [{quality_tag}]"

        filename_part = f"{base_name}{ext}" 

        # This is the full path to the file
        full_path_to_use = os.path.join(DOWNLOAD_FOLDER, filename_part)

        counter = 1
        # Keep checking for "Video [1080p] (1).mp4", etc.
        while os.path.exists(full_path_to_use):
            filename_part = f"{base_name} ({counter}){ext}"
            full_path_to_use = os.path.join(DOWNLOAD_FOLDER, filename_part)
            counter += 1
        
        # 'full_path_to_use' is now a unique name inside the folder

        # --- STEP 3: Build the final download command ---
        
        # Check by the *name* in the dropdown for the audio fix
        if selected_quality == 'Audio Only':
            command = [
                'yt-dlp',
                '-f', 'bestaudio[ext=m4a]/bestaudio', # Get best m4a
                '-o', full_path_to_use, # <-- Use the unique full path
                url
            ]
        else:
            # This is the default command for all video
            command = [
                'yt-dlp',
                '-f', format_code,
                '--merge-output-format', 'mp4',
                '-o', full_path_to_use, # <-- Use the unique full path
                url
            ]
        
        # --- STEP 4: Run the download ---
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Combine stdout and stderr
            universal_newlines=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line) # Store all output
            
            match = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)

            if match:
                percent_str = match.group(1)
                try:
                    percent_float = float(percent_str)
                    root.after(0, update_progress, percent_float)
                except ValueError:
                    pass

        process.wait()
        
        full_output = "".join(output_lines)
        
        # Check for FFmpeg "not found" warning
        if "WARNING: FFmpeg not found" in full_output and "Audio Only" not in selected_quality:
             root.after(0, download_error, "FFmpeg not found!\n\nyt-dlp cannot find ffmpeg.exe to merge the files.\n\nPlease place your new ffmpeg.exe in the same folder as this script.")
             return

        if process.returncode == 0:
            root.after(0, download_complete)
        else:
            error_match = re.search(r'ERROR:(.*)', full_output, re.DOTALL)
            if error_match:
                error_message = error_match.group(1).strip()
                # Check for the FFmpeg "old" error
                if "could not find codec parameters" in error_message:
                    root.after(0, download_error, "FFmpeg is too old!\n\nYour FFmpeg cannot read the 4K video file.\n\nPlease place a new ffmpeg.exe in the same folder as this script.")
                else:
                    root.after(0, download_error, f"yt-dlp error:\n{error_message}")
            else:
                root.after(0, download_error, "Process returned an error.\nCheck URL or try updating yt-dlp.")
            
    except FileNotFoundError:
        root.after(0, download_error, "yt-dlp not found!\nPlease run: pip install yt-dlp")
    except Exception as e:
        root.after(0, download_error, str(e))

# --- Main Download Button Function ---
def on_download():
    """
    Called when the user clicks the "DOWNLOAD" button.
    """
    raw = url_var.get().strip()
    if not raw:
        messagebox.showerror("Error", "Please enter a YouTube URL!")
        return
    
    clean_url = to_watch_url(raw)
    selected_quality = quality_var.get() # <-- Get the name (e.g. "1080p")
    
    if selected_quality not in FORMAT_CODES:
        messagebox.showerror("Error", "Please select a valid quality.")
        return
        
    format_code = FORMAT_CODES[selected_quality]
    
    download_button.config(state="disabled")
    bar['value'] = 0
    percent_label.config(text="0.0%")
    
    download_thread = threading.Thread(
        target=start_download,
        args=(clean_url, format_code, selected_quality), # <-- Pass name to thread
        daemon=True
    )
    download_thread.start()

# ---------------------- UI ---------------------- #
root = Tk()
root.title("Azhar YouTube Video Downloader")
root.geometry("500x400")
root.resizable(0, 0)

Label(root, text="YouTube Video Downloader", font="arial 20 bold").pack(pady=10)
Label(root, text="Paste YouTube Link Here:", font="arial 15 bold").place(x=120, y=60)

url_var = StringVar()
Entry(root, width=70, textvariable=url_var).place(x=32, y=90)

# --- Quality Dropdown ---
Label(root, text="Select Quality:", font="arial 15 bold").place(x=180, y=130)
quality_var = StringVar()
quality_dropdown = ttk.Combobox(
    root,
    textvariable=quality_var,
    width=20,
    font="arial 12",
    state="readonly"
)
quality_dropdown['values'] = list(FORMAT_CODES.keys())
quality_dropdown.current(0) # Set default to 'Best Available'
quality_dropdown.place(x=150, y=170)

# --- Download Button ---
download_button = Button(
    root,
    text="DOWNLOAD",
    font="arial 15 bold",
    bg="pale violet red",
    padx=2,
    command=on_download
)
download_button.place(x=180, y=220)

# --- Progress Bar (Green) ---
style = ttk.Style()
style.configure("green.Horizontal.TProgressbar",
                troughcolor='gray',
                background='green')

bar = ttk.Progressbar(
    root,
    orient=HORIZONTAL,
    length=400,
    mode="determinate",
    style="green.Horizontal.TProgressbar"
)
bar.place(x=50, y=290)

# --- Percentage Label ---
percent_label = Label(root, text="0.0%", font="arial 12 bold")
percent_label.place(x=220, y=320)

root.mainloop()