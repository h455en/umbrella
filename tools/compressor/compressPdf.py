
# python -m pip install pymupdf

import fitz  # PyMuPDF
import os
import sys
from pathlib import Path
from datetime import datetime

# ANSI Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def update_bar(current: int, total: int, prefix: str = ''):
    """Clean and responsive progress bar"""
    length = 35
    percent = 100 * (current / float(total))
    filled = int(length * current // total)
    bar = '█' * filled + '─' * (length - filled)
    sys.stdout.write(f'\r{prefix} {CYAN}|{bar}| {percent:5.1f}%{RESET}')
    sys.stdout.flush()


def aggressive_compress_colorful(
    source_folder: str | Path,
    dpi: int = 150,
    quality: int = 60,
    overwrite: bool = False
):
    os.system('')  # Enable ANSI colors on Windows

    base_path = Path(source_folder).resolve()
    
    if not base_path.exists():
        print(f"{RED}❌ Input folder not found: {base_path}{RESET}")
        return
    if not base_path.is_dir():
        print(f"{RED}❌ Path is not a directory: {base_path}{RESET}")
        return

    output_dir = base_path / "_COMPRESSED_PDF"
    output_dir.mkdir(exist_ok=True)

    # Find PDF files (case insensitive)
    pdf_files = [f for f in base_path.iterdir() 
                if f.is_file() and f.suffix.lower() == '.pdf']
    
    total_files = len(pdf_files)
    
    if total_files == 0:
        print(f"{YELLOW}⚠️  No PDF files found in folder.{RESET}")
        return

    print(f"{BOLD}{YELLOW}🚀 Starting aggressive PDF compression — {total_files} files{RESET}")
    print(f"   DPI: {dpi} | JPG Quality: {quality}% | Output: {output_dir.name}\n")

    total_original = 0
    total_new = 0

    for idx, pdf_path in enumerate(pdf_files, 1):
        output_path = output_dir / f"slim_{pdf_path.name}"
        
        if output_path.exists() and not overwrite:
            print(f"{BOLD}[{idx}/{total_files}]{RESET} {YELLOW}⏭️  Skipped (already exists){RESET} {pdf_path.name}")
            continue

        print(f"{BOLD}[{idx}/{total_files}]{RESET} {CYAN}Processing:{RESET} {pdf_path.name}")
        
        try:
            src_doc = fitz.open(pdf_path)
            dest_doc = fitz.open()
            total_pages = len(src_doc)

            for p_num, page in enumerate(src_doc, 1):
                update_bar(p_num, total_pages, prefix='   Pages')

                # Render page to image with reduced DPI
                pix = page.get_pixmap(dpi=dpi, alpha=False)
                img_data = pix.tobytes("jpeg", jpg_quality=quality)

                # Create new page with same dimensions
                new_page = dest_doc.new_page(width=page.rect.width, 
                                           height=page.rect.height)
                new_page.insert_image(new_page.rect, stream=img_data, 
                                    keep_proportion=True)

            sys.stdout.write(f" {YELLOW}Saving...{RESET}")
            sys.stdout.flush()

            # Aggressive saving options
            dest_doc.save(
                output_path,
                garbage=4,           # Aggressive garbage collection
                deflate=True,        # Compress streams
                clean=True,          # Clean unnecessary objects
                expand=0             # Don't expand
            )

            # Size statistics
            orig_size = pdf_path.stat().st_size / (1024 * 1024)
            new_size = output_path.stat().st_size / (1024 * 1024)
            gain = ((orig_size - new_size) / orig_size) * 100 if orig_size > 0 else 0

            total_original += orig_size
            total_new += new_size

            print(f"\n   {GREEN}✅ Done: {orig_size:.2f} MB → {new_size:.2f} MB "
                  f"({gain:.1f}% saved){RESET}\n")

            src_doc.close()
            dest_doc.close()

        except Exception as e:
            print(f"\n   {RED}❌ Error processing {pdf_path.name}: {e}{RESET}\n")

    # Final summary
    total_saved = total_original - total_new
    total_gain = (total_saved / total_original * 100) if total_original > 0 else 0

    print(f"{BOLD}{GREEN}✨ Compression completed!{RESET}")
    print(f"   Original: {total_original:.2f} MB")
    print(f"   Compressed: {total_new:.2f} MB")
    print(f"   Space saved: {total_saved:.2f} MB ({total_gain:.1f}%)")
    print(f"   Output folder: {output_dir}")


if __name__ == "__main__":
    # ================== CONFIG ==================
    IN_FOLDER = r"C:\Users\h455n\Downloads\_PIPELINE\IN\PDFS\AA"
    
    aggressive_compress_colorful(
        source_folder=IN_FOLDER,
        dpi=130,        # 120-150 is good balance (lower = smaller size)
        quality=45,     # 40-60 recommended
        overwrite=False
    )
