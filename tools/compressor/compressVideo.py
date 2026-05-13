import os
import subprocess
from pathlib import Path

# ==========================
# CONFIG
# ==========================
FFMPEG_PATH = r"C:\Users\hdoghmen\Downloads\d00\ffmpeg_master\bin\ffmpeg.exe"   # <-- update
#$FFMPEG = "C:\Users\hdoghmen\Downloads\d00\ffmpeg_master\bin\ffmpeg.exe"


INPUT_DIR = r"F:\_WAY\SAID"           # <-- update
OUTPUT_DIR = r"F:\_WAY\SAID\CONVERTED"         # <-- update

# Compression settings
VIDEO_CRF = "28"     # lower = better quality (23–30 typical)
AUDIO_BITRATE = "128k"

# ==========================
# FUNCTIONS
# ==========================
def run_ffmpeg(cmd):
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")

def process_file(input_path, output_base):
    # Ensure output directory exists
    os.makedirs(output_base.parent, exist_ok=True)

    # 1) Compress video
    compressed_video = output_base.with_suffix(".mp4")
    cmd_video = [
        FFMPEG_PATH,
        "-i", str(input_path),
        "-vcodec", "libx264",
        "-crf", VIDEO_CRF,
        "-preset", "fast",
        "-acodec", "aac",
        "-b:a", AUDIO_BITRATE,
        str(compressed_video)
    ]
    run_ffmpeg(cmd_video)

    # 2) Extract audio (MP3)
    audio_file = output_base.with_suffix(".mp3")
    cmd_audio = [
        FFMPEG_PATH,
        "-i", str(input_path),
        "-vn",
        "-acodec", "libmp3lame",
        "-ab", AUDIO_BITRATE,
        str(audio_file)
    ]
    run_ffmpeg(cmd_audio)

def scan_and_process(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    for file_path in input_dir.rglob("*.mp4"):
        relative_path = file_path.relative_to(input_dir)
        output_base = output_dir / relative_path.with_suffix("")
        
        print(f"Processing: {file_path}")
        process_file(file_path, output_base)

# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    scan_and_process(INPUT_DIR, OUTPUT_DIR)