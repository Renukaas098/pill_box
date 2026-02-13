import logging
import os
import time

import numpy as np
from numpy import asarray
from PIL import Image
from ultralytics import YOLO

from src.utils.config import ConfigLoader
from src.utils.logger import setup_logger

# Load YOLO face detector once
yolo_model_path = ConfigLoader().get_yolo_model_path()
detector = YOLO(yolo_model_path)

CONF_THRES = 0.8

setup_logger()
# ------------------------------------------------------
# Logger setup
# ------------------------------------------------------
logger = logging.getLogger("FaceDatasetService")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ------------------------------------------------------
# Face detector (load once)
# ------------------------------------------------------


# ------------------------------------------------------
# Face extraction
# ------------------------------------------------------
def extract_face(filename, required_size=(160, 160)):

    try:
        image = Image.open(filename).convert("RGB")
        pixels = asarray(image)

        # YOLO expects BGR → convert
        frame = pixels[:, :, ::-1]

        results = detector(frame, conf=CONF_THRES, verbose=False)

        if not results or results[0].boxes is None:
            logger.warning(f"No face detected → {filename}")
            return None

        boxes = results[0].boxes.xyxy.cpu().numpy()
        scores = results[0].boxes.conf.cpu().numpy()

        # Pick highest confidence face
        best_idx = np.argmax(scores)
        x1, y1, x2, y2 = map(int, boxes[best_idx])

        # Clamp bounds
        h, w, _ = frame.shape
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        face_pixels = pixels[y1:y2, x1:x2]

        if face_pixels.size == 0:
            return None

        face_image = Image.fromarray(face_pixels).resize(required_size)

        return asarray(face_image)

    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")
        return None


# ------------------------------------------------------
# Load faces from folder
# ------------------------------------------------------
def load_faces(directory):

    faces = []

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)

        if os.path.isfile(path):
            face = extract_face(path)

            if face is not None:
                faces.append(face)

    return faces


# ------------------------------------------------------
# Load dataset
# ------------------------------------------------------
def load_dataset(directory):

    X, y = [], []
    start = time.time()

    logger.info(f"Starting dataset load → {directory}")

    for subdir in os.listdir(directory):
        path = os.path.join(directory, subdir)

        if not os.path.isdir(path):
            continue

        logger.info(f"Processing class → {subdir}")

        faces = load_faces(path)
        labels = [subdir] * len(faces)

        X.extend(faces)
        y.extend(labels)

        logger.info(f"Loaded {len(faces)} faces")

    logger.info(f"Dataset loading finished in {time.time() - start:.2f} sec")

    return asarray(X), asarray(y)


# ------------------------------------------------------
# Build dataset
# ------------------------------------------------------
def build_face_dataset(data_dir, output_file):

    logger.info("Face dataset pipeline started")

    faces, labels = load_dataset(data_dir)

    logger.info(f"Faces shape: {faces.shape}")
    logger.info(f"Labels shape: {labels.shape}")

    np.savez_compressed(output_file, faces, labels)

    logger.info(f"Dataset saved → {output_file}")
    logger.info("Face dataset pipeline completed")

    return faces, labels
