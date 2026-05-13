#python -m pip install fpdf2 Pillow
#python -m pip install weasyprint Pillow
#python -m pip install reportlab Pillow

import os
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import red
from colorama import Fore, Style, init

init(autoreset=True)

def quick_log(msg, color=Fore.CYAN):
    print(f"{color}{Style.BRIGHT}>> {msg}")

def create_ultra_fast_catalog(root_folder, output_pdf):
    quick_log("Starting Ultra-Fast Validation Mode...")
    
    if not os.path.exists(root_folder):
        print(f"{Fore.RED}Error: Path '{root_folder}' not found.")
        return

    # Canvas and Margin Setup
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4
    margin = 15 * mm  # Strict PDF margins
    
    # Grid Config (6x6)
    cols, rows = 6, 6
    usable_w = width - (2 * margin)
    usable_h = height - (2 * margin)
    cell_w = usable_w / cols
    cell_h = usable_h / rows

    # 1. Collect all image paths immediately
    all_images = []
    for root, _, files in os.walk(root_folder):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                all_images.append(os.path.join(root, f))
    
    quick_log(f"Found {len(all_images)} images. Building PDF...")

    # 2. Direct Placement (No TOC, No Orientation Checks)
    for i in range(0, len(all_images), cols * rows):
        batch = all_images[i : i + cols * rows]
        
        for idx, img_path in enumerate(batch):
            col = idx % cols
            row = idx // cols
            
            # Position calculation (Top-Down)
            x = margin + (col * cell_w)
            y = (height - margin) - ((row + 1) * cell_h)

            try:
                # 'anchorAtXY=True' and no aspect ratio preservation for raw speed validation
                # This fills the cell exactly, even if it causes slight stretching
                c.drawImage(img_path, x, y, width=cell_w, height=cell_h, mask='auto')
                
                # Visual grid lines
                c.setStrokeColor(red)
                c.setLineWidth(0.5)
                c.rect(x, y, cell_w, cell_h, stroke=1)
            except Exception:
                continue
        
        c.showPage()
        sys.stdout.write(f"\r{Fore.GREEN}Processed Page {i // 36 + 1}")
        sys.stdout.flush()

    quick_log("\nFinalizing file...")
    c.save()
    print(f"{Fore.YELLOW}{Style.BRIGHT}DONE: {output_pdf}")

if __name__ == "__main__":
    root_folder=r"C:\Users\h455n\Downloads\_PIPELINE\IN\IMG"
    output_pdf=r"C:\Users\h455n\Downloads\_PIPELINE\IN\IMG\pdf_01.pdf"
    # SET FOLDER HERE
    create_ultra_fast_catalog(root_folder,output_pdf)

