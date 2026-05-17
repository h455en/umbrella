
"""
Burst Video into Unique Slides
Step 1 of the MCQ Pipeline: Extract, Crop, OCR, Clean, JSON, Import
Tested & Updated: 14.05.2026
"""

import cv2
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim

# ==========================================
# CONFIGURATION SECTION
# ==========================================

videoPath = r"C:\Users\h455n\Downloads\_PIPELINE\IN\BGE\BGE_Apprendre decider seul.mp4"  # Adjust to the location of your video

CONFIG = {
    "VIDEO_PATH": videoPath,
    "EXTRACT_EVERY_X_SECONDS": 60,      # Change this to extract every X seconds
    "SIMILARITY_THRESHOLD": 0.70,      # If SSIM >= this value, it's considered a duplicate slide
    "SAVE_DUPLICATES": False,          # True: saves with '_del_'. False: completely skips saving duplicates
}

# ==========================================
# CORE FUNCTIONS
# ==========================================

def calculate_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculates the Structural Similarity Index (SSIM) between two frames."""
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    similarity_index, _ = ssim(img1_gray, img2_gray, full=True)
    return float(similarity_index)


def get_output_folder(video_path: str) -> str:
    """Generates and creates the target BURST directory path."""
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = os.path.join(os.path.dirname(video_path), video_name, 'BURST')
    os.makedirs(output_folder, exist_ok=True)
    return output_folder


def extract_slides(video_path: str, config: dict):
    """Processes the video, extracting unique slide frames based on configuration."""
    output_folder = get_output_folder(video_path)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Could not open video file: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    # Calculate how many frames to skip based on requested seconds
    frame_interval = int(fps * config["EXTRACT_EVERY_X_SECONDS"])
    
    prev_frame = None
    frame_count = 0
    saved_count = 0

    print(f"[INFO] Starting extraction. FPS: {fps:.2f} | Extracting every {config['EXTRACT_EVERY_X_SECONDS']}s (Interval: {frame_interval} frames)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Check if it's time to sample a frame
        if frame_count % frame_interval == 0:
            slide_index = (frame_count // frame_interval) + 1
            filename = f"{video_name}___{slide_index:04d}.png"
            file_path = os.path.join(output_folder, filename)
            
            is_duplicate = False

            # Check similarity against the last saved frame
            if prev_frame is not None:
                similarity = calculate_similarity(prev_frame, frame)
                if similarity >= config["SIMILARITY_THRESHOLD"]:
                    is_duplicate = True

            # Decide what to do with duplicates based on config
            if is_duplicate:
                if config["SAVE_DUPLICATES"]:
                    file_path = file_path.replace(".png", "_del_.png")
                    cv2.imwrite(file_path, frame)
                    print(f"[-] Saved duplicate slide (flagged for deletion): {filename}")
                else:
                    print(f"[~] Skipped duplicate slide: {filename} (Similarity: {similarity:.4f})")
                    frame_count += 1
                    continue
            else:
                cv2.imwrite(file_path, frame)
                print(f"[+] Saved unique slide: {filename}")
                saved_count += 1
                # Only update prev_frame if it was a genuinely new unique slide
                prev_frame = frame

        frame_count += 1

    cap.release()
    print("\n" + "="*50)
    print(f"[SUCCESS] Extraction complete!")
    print(f"Total unique slides saved: {saved_count}")
    print(f"Output folder: {output_folder}")
    print("="*50)


# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    extract_slides(CONFIG["VIDEO_PATH"], CONFIG)