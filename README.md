# Animated GIF Maker (Python)

A simple cross-platform GUI tool for turning short video clips into animated GIFs with text overlays.

This app is designed as a modern replacement for tools like Gifcurry, with a focus on:
- Visual trimming (start/end sliders)
- Live preview
- Caption text with size and vertical position controls
- Safe GIF export (≤ 10 seconds)
- Run with: python3 gif_maker.py

Built with Python, Tkinter, OpenCV, and Pillow.

---

##Notes

- Very short selections (less than ~2 frames) cannot be exported

- The preview always matches the exported GIF

- Fonts are automatically selected based on your OS

---

## Features

- Load common video formats (mp4, mov, avi, mkv)
- Scrub start and end points visually
- Live preview with text overlay
- White text with black outline (auto-centered)
- Export optimized animated GIFs
- Works on Linux, Windows, and macOS

---

## Requirements

- Python **3.8+**
- ffmpeg installed on your system

### Python libraries
- `opencv-python`
- `Pillow`

---

## Installation

### 1. Install Python dependencies

```bash
pip install opencv-python Pillow
