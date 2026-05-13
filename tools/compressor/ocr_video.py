
# pip install opencv-python pytesseract numpy scikit-image pillow

import cv2
import pytesseract
import os
from skimage.metrics import structural_similarity as ssim

# ===== CONFIG =====
VIDEO_PATH = r"F:\_ZDOWN\d50\exam_126_150.mp4"
OUTPUT_DIR = r"F:\_ZDOWN\d50\frames"
OCR_OUTPUT = r"F:\_ZDOWN\d50\out__exam_126_150.txt"
FRAME_INTERVAL_SEC = 0.5
SIMILARITY_THRESHOLD = 0.90



# ===== TESSERACT AUTO-DETECTION =====
def setup_tesseract():
    possible_paths = [
        r"F:\PROGRAM_FILES\TesseractOCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"[INFO] Tesseract found: {path}")
            return

    raise Exception("Tesseract not found. Install it from:\nhttps://github.com/UB-Mannheim/tesseract/wiki")

# ==================

def log(msg):
    print(f"[INFO] {msg}")


def extract_frames():
    log("Starting frame extraction...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * FRAME_INTERVAL_SEC)

    count = 0
    saved = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if count % frame_interval == 0:
            filename = f"{OUTPUT_DIR}/frame_{saved:02d}.png"
            cv2.imwrite(filename, frame)
            log(f"Saved {filename}")
            saved += 1

        count += 1

    cap.release()
    log(f"Total frames extracted: {saved}")


def crop_image(img):
    h, w = img.shape[:2]

    top = int(h * 0.05)
    bottom = int(h * 0.95)
    left = int(w * 0.05)
    right = int(w * 0.95)

    return img[top:bottom, left:right]


def is_similar(img1, img2):
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    gray1 = cv2.resize(gray1, (500, 300))
    gray2 = cv2.resize(gray2, (500, 300))

    score, _ = ssim(gray1, gray2, full=True)
    return score > SIMILARITY_THRESHOLD


def remove_duplicates():
    log("Removing duplicate frames...")
    files = sorted(os.listdir(OUTPUT_DIR))

    unique_files = []
    prev_img = None

    for f in files:
        path = os.path.join(OUTPUT_DIR, f)
        img = cv2.imread(path)

        if prev_img is None:
            unique_files.append(path)
            prev_img = img
            continue

        if not is_similar(prev_img, img):
            unique_files.append(path)
            prev_img = img
        else:
            log(f"Duplicate removed: {f}")

    log(f"Unique frames: {len(unique_files)}")
    return unique_files


def preprocess_for_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Improve OCR accuracy
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    return gray


def ocr_image(image_path, index):
    log(f"OCR processing frame {index:02d}...")

    img = cv2.imread(image_path)

    # Crop
    img = crop_image(img)
    log(f"Cropping applied on frame {index:02d}")

    # Preprocess
    processed = preprocess_for_ocr(img)

    config = "--oem 3 --psm 6 -l eng"

    text = pytesseract.image_to_string(processed, config=config)

    return text.strip()


def clean_text(text):
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()
        if len(line) > 2:
            cleaned.append(line)

    return "\n".join(cleaned)


def process_video():
    setup_tesseract()

    extract_frames()
    unique_frames = remove_duplicates()

    log("Starting OCR extraction...")

    with open(OCR_OUTPUT, "w", encoding="utf-8") as f:
        for idx, frame_path in enumerate(unique_frames, start=1):
            text = ocr_image(frame_path, idx)
            text = clean_text(text)

            log(f"Writing Slide {idx} to file")

            f.write(f"Slide {idx}\n")
            f.write(text + "\n")
            f.write("----------------------------\n")

    log("Export completed → output.txt")


if __name__ == "__main__":
    process_video()