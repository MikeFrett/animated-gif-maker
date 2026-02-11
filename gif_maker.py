import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import cv2
import threading
import time
import os

MAX_DURATION = 10.0
GIF_FPS = 12
EXPORT_WIDTH = 480


def get_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Helvetica.ttc"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()


class GifMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Animated GIF Maker")
        self.root.geometry("720x640")

        self.cap = None
        self.fps = 0
        self.total_frames = 0

        self.playing = False
        self.exporting = False
        self.last_slider = "start"

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- UI ----------
    def build_ui(self):
        tk.Button(
            self.root,
            text="Load Video",
            command=self.load_video,
            bg="lightblue",
            font=("Arial", 12)
        ).pack(pady=8)

        self.canvas = tk.Canvas(
            self.root,
            width=400,
            height=300,
            bg="black",
            relief=tk.SUNKEN,
            bd=2
        )
        self.canvas.pack()

        self.duration_label = tk.Label(self.root, text="Duration: 0.00s")
        self.duration_label.pack(pady=4)

        timeline = tk.Frame(self.root)
        timeline.pack(pady=6)

        self.start_var = tk.DoubleVar(value=0)
        self.end_var = tk.DoubleVar(value=0)

        tk.Label(timeline, text="Start (s)").grid(row=0, column=0)
        tk.Label(timeline, text="End (s)").grid(row=0, column=1)

        self.start_slider = tk.Scale(
            timeline,
            orient=tk.HORIZONTAL,
            length=260,
            resolution=0.01,
            variable=self.start_var,
            command=self.on_start_move
        )
        self.start_slider.grid(row=1, column=0, padx=10)

        self.end_slider = tk.Scale(
            timeline,
            orient=tk.HORIZONTAL,
            length=260,
            resolution=0.01,
            variable=self.end_var,
            command=self.on_end_move
        )
        self.end_slider.grid(row=1, column=1, padx=10)

        # ---------- Text controls ----------
        text_row = tk.Frame(self.root)
        text_row.pack(pady=10)

        tk.Label(text_row, text="Text").grid(
            row=0, column=0, padx=(0, 4), sticky="e"
        )

        self.text_var = tk.StringVar(value="TEXT HERE")
        tk.Entry(
            text_row,
            textvariable=self.text_var,
            width=22
        ).grid(row=0, column=1, padx=(0, 12))

        self.text_var.trace_add("write", lambda *args: self.update_preview())

        tk.Label(text_row, text="Font Size").grid(
            row=0, column=2, padx=(0, 4), sticky="e"
        )

        self.size_var = tk.IntVar(value=28)
        tk.Scale(
            text_row,
            from_=12,
            to=72,
            length=100,
            orient=tk.HORIZONTAL,
            variable=self.size_var,
            command=lambda e: self.update_preview()
        ).grid(row=0, column=3, padx=(0, 12))

        tk.Label(text_row, text="Text Vertical").grid(
            row=0, column=4, padx=(0, 4), sticky="e"
        )

        self.pos_var = tk.DoubleVar(value=0.85)
        tk.Scale(
            text_row,
            from_=0.05,
            to=0.95,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            length=120,
            variable=self.pos_var,
            command=lambda e: self.update_preview()
        ).grid(row=0, column=5)

        # ---------- Buttons ----------
        buttons = tk.Frame(self.root)
        buttons.pack(pady=8)

        self.play_btn = tk.Button(
            buttons,
            text="Play Trimmed Range",
            command=self.toggle_play,
            bg="yellow"
        )
        self.play_btn.pack(side=tk.LEFT, padx=6)

        self.export_btn = tk.Button(
            buttons,
            text="Export Animated GIF",
            command=self.export_gif,
            bg="green",
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=6)

        self.progress = ttk.Progressbar(
            self.root,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(fill=tk.X, padx=30, pady=10)

    # ---------- Video ----------
    def load_video(self):
        path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if not path:
            return

        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = self.total_frames / self.fps

        self.start_slider.config(from_=0, to=duration)
        self.end_slider.config(from_=0, to=duration)

        self.start_var.set(0)
        self.end_var.set(min(duration, 5))

        self.update_duration()
        self.update_preview()

    def on_start_move(self, _):
        self.last_slider = "start"
        self.update_duration()
        self.update_preview()

    def on_end_move(self, _):
        self.last_slider = "end"
        self.update_duration()
        self.update_preview()

    def update_duration(self):
        dur = max(0.0, self.end_var.get() - self.start_var.get())
        self.duration_label.config(text=f"Duration: {dur:.2f}s")

        if 2 / GIF_FPS <= dur <= MAX_DURATION:
            self.export_btn.config(state=tk.NORMAL)
        else:
            self.export_btn.config(state=tk.DISABLED)

    # ---------- Frames & Text ----------
    def get_frame_by_time(self, t):
        frame_idx = min(int(t * self.fps), self.total_frames - 1)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = self.cap.read()
        if not ok:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def draw_text(self, img):
        txt = self.text_var.get().strip()
        if not txt:
            return img

        w, h = img.size
        font = get_font(self.size_var.get())
        draw = ImageDraw.Draw(img)

        box = draw.textbbox((0, 0), txt, font=font)
        tw = box[2] - box[0]
        th = box[3] - box[1]

        x = max(0, (w - tw) // 2)
        y = int(h * self.pos_var.get() - th / 2)
        y = max(0, min(y, h - th))

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    draw.text((x + dx, y + dy), txt, font=font, fill="black")

        draw.text((x, y), txt, font=font, fill="white")
        return img

    # ---------- Preview ----------
    def update_preview(self):
        if not self.cap:
            return

        t = self.start_var.get() if self.last_slider == "start" else self.end_var.get()
        frame = self.get_frame_by_time(t)
        if frame is None:
            return

        img = Image.fromarray(frame)
        img = self.draw_text(img)
        img.thumbnail((400, 300))

        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(200, 150, image=self.photo)

    # ---------- Playback ----------
    def toggle_play(self):
        if self.playing:
            self.playing = False
            self.play_btn.config(text="Play Trimmed Range")
            return

        self.playing = True
        self.play_btn.config(text="Stop")
        threading.Thread(target=self.play_loop, daemon=True).start()

    def play_loop(self):
        t = self.start_var.get()
        end = self.end_var.get()
        step = 1 / self.fps

        while self.playing and t <= end:
            frame = self.get_frame_by_time(t)
            if frame is None:
                break

            img = Image.fromarray(frame)
            img = self.draw_text(img)
            img.thumbnail((400, 300))

            self.photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(200, 150, image=self.photo)

            time.sleep(step)
            t += step

        self.playing = False
        self.play_btn.config(text="Play Trimmed Range")

    # ---------- Export ----------
    def export_gif(self):
        if self.exporting:
            return

        start = self.start_var.get()
        end = self.end_var.get()
        duration = end - start
        frame_count = int(duration * GIF_FPS)

        if frame_count < 2:
            messagebox.showerror("Error", "Selection too short.")
            return

        out = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF", "*.gif")]
        )
        if not out:
            return

        self.exporting = True
        self.progress["value"] = 0

        def worker():
            frames = []

            for i in range(frame_count):
                t = start + i / GIF_FPS
                frame = self.get_frame_by_time(t)
                if frame is None:
                    continue

                img = Image.fromarray(frame)
                img = self.draw_text(img)
                img = img.resize(
                    (EXPORT_WIDTH, int(img.height * EXPORT_WIDTH / img.width)),
                    Image.LANCZOS
                )
                frames.append(img)

                self.progress["value"] = (i + 1) / frame_count * 100
                self.root.update_idletasks()

            frames[0].save(
                out,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=int(1000 / GIF_FPS),
                loop=0,
                disposal=2
            )

            self.exporting = False
            messagebox.showinfo("Done", "Animated GIF saved successfully.")

        threading.Thread(target=worker, daemon=True).start()

    def on_close(self):
        self.playing = False
        if self.cap:
            self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    GifMaker(root)
    root.mainloop()

