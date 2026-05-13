# ================================================
#          HEIC to JPEG/PNG Converter
# ================================================

# python -m pip install pillow pillow-heif

# ==================== CONFIG ====================
INPUT_FOLDER = r"C:\Users\h455n\Downloads\_PIPELINE\IN\IMG\ECOLE\CE2"   # Change this

TARGET_FORMAT = "JPEG"      # Options: "JPEG" or "PNG"
QUALITY = 70                # 1-100 (only applies to JPEG)
DELETE_ORIGINAL = False     # Set to True to delete HEIC files after successful conversion (Use with caution!)
# ================================================

import os
from pathlib import Path
from PIL import Image
import pillow_heif
import gc
import time

# Enable HEIC support
pillow_heif.register_heif_opener()


def convert_heic_files():
    input_path = Path(INPUT_FOLDER).resolve()
    
    if not input_path.exists():
        print(f"❌ Error: Input folder not found -> {input_path}")
        return

    # Auto create output folder at the same level as input folder
    parent_folder = input_path.parent
    output_name = f"{input_path.name}_converted_{TARGET_FORMAT.lower()}"
    output_path = parent_folder / output_name
    
    output_path.mkdir(exist_ok=True)

    # Find all HEIC/HEIF files (recursive)
    heic_files = list(input_path.glob("**/*.[Hh][Ee][Ii][Cc]")) + \
                 list(input_path.glob("**/*.[Hh][Ee][Ii][Ff]"))
    
    total = len(heic_files)
    print(f"Found {total} HEIC/HEIF files.")
    print(f"Output folder: {output_path}\nStarting conversion...\n")

    converted = 0
    failed = 0

    for i, heic_file in enumerate(heic_files, 1):
        try:
            # Keep same subfolder structure if any
            relative_path = heic_file.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix(f".{TARGET_FORMAT.lower()}")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with Image.open(heic_file) as img:
                if TARGET_FORMAT == "JPEG" and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                save_params = {"format": TARGET_FORMAT}
                if TARGET_FORMAT == "JPEG":
                    save_params.update({"quality": QUALITY, "optimize": True})
                
                img.save(output_file, **save_params)
            
            converted += 1
            print(f"[{i:4d}/{total}] ✅ {heic_file.name} → {output_file.name}")

            # Memory management to prevent freezing
            if i % 30 == 0:
                gc.collect()
                time.sleep(0.05)

        except Exception as e:
            failed += 1
            print(f"[{i:4d}/{total}] ❌ Failed {heic_file.name} | {e}")

    # Final summary
    print("\n" + "="*65)
    print(f"✅ Conversion Completed!")
    print(f"   Successfully converted : {converted}/{total}")
    print(f"   Failed                 : {failed}")
    print(f"   Output location        : {output_path}")
    print("="*65)


# ==================== RUN ====================
if __name__ == "__main__":
    convert_heic_files()