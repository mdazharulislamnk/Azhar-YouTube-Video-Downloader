import subprocess
from tkinter import *
from tkinter import ttk, messagebox
from urllib.parse import urlparse, parse_qs

def to_watch_url(url: str) -> str:
    """
    Normalizes any YouTube link to a clean 'watch?v=' URL.
    This is still good practice.
    """
    if "/shorts/" in url:
        vid = url.split("/shorts/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={vid}"
    if "watch?" in url and "v=" in url:
        q = parse_qs(urlparse(url).query)
        if "v" in q and q["v"]:
            return f"https://www.youtube.com/watch?v={q['v'][0]}"
    return url

# ---------------------- UI ---------------------- #
root = Tk()
root.title("Azhar YouTube Video Downloader")
root.geometry("500x300"); root.resizable(0, 0) # Made window smaller

Label(root, text="YouTube Video Downloader", font="arial 20 bold").pack(pady=10)
Label(root, text="Paste YouTube Link Here:", font="arial 15 bold").place(x=120, y=60)

url_var = StringVar()
Entry(root, width=70, textvariable=url_var).place(x=32, y=90)

# -----------------------------------------------------------------
# UPDATED DOWNLOAD FUNCTION
# -----------------------------------------------------------------
def on_download():
    raw = url_var.get().strip()
    if not raw:
        messagebox.showerror("Error", "Please enter a YouTube URL!")
        return

    clean_url = to_watch_url(raw)
    
    messagebox.showinfo("Downloading", "Download started.\nThe app will freeze until the download is complete. This is normal.")
    
    try:
        # --- THIS COMMAND IS THE FIX ---
        # We now force yt-dlp to find an 'h264' (avc) video and 'aac' (mp4a) audio.
        # This is the most compatible format for FFmpeg and MP4 files.
        command = [
            'yt-dlp',
            '-f', 'bestvideo[vcodec^=avc]+bestaudio[acodec^=mp4a]/best[vcodec^=avc]/best',
            '--merge-output-format', 'mp4',
            clean_url
        ]
        
        # Run the command.
        subprocess.run(
            command,
            check=True,  # This will raise an error if yt-dlp fails
        )
        
        messagebox.showinfo("Success", "Download complete!")

    except FileNotFoundError:
        messagebox.showerror("Error", "yt-dlp not found!\nPlease run: pip install yt-dlp")
    except Exception as e:
        messagebox.showerror("Error", f"Download failed.\n\nError: {e}")

# -----------------------------------------------------------------

Button(root, text="DOWNLOAD", font="arial 15 bold", bg="pale violet red", padx=2, command=on_download).place(x=180, y=150)
root.mainloop()