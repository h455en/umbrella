
# python -m pip install pymupdf

import fitz  # PyMuPDF
import os
import sys
from pathlib import Path

# ANSI Color Codes
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def update_bar(current, total, prefix=''):
    length = 30
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled = int(length * current // total)
    bar = '█' * filled + '-' * (length - filled)
    # Using Cyan for the progress bar
    sys.stdout.write(f'\r{prefix} {CYAN}|{bar}| {percent}%{RESET}')
    sys.stdout.flush()

def aggressive_compress_colorful(source_folder, dpi=150, quality=50):
    # Enable ANSI colors for Windows 10+ consoles
    os.system('') 

    base_path = Path(source_folder)
    output_dir = base_path / "_COMP_PDF_AGGRESSIVE"
    output_dir.mkdir(exist_ok=True)

    pdf_files = list(base_path.glob("*.pdf")) + list(base_path.glob("*.PDF"))
    total_files = len(pdf_files)
    
    if total_files == 0:
        print(f"{RED}No PDF files found in the folder.{RESET}")
        return

    print(f"{BOLD}{YELLOW}🚀 Starting Batch: {total_files} files found.{RESET}")
    print(f"{YELLOW}Settings: DPI={dpi}, Quality={quality}%{RESET}\n")

    for idx, pdf_path in enumerate(pdf_files, 1):
        output_path = output_dir / f"slim_{pdf_path.name}"
        
        print(f"{BOLD}[{idx}/{total_files}]{RESET} {CYAN}Processing:{RESET} {pdf_path.name}")
        
        try:
            src_doc = fitz.open(pdf_path)
            dest_doc = fitz.open()
            total_pages = len(src_doc)
            
            for p_num, page in enumerate(src_doc, 1):
                update_bar(p_num, total_pages, prefix='   Pages')
                
                pix = page.get_pixmap(dpi=dpi)
                img_data = pix.tobytes("jpg", jpg_quality=quality)
                
                new_page = dest_doc.new_page(width=page.rect.width, 
                                           height=page.rect.height)
                new_page.insert_image(new_page.rect, stream=img_data)
                
            sys.stdout.write(f" {YELLOW}- Saving...{RESET}")
            sys.stdout.flush()
            
            dest_doc.save(output_path, garbage=4, deflate=True)
            
            orig_size = pdf_path.stat().st_size / (1024 * 1024)
            new_size = output_path.stat().st_size / (1024 * 1024)
            
            # Calculate Gain Percentage
            # Formula: ((Original - New) / Original) * 100
            gain = ((orig_size - new_size) / orig_size) * 100 if orig_size > 0 else 0
            
            # Final line with size comparison and gain
            print(f"\n   {GREEN}✅ Done: {orig_size:.1f} MB → {new_size:.1f} MB ({gain:.1f}% space saved){RESET}\n")
            
            src_doc.close()
            dest_doc.close()
            
        except Exception as e:
            print(f"\n   {RED}❌ Error: {e}{RESET}\n")

    print(f"{BOLD}{GREEN}✨ All tasks complete!{RESET}")
    print(f"Output folder: {output_dir}")

if __name__ == "__main__":
    # Settings: DPI 150 is good, 120 is more aggressive.
    target_directory = r"C:\Users\h455n\Downloads\_PIPELINE\AR\_SELECT"
    
    aggressive_compress_colorful(target_directory, dpi=120, quality=40)
    
