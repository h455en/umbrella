
# python -m pip install 

import os
import time
import subprocess
from pathlib import Path
from PIL import Image



# --- CONFIGURATION ---
IN = r"C:\Users\h455n\Downloads\Rdv"
OUT = IN + '_RESIZED'

CONFIG = {
    "IN_DIR":IN,
    "OUT_DIR": OUT,
    "QUALITY": 50, # No less than 20, 50 is good 
    "MAX_WIDTH": 1200, 
    "OPTIMIZE": True, 
    "EXTENSIONS": {'.jpg', '.jpeg', '.png'}
}

# ANSI Colors
GREEN, RED, CYAN, YELLOW, RESET = '\033[92m', '\033[91m', '\033[96m', '\033[93m', '\033[0m'

def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G", "T"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor

def get_folder_size(path):
    """Simple recursive size calculation."""
    total = 0
    p = Path(path)
    if not p.exists(): return 0
    for entry in p.rglob('*'):
        if entry.is_file():
            total += entry.stat().st_size
    return total

def process_photos():
    start_time = time.time()
    count = 0
    
    in_path = Path(CONFIG["IN_DIR"]).resolve()
    out_path = Path(CONFIG["OUT_DIR"]).resolve()

    if not in_path.exists():
        print(f"{RED}[ERROR] Input directory not found: {in_path}{RESET}")
        return

    # Check if Out is inside In to prevent infinite loops
    if in_path in out_path.parents or in_path == out_path:
        print(f"{RED}[ERROR] OUT_DIR cannot be inside IN_DIR for mirroring!{RESET}")
        return

    print(f"{CYAN}--- Starting Recursive Mirroring ---{RESET}")
    print(f"Source: {in_path}")
    print(f"Result: {out_path}\n")

    # Calculate initial size
    size_before = get_folder_size(in_path)

    # Walk through the directory recursively
    for file_path in in_path.rglob('*'):
        # Filter for image extensions
        if file_path.suffix.lower() in CONFIG["EXTENSIONS"]:
            
            # 1. Map the source path to the destination path
            relative_path = file_path.relative_to(in_path)
            destination = out_path / relative_path
            
            # 2. Recreate the specific subfolder structure in the destination
            destination.parent.mkdir(parents=True, exist_ok=True)

            try:
                with Image.open(file_path) as img:
                    img = img.convert("RGB")
                    
                    # Resize logic
                    if img.size[0] > CONFIG["MAX_WIDTH"]:
                        w_percent = (CONFIG["MAX_WIDTH"] / float(img.size[0]))
                        h_size = int((float(img.size[1]) * float(w_percent)))
                        img = img.resize((CONFIG["MAX_WIDTH"], h_size), Image.Resampling.LANCZOS)

                    img.save(destination, "JPEG", quality=CONFIG["QUALITY"], optimize=CONFIG["OPTIMIZE"])
                    print(f"{GREEN}[SUCCESS]{RESET} {relative_path}")
                    count += 1
            except Exception as e:
                print(f"{RED}[ERROR]{RESET}   Failed {relative_path}: {e}")

    # Final stats
    size_after = get_folder_size(out_path)
    duration = round(time.time() - start_time, 2)
    diff = size_before - size_after
    gain_pct = (diff / size_before) * 100 if size_before > 0 else 0

    print(f"\n{CYAN}--- Mirroring Finished ---{RESET}")
    print(f"{YELLOW}Photos Processed:  {count}")
    print(f"{YELLOW}Source Total Size: {get_size_format(size_before)}")
    print(f"{YELLOW}Result Total Size: {get_size_format(size_after)}")
    print(f"{GREEN}Space Gained:      {get_size_format(diff)} ({gain_pct:.1f}% reduction){RESET}")
    print(f"{YELLOW}Total Time:        {duration} seconds{RESET}")

    subprocess.Popen(f'explorer "{out_path}"')

if __name__ == "__main__":
    os.system('') 
    process_photos()