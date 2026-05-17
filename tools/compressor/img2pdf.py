
# python -m pip install  reportlab pillow

import os
import argparse
from pathlib import Path
from PIL import Image

from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor


# ========================== CONFIGURATION ==========================

IN = r"C:\Users\h455n\Downloads\_PIPELINE\IN\BGE\BGE_Entreprendre"
PDF_PATH = r"C:\Users\h455n\Downloads\_PIPELINE\IN\IMG\E_00.pdf"

CONFIG = {
    "input_folder": IN,                    # ← Change this to your folder
    "output_pdf": PDF_PATH,
    "images_per_page": 4,
    "page_size": "A4",
    "orientation": "portrait",              # "portrait" or "landscape"
    "margin_inches": 0.35,

    "grid": {
        "auto": True,
        "rows": None,
        "cols": None
    },

    # Tight layout
    "image_padding": 0.008,                 # Very small gap between images
    "border_thickness": 1.0,
    "border_color": "#C40D0D",

    "show_folder_headers": True,
    "filename_max_length": 40,
    "show_page_numbers": True,
}
# ================================================================


def get_page_size():
    """Return correct page size based on orientation."""
    base_size = A4 if CONFIG["page_size"].upper() == "A4" else letter
    
    if CONFIG["orientation"].lower() == "landscape":
        return (base_size[1], base_size[0])   # Swap width and height
    else:
        return base_size                      # Portrait (default)


def get_images_recursive(root_folder):
    images = []
    valid_ext = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    for root, _, files in os.walk(root_folder):
        for file in sorted(files):
            if Path(file).suffix.lower() in valid_ext:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, root_folder)
                if rel_path == '.':
                    rel_path = ''
                images.append((rel_path, full_path))
    return images


def create_pdf():
    page_size = get_page_size()
    width, height = page_size
    margin = CONFIG["margin_inches"] * inch

    images = get_images_recursive(CONFIG["input_folder"])
    if not images:
        print("❌ No images found!")
        return

    # Grid setup
    if CONFIG["grid"]["auto"]:
        rows = int(CONFIG["images_per_page"] ** 0.5)
        cols = (CONFIG["images_per_page"] + rows - 1) // rows
    else:
        rows = CONFIG["grid"]["rows"] or int(CONFIG["images_per_page"] ** 0.5)
        cols = CONFIG["grid"]["cols"] or (CONFIG["images_per_page"] + rows - 1) // rows

    cell_w = (width - 2 * margin) / cols
    cell_h = (height - 2 * margin) / rows

    # Build TOC (tree style, no duplicates)
    toc = []
    seen_folders = set()
    img_idx = 0
    content_page = 2

    while img_idx < len(images):
        folder = images[img_idx][0]
        if folder not in seen_folders:
            seen_folders.add(folder)
            indent = "    " * folder.count(os.sep) if folder else ""
            display_name = f"{indent}• {folder}" if folder else "• Root Folder"
            toc.append((display_name, content_page))
        img_idx += CONFIG["images_per_page"]
        content_page += 1

    # ====================== Create PDF ======================
    c = canvas.Canvas(CONFIG["output_pdf"], pagesize=page_size)
    border_color = HexColor(CONFIG["border_color"])
    total_content_pages = len(toc)

    # ====================== Table of Contents ======================
    c.setFont("Helvetica-Bold", 24)
    c.drawString(margin, height - margin - 50, "Table of Contents")

    c.setFont("Helvetica", 12.5)
    y_pos = height - margin - 110

    for title, page_num in toc:
        c.drawString(margin + 30, y_pos, title)
        c.drawRightString(width - margin - 30, y_pos, str(page_num))

        c.linkRect(
            contents=title,
            destinationname=f"page{page_num}",
            Rect=(margin + 20, y_pos - 6, width - margin - 20, y_pos + 16),
            relative=1,
            thickness=0
        )
        y_pos -= 30
        if y_pos < 100:
            c.showPage()
            y_pos = height - margin - 80

    c.showPage()

    # ====================== Content Pages ======================
    img_idx = 0
    current_page = 2

    while img_idx < len(images):
        folder = images[img_idx][0]
        folder_title = f"Folder: {folder}" if folder else "Root Folder"

        if CONFIG["show_folder_headers"]:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margin, height - margin - 30, folder_title)

        for row in range(rows):
            for col in range(cols):
                if img_idx >= len(images):
                    break

                _, img_path = images[img_idx]
                x = margin + col * cell_w
                y = height - margin - (row + 1) * cell_h

                try:
                    with Image.open(img_path) as im:
                        img_w, img_h = im.size
                        padding = CONFIG["image_padding"]
                        
                        scale = min((cell_w * (1 - 2*padding)) / img_w,
                                   (cell_h * (1 - 2*padding)) / img_h)
                        
                        draw_w = img_w * scale
                        draw_h = img_h * scale
                        draw_x = x + (cell_w - draw_w) / 2
                        draw_y = y + (cell_h - draw_h) / 2 + 10

                        # Thin border
                        c.setStrokeColor(border_color)
                        c.setLineWidth(CONFIG["border_thickness"])
                        c.rect(draw_x - 3, draw_y - 3, draw_w + 6, draw_h + 6, stroke=1, fill=0)

                        # Draw image
                        c.drawImage(img_path, draw_x, draw_y,
                                    width=draw_w, height=draw_h,
                                    preserveAspectRatio=True)

                        # Filename
                        filename = os.path.basename(img_path)
                        c.setFont("Helvetica", 8)
                        c.drawCentredString(x + cell_w / 2, y + 4,
                                            filename[:CONFIG["filename_max_length"]])

                except Exception as e:
                    print(f"Error loading {img_path}: {e}")

                img_idx += 1

        # Page number
        if CONFIG["show_page_numbers"]:
            c.setFont("Helvetica", 9)
            c.drawCentredString(width / 2, 30, f"{current_page - 1} / {total_content_pages}")

        c.bookmarkPage(f"page{current_page}")
        c.showPage()
        current_page += 1

    c.save()
    print(f"✅ PDF successfully created: **{CONFIG['output_pdf']}**")
    print(f"   Orientation: {CONFIG['orientation'].capitalize()} | Images per page: {CONFIG['images_per_page']}")


def main():
    parser = argparse.ArgumentParser(description="Recursive Images to PDF")
    parser.add_argument("--input", type=str, help="Override input folder")
    parser.add_argument("--output", type=str, help="Override output PDF name")
    parser.add_argument("-n", "--images-per-page", type=int, help="Override images per page")
    parser.add_argument("--orientation", choices=["portrait", "landscape"], help="Override orientation")

    args = parser.parse_args()

    if args.input:
        CONFIG["input_folder"] = args.input
    if args.output:
        CONFIG["output_pdf"] = args.output
    if args.images_per_page:
        CONFIG["images_per_page"] = args.images_per_page
    if args.orientation:
        CONFIG["orientation"] = args.orientation

    create_pdf()


if __name__ == "__main__":
    main()