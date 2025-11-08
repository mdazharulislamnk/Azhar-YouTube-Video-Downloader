import subprocess
import threading
import re
import os
from tkinter import *
from tkinter import ttk, messagebox
from urllib.parse import urlparse, parse_qs

def to_watch_url(url: str) -> str:
    video_id = None
    if "watch?" in url:
        try:
            q = parse_qs(urlparse(url).query); video_id = q["v"][0]
        except:
            pass
    elif "/shorts/" in url:
        try:
            video_id = url.split("/shorts/")[1].split("?")[0]
        except:
            pass
    elif "youtu.be/" in url:
        try:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        except:
            pass
    if not video_id and "v=" in url:
        try:
            q = parse_qs(urlparse(url).query); video_id = q["v"][0]
        except:
            pass
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else url

FORMAT_CODES = {
    'Best Available': 'bestvideo+bestaudio/best',
    '4K (2160p)': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
    '2K (1440p)': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
    'Audio Only': 'bestaudio[ext=m4a]',
    '1080p': 'bestvideo[height<=1080][vcodec^=avc]+bestaudio[acodec^=mp4a]/best[height<=1080][vcodec^=avc]',
    '720p': 'bestvideo[height<=720][vcodec^=avc]+bestaudio[acodec^=mp4a]/best[height<=720][vcodec^=avc]',
    '480p': 'bestvideo[height<=480][vcodec^=avc]+bestaudio[acodec^=mp4a]/best[height<=480][vcodec^=avc]',
    '360p': 'bestvideo[height<=360][vcodec^=avc]+bestaudio[acodec^=mp4a]/best[height<=360][vcodec^=avc]',
    '144p': 'bestvideo[height<=144][vcodec^=avc]+bestaudio[acodec^=mp4a]/best[height<=144][vcodec^=avc]'
}

# ---------------------- UI ---------------------- #
root = Tk()
root.title("Azhar YouTube Video Downloader")

# size you want
WIN_W, WIN_H = 1080, 720

# center it on the primary display
root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
x = (screen_w // 2) - (WIN_W // 2)
y = (screen_h // 2) - (WIN_H // 2)
root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

# allow width resize, lock height
root.resizable(True, False)

# --------- Architectural theme (dark + gradient + ttk styles) ---------
bg = Canvas(root, width=WIN_W, height=WIN_H, highlightthickness=0, bd=0)
bg.place(x=0, y=0)

def draw_vertical_gradient(cvs, w, h, start="#0f172a", end="#1e293b", steps=256):
    r1,g1,b1 = root.winfo_rgb(start)
    r2,g2,b2 = root.winfo_rgb(end)
    for i in range(steps):
        nr = (r1 + (r2 - r1) * i // steps) >> 8
        ng = (g1 + (g2 - g1) * i // steps) >> 8
        nb = (b1 + (b2 - b1) * i // steps) >> 8
        color = f"#{nr:02x}{ng:02x}{nb:02x}"
        y0 = int(i * (h / steps))
        cvs.create_rectangle(0, y0, w, y0 + int(h/steps) + 1, outline="", fill=color)

draw_vertical_gradient(bg, WIN_W, WIN_H)
root.configure(bg="#0f172a")

style = ttk.Style()
style.theme_use("clam")
ACCENT = "#22c55e"
FG = "#e5e7eb"
SUBFG = "#cbd5e1"

style.configure("TEntry", fieldbackground="#0b1220", foreground=FG, bordercolor="#1f2937")
style.map("TEntry", fieldbackground=[("focus", "#0b1220")])
style.configure("TCombobox", fieldbackground="#0b1220", foreground=FG, bordercolor="#1f2937", arrowcolor=FG)
style.map("TCombobox", fieldbackground=[("focus", "#0b1220")], foreground=[("disabled", SUBFG)])
style.configure("Accent.Horizontal.TProgressbar", troughcolor="#0b1220", background=ACCENT, bordercolor="#0b1220")

label_kwargs = dict(bg="#0f172a", fg=FG)

Label(root, text="Azhar YouTube Video Downloader", font="arial 20 bold", **label_kwargs).pack(pady=5)
Label(root, text="Paste YouTube Link Here:", font="arial 15 bold", **label_kwargs).place(x=420, y=60)

url_var = StringVar()
ttk.Entry(root, width=100, textvariable=url_var).place(x=235, y=90)

Label(root, text="Select Quality:", font="arial 15 bold", **label_kwargs).place(x=480, y=130)
quality_var = StringVar()
quality_dropdown = ttk.Combobox(root, textvariable=quality_var, width=22, font="arial 12", state="readonly")
quality_dropdown['values'] = list(FORMAT_CODES.keys())
quality_dropdown.current(0)
quality_dropdown.place(x=445, y=170)

bar = ttk.Progressbar(root, orient=HORIZONTAL, length=480, mode="determinate", style="Accent.Horizontal.TProgressbar")
bar.place(x=310, y=420)

percent_label = Label(root, text="0.0%", font="arial 12 bold", **label_kwargs)
percent_label.place(x=540, y=450)

# Info card (fixed bg color)
card = Canvas(root, width=860, height=180, bg="#0f172a", highlightthickness=0, bd=0)
card.place(x=110, y=490)
card.create_rectangle(0, 0, 860, 180, fill="#111827", outline="#1f2937", width=1)


info_y = 500
Label(root, text="Status:", font="arial 12 bold", **label_kwargs).place(x=120, y=info_y)
status_value_label = Label(root, text="Idle", font="arial 12", **label_kwargs); status_value_label.place(x=250, y=info_y)

Label(root, text="Filename:", font="arial 12 bold", **label_kwargs).place(x=120, y=info_y+30)
filename_value_label = Label(root, text="-", font="arial 12", wraplength=680, justify=LEFT, **label_kwargs)
filename_value_label.place(x=250, y=info_y+30)

Label(root, text="Total Size:", font="arial 12 bold", **label_kwargs).place(x=120, y=info_y+60)
total_value_label = Label(root, text="-", font="arial 12", **label_kwargs); total_value_label.place(x=250, y=info_y+60)

Label(root, text="Downloaded:", font="arial 12 bold", **label_kwargs).place(x=120, y=info_y+90)
downloaded_value_label = Label(root, text="-", font="arial 12", **label_kwargs); downloaded_value_label.place(x=250, y=info_y+90)

Label(root, text="Speed:", font="arial 12 bold", **label_kwargs).place(x=120, y=info_y+120)
speed_value_label = Label(root, text="-", font="arial 12", **label_kwargs); speed_value_label.place(x=250, y=info_y+120)

def set_status(t): status_value_label.config(text=t); root.update_idletasks()
def set_filename(t): filename_value_label.config(text=t); root.update_idletasks()
def set_total(t): total_value_label.config(text=t); root.update_idletasks()
def set_downloaded(t): downloaded_value_label.config(text=t); root.update_idletasks()
def set_speed(t): speed_value_label.config(text=t); root.update_idletasks()

def reset_progress_ui():
    bar['value'] = 0
    percent_label.config(text="0.0%")
    set_status("Idle")
    set_filename("-")
    set_total("-")
    set_downloaded("-")
    set_speed("-")

def update_progress(percent_float):
    bar['value'] = percent_float
    percent_label.config(text=f"{percent_float:.1f}%")
    root.update_idletasks()

def download_complete():
    messagebox.showinfo("Success", "Download complete!")
    reset_progress_ui()
    download_button.config(state="normal")
    resume_button.config(state="disabled")

def download_error(error_message):
    messagebox.showerror("Error", f"Download failed:\n{error_message}")
    reset_progress_ui()
    download_button.config(state="normal")
    resume_button.config(state="disabled")

# ---------- resume/pause/cancel state ----------
current_process = None
current_part_path = None
current_full_output_path = None
current_command = None
stop_requested = False
cancel_requested = False

# Track stream type to show only video stats
current_stream = "unknown"   # "video" | "audio" | "unknown"
last_video_tot = "-"
last_video_done = "-"
last_video_speed = "-"

progress_re = re.compile(
    r'\[download\]\s+(?:(?P<pct>\d+(?:\.\d+)?)%\s+of\s+(?P<tot1>[\d\.]+[KMG]?i?B)|(?P<done>[\d\.]+[KMG]?i?B)\s+of\s+(?P<tot2>[\d\.]+[KMG]?i?B))\s+at\s+(?P<speed>[\d\.]+[KMG]?i?B/s).*?(?:ETA\s+(?P<eta>\S+))?',
    re.IGNORECASE
)
complete_line_re = re.compile(
    r'\[download\]\s+(?P<pct>\d+(?:\.\d+)?)%\s+of\s+(?P<tot>[\d\.]+[KMG]?i?B)\s+in\s+(?P<time>\S+)',
    re.IGNORECASE
)

def on_stop():
    global stop_requested, cancel_requested
    stop_requested = True
    cancel_requested = False
    if current_process and current_process.poll() is None:
        try:
            current_process.terminate()
        except Exception:
            try:
                current_process.kill()
            except Exception:
                pass
    set_status("Paused (partial kept)")
    resume_button.config(state="normal")
    download_button.config(state="normal")

def on_cancel():
    global stop_requested, cancel_requested
    stop_requested = False
    cancel_requested = True
    if current_process and current_process.poll() is None:
        try:
            current_process.terminate()
        except Exception:
            try:
                current_process.kill()
            except Exception:
                pass
    if current_part_path and os.path.exists(current_part_path):
        try:
            os.remove(current_part_path)
        except Exception:
            pass
    reset_progress_ui()
    download_button.config(state="normal")
    resume_button.config(state="disabled")

def on_start_resume():
    if current_command and current_part_path and os.path.exists(current_part_path):
        set_status("Resuming")
        resume_button.config(state="disabled")
        download_button.config(state="disabled")
        def _resume():
            global current_process, stop_requested, cancel_requested, current_stream, last_video_tot, last_video_done, last_video_speed
            stop_requested = False
            cancel_requested = False
            current_stream = "unknown"
            try:
                proc = subprocess.Popen(
                    current_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                globals()['current_process'] = proc
                output_lines = []
                for line in proc.stdout:
                    output_lines.append(line)

                    if line.startswith("[download] Destination:"):
                        try:
                            dest = line.split("Destination:", 1)[1].strip()
                            globals()['current_part_path'] = dest + ".part"
                            if quality_var.get() == "Audio Only" or dest.lower().endswith((".mp4",".mkv",".mov")) or any(h in dest for h in ["2160","1440","1080","720","480","360","240","144"]):
                                root.after(0, set_filename, os.path.basename(dest))
                            low = dest.lower()
                            if low.endswith((".m4a",)) or ".f251" in low or "audio" in low:
                                current_stream = "audio"
                            else:
                                current_stream = "video"
                        except Exception:
                            pass

                    m_pct = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
                    if m_pct:
                        if quality_var.get() == "Audio Only" or current_stream == "video":
                            try: root.after(0, update_progress, float(m_pct.group(1)))
                            except ValueError: pass

                    m = progress_re.search(line)
                    if m:
                        pct = m.group('pct')
                        tot = m.group('tot1') or m.group('tot2') or '-'
                        done = m.group('done') or (pct and pct + '%') or '-'
                        spd = m.group('speed') or '-'
                        if quality_var.get() == "Audio Only" or current_stream == "video":
                            downloaded_text = f"{done} of {tot}" if 'of' not in str(done) else done
                            root.after(0, set_status, "Downloading")
                            root.after(0, set_total, tot)
                            root.after(0, set_downloaded, downloaded_text)
                            root.after(0, set_speed, spd)
                            if current_stream == "video":
                                last_video_tot = tot
                                last_video_done = downloaded_text
                                last_video_speed = spd
                    else:
                        mc = complete_line_re.search(line)
                        if mc:
                            tot = mc.group('tot')
                            if quality_var.get() == "Audio Only" or current_stream == "video":
                                root.after(0, set_total, tot)
                                root.after(0, set_downloaded, f"{tot} of {tot}")
                                root.after(0, set_speed, "-")
                                if current_stream == "video":
                                    last_video_tot = tot
                                    last_video_done = f"{tot} of {tot}"
                                    last_video_speed = "-"

                    if line.startswith("[Merger]") or "Merging formats" in line:
                        if quality_var.get() != "Audio Only":
                            root.after(0, set_total, last_video_tot or "-")
                            root.after(0, set_downloaded, last_video_done or "-")
                            root.after(0, set_speed, last_video_speed or "-")

                    if stop_requested or cancel_requested:
                        break

                proc.wait()
                full_output = "".join(output_lines)

                if stop_requested:
                    root.after(0, set_status, "Paused (partial kept)")
                    root.after(0, download_button.config, {'state': 'normal'})
                    root.after(0, resume_button.config, {'state': 'normal'})
                    return

                if cancel_requested:
                    if globals()['current_part_path'] and os.path.exists(globals()['current_part_path']):
                        try: os.remove(globals()['current_part_path'])
                        except Exception: pass
                    root.after(0, reset_progress_ui)
                    root.after(0, download_button.config, {'state': 'normal'})
                    root.after(0, resume_button.config, {'state': 'disabled'})
                    return

                if "WARNING: FFmpeg not found" in full_output:
                    root.after(0, download_error, "FFmpeg not found!\nPlace ffmpeg.exe next to this script.")
                    return

                if proc.returncode == 0:
                    root.after(0, set_status, "Completed")
                    root.after(0, download_complete)
                else:
                    error_match = re.search(r'ERROR:(.*)', full_output, re.DOTALL)
                    if error_match:
                        root.after(0, download_error, f"yt-dlp error:\n{error_match.group(1).strip()}")
                    else:
                        root.after(0, download_error, "Process returned an error.\nTry updating yt-dlp.")
            except FileNotFoundError:
                root.after(0, download_error, "yt-dlp not found!\nPlease run: pip install yt-dlp")
            except Exception as e:
                root.after(0, download_error, str(e))
            finally:
                root.after(0, download_button.config, {'state': 'normal'})
        threading.Thread(target=_resume, daemon=True).start()
    else:
        pass

# -----------------------------------------------------------------
# START_DOWNLOAD FUNCTION (records command/path for resume)
# -----------------------------------------------------------------
def start_download(url, format_code, selected_quality):
    DOWNLOAD_FOLDER = "Azhar Youtube Video Downloader"
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    def worker():
        global current_process, current_part_path, current_full_output_path, current_command, stop_requested, cancel_requested, current_stream, last_video_tot, last_video_done, last_video_speed
        stop_requested = False
        cancel_requested = False
        current_process = None
        current_part_path = None
        current_full_output_path = None
        current_command = None
        current_stream = "unknown"
        last_video_tot = "-"
        last_video_done = "-"
        last_video_speed = "-"

        try:
            get_title_cmd = ['yt-dlp', '--get-filename', '-o', '%(title)s', url]
            title_process = subprocess.run(get_title_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            title = title_process.stdout.strip()
            if not title:
                root.after(0, download_error, "Could not get video title.")
                return

            ext = '.m4a' if selected_quality == 'Audio Only' else '.mp4'
            quality_tag = selected_quality.split(" ")[0]
            if selected_quality == 'Audio Only': quality_tag = 'Audio'
            base_name = title if selected_quality == 'Best Available' else f"{title} [{quality_tag}]"

            filename_part = f"{base_name}{ext}"
            full_path_to_use = os.path.join(DOWNLOAD_FOLDER, filename_part)
            counter = 1
            while os.path.exists(full_path_to_use):
                filename_part = f"{base_name} ({counter}){ext}"
                full_path_to_use = os.path.join(DOWNLOAD_FOLDER, filename_part)
                counter += 1

            root.after(0, set_filename, filename_part)

            if selected_quality == 'Audio Only':
                command = ['yt-dlp', '-f', 'bestaudio[ext=m4a]/bestaudio', '-o', full_path_to_use, url]
            else:
                command = ['yt-dlp', '-f', format_code, '--merge-output-format', 'mp4', '-o', full_path_to_use, url]

            globals()['current_full_output_path'] = full_path_to_use
            globals()['current_command'] = command

            set_status("Starting")
            set_total("-"); set_downloaded("-"); set_speed("-")

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='ignore'
            )
            globals()['current_process'] = process
            globals()['current_part_path'] = full_path_to_use + ".part"

            output_lines = []
            for line in process.stdout:
                output_lines.append(line)

                if line.startswith("[download] Destination:"):
                    try:
                        dest = line.split("Destination:", 1)[1].strip()
                        globals()['current_part_path'] = dest + ".part"
                        if selected_quality == "Audio Only" or dest.lower().endswith((".mp4",".mkv",".mov")) or any(h in dest for h in ["2160","1440","1080","720","480","360","240","144"]):
                            root.after(0, set_filename, os.path.basename(dest))
                        low = dest.lower()
                        if low.endswith((".m4a",)) or ".f251" in low or "audio" in low:
                            current_stream = "audio"
                        else:
                            current_stream = "video" if selected_quality != "Audio Only" else "audio"
                    except Exception:
                        pass

                m_pct = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
                if m_pct:
                    if selected_quality == "Audio Only" or current_stream == "video":
                        try: root.after(0, update_progress, float(m_pct.group(1)))
                        except ValueError: pass

                m = progress_re.search(line)
                if m:
                    pct = m.group('pct')
                    tot = m.group('tot1') or m.group('tot2') or '-'
                    done = m.group('done') or (pct and pct + '%') or '-'
                    spd = m.group('speed') or '-'
                    if selected_quality == "Audio Only" or current_stream == "video":
                        downloaded_text = f"{done} of {tot}" if 'of' not in str(done) else done
                        root.after(0, set_status, "Downloading")
                        root.after(0, set_total, tot)
                        root.after(0, set_downloaded, downloaded_text)
                        root.after(0, set_speed, spd)
                        if current_stream == "video":
                            last_video_tot = tot
                            last_video_done = downloaded_text
                            last_video_speed = spd
                else:
                    mc = complete_line_re.search(line)
                    if mc:
                        tot = mc.group('tot')
                        if selected_quality == "Audio Only" or current_stream == "video":
                            root.after(0, set_total, tot)
                            root.after(0, set_downloaded, f"{tot} of {tot}")
                            root.after(0, set_speed, "-")
                            if current_stream == "video":
                                last_video_tot = tot
                                last_video_done = f"{tot} of {tot}"
                                last_video_speed = "-"

                if line.startswith("[Merger]") or "Merging formats" in line:
                    if selected_quality != "Audio Only":
                        root.after(0, set_total, last_video_tot or "-")
                        root.after(0, set_downloaded, last_video_done or "-")
                        root.after(0, set_speed, last_video_speed or "-")

                if stop_requested or cancel_requested:
                    break

            process.wait()
            full_output = "".join(output_lines)

            if "WARNING: FFmpeg not found" in full_output and "Audio Only" not in selected_quality:
                root.after(0, download_error, "FFmpeg not found!\n\nyt-dlp cannot find ffmpeg.exe to merge the files.\n\nPlease place your new ffmpeg.exe in the same folder as this script.")
                return

            if stop_requested:
                root.after(0, set_status, "Paused (partial kept)")
                root.after(0, download_button.config, {'state': 'normal'})
                root.after(0, resume_button.config, {'state': 'normal'})
                return

            if cancel_requested:
                if globals()['current_part_path'] and os.path.exists(globals()['current_part_path']):
                    try: os.remove(globals()['current_part_path'])
                    except Exception: pass
                root.after(0, reset_progress_ui)
                root.after(0, download_button.config, {'state': 'normal'})
                root.after(0, resume_button.config, {'state': 'disabled'})
                return

            if process.returncode == 0:
                root.after(0, set_status, "Completed")
                root.after(0, download_complete)
            else:
                error_match = re.search(r'ERROR:(.*)', full_output, re.DOTALL)
                if error_match:
                    error_message = error_match.group(1).strip()
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
        finally:
            root.after(0, download_button.config, {'state': 'normal'})

    threading.Thread(target=worker, daemon=True).start()

# --- Main Download Button Function ---
def on_download():
    raw = url_var.get().strip()
    if not raw:
        messagebox.showerror("Error", "Please enter a YouTube URL!")
        return
    clean_url = to_watch_url(raw)
    selected_quality = quality_var.get()
    if selected_quality not in FORMAT_CODES:
        messagebox.showerror("Error", "Please select a valid quality.")
        return
    format_code = FORMAT_CODES[selected_quality]
    download_button.config(state="disabled")
    resume_button.config(state="disabled")
    bar['value'] = 0
    percent_label.config(text="0.0%")
    set_status("Queued")
    threading.Thread(target=start_download, args=(clean_url, format_code, selected_quality), daemon=True).start()

# --- Buttons (moved right; Resume above Pause) ---
def style_button(btn, bg):
    btn.configure(bg=bg, fg="#0b1220", activebackground=bg, activeforeground="#0b1220", bd=0, relief="flat", cursor="hand2")

download_button = Button(root, text="DOWNLOAD", font="arial 15 bold", padx=10, command=on_download)
download_button.place(x=485, y=350)
style_button(download_button, "#e879f9")

controls_x = 880
resume_button = Button(root, text="Resume", font="arial 12 bold", state="disabled", command=on_start_resume)
resume_button.place(x=controls_x, y=500)
style_button(resume_button, "#22c55e")

pause_button = Button(root, text="Pause", font="arial 12 bold", command=on_stop)
pause_button.place(x=controls_x+10, y=560)
style_button(pause_button,  "#f59e0b")

cancel_button = Button(root, text="Cancel", font="arial 12 bold", command=on_cancel)
cancel_button.place(x=controls_x+10, y=620)
style_button(cancel_button, "#ef4444")

try:
    root.iconbitmap("azhar.ico")
except Exception:
    pass

root.mainloop()
