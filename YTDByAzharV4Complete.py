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

WIN_W, WIN_H = 1080, 720
root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
x = (screen_w // 2) - (WIN_W // 2)
y = (screen_h // 2) - (WIN_H // 2)
root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")
root.resizable(True, False)

# Colors / type (lighter theme)
BG = "#0f172a"       # soft navy
SURFACE = "#1e293b"  # mid-navy
CARD = "#223046"     # cool slate
OUTLINE = "#334155"  # slate border
TXT = "#f1f5f9"      # near-white
TXT2 = "#cbd5e1"     # secondary text
ACCENT = "#38bdf8"   # sky blue
SUCCESS = "#22c55e"  # emerald


root.configure(bg=BG)

# Gradient background
bg = Canvas(root, width=WIN_W, height=WIN_H, highlightthickness=0, bd=0)
bg.place(x=0, y=0)

def draw_vertical_gradient(cvs, w, h, start=BG, end=SURFACE, steps=192):
    r1,g1,b1 = root.winfo_rgb(start); r2,g2,b2 = root.winfo_rgb(end)
    cvs.delete("all")
    for i in range(steps):
        nr = (r1 + (r2 - r1) * i // steps) >> 8
        ng = (g1 + (g2 - g1) * i // steps) >> 8
        nb = (b1 + (b2 - b1) * i // steps) >> 8
        color = f"#{nr:02x}{ng:02x}{nb:02x}"
        y0 = int(i * (h / steps))
        cvs.create_rectangle(0, y0, w, y0 + int(h/steps) + 1, outline="", fill=color)

draw_vertical_gradient(bg, WIN_W, WIN_H)

# Animated background hue shift
def animate_bg(step=0):
    schemes = [("#0f172a", "#1e293b"), ("#0e1725", "#182338"), ("#0c1522", "#1a2436")]
    a = (step // 140) % len(schemes)
    start, end = schemes[a]
    draw_vertical_gradient(bg, WIN_W, WIN_H, start=start, end=end, steps=192)
    root.after(60, animate_bg, step + 1)
animate_bg()

# ttk styles
style = ttk.Style()
style.theme_use("clam")
style.configure("TEntry", fieldbackground="#0b1220", foreground=TXT, bordercolor=OUTLINE)
style.map("TEntry", fieldbackground=[("focus", "#0b1220")])
style.configure("TCombobox", fieldbackground="#0b1220", foreground=TXT, bordercolor=OUTLINE, arrowcolor=TXT)
style.map("TCombobox", fieldbackground=[("focus", "#0b1220")], foreground=[("disabled", TXT2)])
style.configure("Accent.Horizontal.TProgressbar", troughcolor="#0b1220", background=SUCCESS, bordercolor="#0b1220")

label_kwargs = dict(bg=BG, fg=TXT)

# Title
Label(root, text="Azhar YouTube Video Downloader", font=("Segoe UI", 24, "bold"), **label_kwargs).pack(pady=8)
Label(root, text="Paste YouTube Link Here:", font=("Segoe UI", 14, "bold"), **label_kwargs).place(x=420, y=60)

# Inputs
url_var = StringVar()
ttk.Entry(root, width=100, textvariable=url_var).place(x=235, y=90)

Label(root, text="Select Quality:", font=("Segoe UI", 14, "bold"), **label_kwargs).place(x=480, y=130)
quality_var = StringVar()
quality_dropdown = ttk.Combobox(root, textvariable=quality_var, width=22, font=("Segoe UI", 11), state="readonly")
quality_dropdown['values'] = list(FORMAT_CODES.keys())
quality_dropdown.current(0)
quality_dropdown.place(x=445, y=170)

# Progress
bar = ttk.Progressbar(root, orient=HORIZONTAL, length=480, mode="determinate", style="Accent.Horizontal.TProgressbar")
bar.place(x=310, y=420)

percent_label = Label(root, text="0.0%", font=("Consolas", 12, "bold"), **label_kwargs)
percent_label.place(x=540, y=450)

# Shimmer overlay for bar
bar_overlay = Canvas(root, width=480, height=6, highlightthickness=0, bd=0, bg=root["bg"])
bar_overlay.place(x=310, y=420+2)
def shimmer(x=0):
    bar_overlay.delete("all")
    for i in range(0, 80, 8):
        shade = 210 - i*2
        c = f"#{shade:02x}{shade:02x}{shade:02x}"
        x0 = (x+i) % 520 - 40
        bar_overlay.create_rectangle(x0, 0, x0+40, 6, outline="", fill=c)
    root.after(60, shimmer, x+10)
shimmer()

# Info card + shadow
shadow = Canvas(root, width=860, height=180, bg=BG, highlightthickness=0, bd=0)
shadow.place(x=110+3, y=490-6)
shadow.create_rectangle(0, 0, 860, 180, fill="#0a0f1c", outline="")

card = Canvas(root, width=860, height=180, bg=BG, highlightthickness=0, bd=0)
card.place(x=110, y=490)
card.create_rectangle(0, 0, 860, 180, fill="#111827", outline="#1f2937", width=1)
card.create_line(16, 60, 844, 60, fill="#1f2937")
card.create_line(16, 120, 844, 120, fill="#1f2937")

info_y = 500
Label(root, text="Status:", font=("Segoe UI", 12, "bold"), bg="#111827", fg=TXT2).place(x=120, y=info_y-10)
status_value_label = Label(root, text="Idle", font=("Segoe UI", 12), bg="#111827", fg=TXT); status_value_label.place(x=250, y=info_y-10)

Label(root, text="Filename:", font=("Segoe UI", 12, "bold"), bg="#111827", fg=TXT2).place(x=120, y=info_y+30)
filename_value_label = Label(root, text="-", font=("Segoe UI", 12), wraplength=680, justify=LEFT, bg="#111827", fg=TXT)
filename_value_label.place(x=250, y=info_y+30)

Label(root, text="Total Size:", font=("Segoe UI", 12, "bold"), bg="#111827", fg=TXT2).place(x=120, y=info_y+70)
total_value_label = Label(root, text="-", font=("Segoe UI", 12), bg="#111827", fg=TXT); total_value_label.place(x=250, y=info_y+70)

Label(root, text="Downloaded:", font=("Segoe UI", 12, "bold"), bg="#111827", fg=TXT2).place(x=120, y=info_y+100)
downloaded_value_label = Label(root, text="-", font=("Segoe UI", 12), bg="#111827", fg=TXT); downloaded_value_label.place(x=250, y=info_y+100)

Label(root, text="Speed:", font=("Segoe UI", 12, "bold"), bg="#111827", fg=TXT2).place(x=120, y=info_y+130)
speed_value_label = Label(root, text="-", font=("Segoe UI", 12), bg="#111827", fg=TXT); speed_value_label.place(x=250, y=info_y+130)

# Buttons
def style_button(btn, bgcol):
    btn.configure(bg=bgcol, fg="#0b1020", activebackground=bgcol, activeforeground="#0b1020",
                  bd=0, relief="flat", cursor="hand2", font=("Segoe UI", 14, "bold"), padx=14, pady=6)

download_button = Button(root, text="DOWNLOAD")
style_button(download_button, ACCENT)
download_button.place(x=470, y=350)

controls_x = 860
resume_button = Button(root, text="Resume", state="disabled")
style_button(resume_button, "#22c55e"); resume_button.place(x=controls_x, y=490)

pause_button = Button(root, text="Pause")
style_button(pause_button, "#f59e0b"); pause_button.place(x=controls_x+15, y=550)

cancel_button = Button(root, text="Cancel")
style_button(cancel_button, "#ef4444"); cancel_button.place(x=controls_x+10, y=610)

# Hover scale + ripple
def add_hover_scale(btn, dy=1):
    def enter(_): btn.place_configure(y=btn.winfo_y()-dy)
    def leave(_): btn.place_configure(y=btn.winfo_y()+dy)
    btn.bind("<Enter>", enter); btn.bind("<Leave>", leave)

def add_ripple(btn, color="#ffffff", duration=120):
    def flash(_):
        orig = btn.cget("bg"); btn.configure(bg=color); root.after(duration, lambda: btn.configure(bg=orig))
    btn.bind("<Button-1>", flash)

for b in (download_button, resume_button, pause_button, cancel_button):
    add_hover_scale(b); add_ripple(b)





# Colored breathing glow with name
glow = Canvas(root, width=240, height=44, highlightthickness=0, bd=0, bg=BG)
glow.place(x=10, y=10)

def pulse(t=0):
    glow.delete("all")

    # Color cycle: red, green, blue, pink
    colors = ["#ef4444", "#22c55e", "#3b82f6", "#ec4899"]
    c = colors[(t // 20) % len(colors)]

    # Breathing brightness 0..1..0
    breath = abs(((t % 40) - 20) / 20)

    # Mix toward white slightly for the peak glow
    def tint(hexcol, factor):
        r = int(hexcol[1:3], 16); g = int(hexcol[3:5], 16); b = int(hexcol[5:7], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    fill_col = tint(c, 0.35 * breath)

    # Draw glowing ellipse
    glow.create_oval(8, 6, 212, 38, outline="", fill=fill_col)

    # Inner highlight (subtle)
    inner = tint(c, 0.6 * breath)
    glow.create_oval(30, 12, 190, 34, outline="", fill=inner)

    # Your name centered on top
    glow.create_text(110, 22, text="Azhar", font=("Segoe UI", 11, "bold"),
                     fill="#ffffff")

    root.after(60, pulse, t + 1)

pulse()







# UI updaters
_current_percent = 0.0
def set_status(t): status_value_label.config(text=t); root.update_idletasks()
def set_filename(t): filename_value_label.config(text=t); root.update_idletasks()
def set_total(t): total_value_label.config(text=t); root.update_idletasks()
def set_downloaded(t): downloaded_value_label.config(text=t); root.update_idletasks()
def set_speed(t): speed_value_label.config(text=t); root.update_idletasks()

def reset_progress_ui():
    global _current_percent
    _current_percent = 0.0
    bar['value'] = 0
    percent_label.config(text="0.0%")
    set_status("Idle"); set_filename("-"); set_total("-"); set_downloaded("-"); set_speed("-")

def update_progress(percent_float):
    global _current_percent
    start = _current_percent; target = percent_float; steps = 8
    def step(i=0):
        global _current_percent
        val = start + (target-start) * (i/steps)
        _current_percent = val
        bar['value'] = val
        percent_label.config(text=f"{val:.1f}%")
        if i < steps: root.after(20, step, i+1)
    step()

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
    stop_requested = True; cancel_requested = False
    if current_process and current_process.poll() is None:
        try: current_process.terminate()
        except Exception:
            try: current_process.kill()
            except Exception: pass
    set_status("Paused (partial kept)")
    resume_button.config(state="normal"); download_button.config(state="normal")

def on_cancel():
    global stop_requested, cancel_requested
    stop_requested = False; cancel_requested = True
    if current_process and current_process.poll() is None:
        try: current_process.terminate()
        except Exception:
            try: current_process.kill()
            except Exception: pass
    if current_part_path and os.path.exists(current_part_path):
        try: os.remove(current_part_path)
        except Exception: pass
    reset_progress_ui(); download_button.config(state="normal"); resume_button.config(state="disabled")

def on_start_resume():
    if current_command and current_part_path and os.path.exists(current_part_path):
        set_status("Resuming")
        resume_button.config(state="disabled"); download_button.config(state="disabled")
        def _resume():
            global current_process, stop_requested, cancel_requested, current_stream
            stop_requested = False; cancel_requested = False; current_stream = "unknown"
            try:
                proc = subprocess.Popen(current_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        universal_newlines=True, encoding='utf-8', errors='ignore')
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
                        except Exception: pass

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
                                globals()['last_video_tot'] = tot
                                globals()['last_video_done'] = downloaded_text
                                globals()['last_video_speed'] = spd
                    else:
                        mc = complete_line_re.search(line)
                        if mc:
                            tot = mc.group('tot')
                            if quality_var.get() == "Audio Only" or current_stream == "video":
                                root.after(0, set_total, tot)
                                root.after(0, set_downloaded, f"{tot} of {tot}")
                                root.after(0, set_speed, "-")
                                if current_stream == "video":
                                    globals()['last_video_tot'] = tot
                                    globals()['last_video_done'] = f"{tot} of {tot}"
                                    globals()['last_video_speed'] = "-"

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

def start_download(url, format_code, selected_quality):
    DOWNLOAD_FOLDER = "Azhar Youtube Video Downloader"
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    def worker():
        global current_process, current_part_path, current_full_output_path, current_command, stop_requested, cancel_requested, current_stream, last_video_tot, last_video_done, last_video_speed
        stop_requested = False; cancel_requested = False
        current_process = None; current_part_path = None
        current_full_output_path = None; current_command = None
        current_stream = "unknown"; last_video_tot = "-"; last_video_done = "-"; last_video_speed = "-"

        try:
            get_title_cmd = ['yt-dlp', '--get-filename', '-o', '%(title)s', url]
            title_process = subprocess.run(get_title_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            title = title_process.stdout.strip()
            if not title:
                root.after(0, download_error, "Could not get video title."); return

            ext = '.m4a' if selected_quality == 'Audio Only' else '.mp4'
            quality_tag = selected_quality.split(" ")[0]
            if selected_quality == 'Audio Only': quality_tag = 'Audio'
            base_name = title if selected_quality == 'Best Available' else f"{title} [{quality_tag}]"
            filename_part = f"{base_name}{ext}"
            full_path_to_use = os.path.join(DOWNLOAD_FOLDER, filename_part)
            counter = 1
            while os.path.exists(full_path_to_use):
                filename_part = f"{base_name} ({counter}){ext}"
                full_path_to_use = os.path.join(DOWNLOAD_FOLDER, filename_part); counter += 1
            root.after(0, set_filename, filename_part)

            if selected_quality == 'Audio Only':
                command = ['yt-dlp', '-f', 'bestaudio[ext=m4a]/bestaudio', '-o', full_path_to_use, url]
            else:
                command = ['yt-dlp', '-f', format_code, '--merge-output-format', 'mp4', '-o', full_path_to_use, url]

            globals()['current_full_output_path'] = full_path_to_use
            globals()['current_command'] = command

            set_status("Starting"); set_total("-"); set_downloaded("-"); set_speed("-")

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       universal_newlines=True, encoding='utf-8', errors='ignore')
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
                    except Exception: pass

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
                            last_video_tot = tot; last_video_done = downloaded_text; last_video_speed = spd
                else:
                    mc = complete_line_re.search(line)
                    if mc:
                        tot = mc.group('tot')
                        if selected_quality == "Audio Only" or current_stream == "video":
                            root.after(0, set_total, tot)
                            root.after(0, set_downloaded, f"{tot} of {tot}")
                            root.after(0, set_speed, "-")
                            if current_stream == "video":
                                last_video_tot = tot; last_video_done = f"{tot} of {tot}"; last_video_speed = "-"

                if line.startswith("[Merger]") or "Merging formats" in line:
                    if selected_quality != "Audio Only":
                        root.after(0, set_total, last_video_tot or "-")
                        root.after(0, set_downloaded, last_video_done or "-")
                        root.after(0, set_speed, last_video_speed or "-")

                if stop_requested or cancel_requested: break

            process.wait()
            full_output = "".join(output_lines)

            if "WARNING: FFmpeg not found" in full_output and selected_quality != "Audio Only":
                root.after(0, download_error, "FFmpeg not found!\n\nyt-dlp cannot find ffmpeg.exe to merge the files.\n\nPlace a new ffmpeg.exe next to this script."); return

            if stop_requested:
                root.after(0, set_status, "Paused (partial kept)")
                root.after(0, download_button.config, {'state': 'normal'})
                root.after(0, resume_button.config, {'state': 'normal'})
                return

            if cancel_requested:
                if current_part_path and os.path.exists(current_part_path):
                    try: os.remove(current_part_path)
                    except Exception: pass
                root.after(0, reset_progress_ui)
                root.after(0, download_button.config, {'state': 'normal'})
                root.after(0, resume_button.config, {'state': 'disabled'})
                return

            if process.returncode == 0:
                root.after(0, set_status, "Completed"); root.after(0, download_complete)
            else:
                error_match = re.search(r'ERROR:(.*)', full_output, re.DOTALL)
                if error_match:
                    err = error_match.group(1).strip()
                    if "could not find codec parameters" in err:
                        root.after(0, download_error, "FFmpeg is too old!\n\nPlace a newer ffmpeg.exe next to this script.")
                    else:
                        root.after(0, download_error, f"yt-dlp error:\n{err}")
                else:
                    root.after(0, download_error, "Process returned an error.\nCheck URL or update yt-dlp.")
        except FileNotFoundError:
            root.after(0, download_error, "yt-dlp not found!\nPlease run: pip install yt-dlp")
        except Exception as e:
            root.after(0, download_error, str(e))
        finally:
            root.after(0, download_button.config, {'state': 'normal'})

    threading.Thread(target=worker, daemon=True).start()

def on_download():
    raw = url_var.get().strip()
    if not raw:
        messagebox.showerror("Error", "Please enter a YouTube URL!"); return
    clean_url = to_watch_url(raw)
    selected_quality = quality_var.get()
    if selected_quality not in FORMAT_CODES:
        messagebox.showerror("Error", "Please select a valid quality."); return
    format_code = FORMAT_CODES[selected_quality]
    download_button.config(state="disabled"); resume_button.config(state="disabled")
    bar['value'] = 0; percent_label.config(text="0.0%"); set_status("Queued")
    threading.Thread(target=start_download, args=(clean_url, format_code, selected_quality), daemon=True).start()

# Wire button commands
download_button.config(command=on_download)
pause_button.config(command=on_stop)
cancel_button.config(command=on_cancel)
resume_button.config(command=on_start_resume)

try: root.iconbitmap("azhar.ico")
except Exception: pass

root.mainloop()
