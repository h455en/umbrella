# -*- coding: utf-8 -*-

import subprocess
from pathlib import Path

# =========================
# CONFIG (OPTIMIZED SPEECH)
# =========================

IN = r"C:\Users\h455n\Downloads\_PIPELINE\IN\AUD\سعيِّد بن هليِّل العُمر\التعليقات الذهبية على كتاب السياسة الشرعية"

EXTENSIONS = {".mp4", ".mp3", ".m4a", ".wav", ".aac", ".mpeg", ".mkv", ".opus"}
CONFIG = {
    "FFMPEG": r"D:\H455N\TAFF\EXE\FFMPEG\bin\ffmpeg.exe",
    "INPUT_DIR": IN,
    "OUTPUT_FOLDER_NAME": "_COMPRESSED",
    "OUTPUT_EXT": ".mp3",

    # Ultra compression for speech
    "MODE": "speech_good",
    # Speech optimization
    "MONO": True,
    "SAMPLE_RATE": 16000, #8k = telephone / 16k recommended (clear Arabic speech) / 22050 → high clarity
    # Bitrate tuned for speech
    "BITRATE": {
        "speech_ultra": "6k",
        "speech_good": "8k",
        "speech_max": "12k"
    },
    # Max compression efficiency
    "COMPRESSION_LEVEL": 7,
    # Silence logs
    "LOGLEVEL": "error"
}
# =========================
# INIT
# =========================
FFMPEG = CONFIG["FFMPEG"]
IN_DIR = Path(CONFIG["INPUT_DIR"])
OUT_DIR = IN_DIR / CONFIG["OUTPUT_FOLDER_NAME"]

if not Path(FFMPEG).exists():
    raise FileNotFoundError(f"FFmpeg not found: {FFMPEG}")

if not IN_DIR.exists():
    raise FileNotFoundError(f"Input folder not found: {IN_DIR}")

OUT_DIR.mkdir(parents=True, exist_ok=True)

files = [f for f in IN_DIR.rglob("*") if f.is_file() and f.suffix.lower() in EXTENSIONS]

print(f"Files detected: {len(files)}")
print(f"Mode: {CONFIG['MODE']}")

# =========================
# PROCESS
# =========================
for i, file in enumerate(files, 1):

    rel = file.relative_to(IN_DIR)
    out_file = (OUT_DIR / rel).with_suffix(CONFIG["OUTPUT_EXT"])
    out_file.parent.mkdir(parents=True, exist_ok=True)

    bitrate = CONFIG["BITRATE"][CONFIG["MODE"]]

    cmd = [
        CONFIG["FFMPEG"],
        "-y",
        "-i", str(file),

        "-ac", "1" if CONFIG["MONO"] else "2",
        "-ar", str(CONFIG["SAMPLE_RATE"]),

        "-c:a", "libmp3lame",
        "-b:a", bitrate,
        "-compression_level", str(CONFIG["COMPRESSION_LEVEL"]),

        "-loglevel", CONFIG["LOGLEVEL"],

        str(out_file)
    ]

    print(f"[{i}/{len(files)}] {file.name} -> {bitrate}")

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("ERROR:", file)

print("Done")