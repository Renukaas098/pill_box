import logging
import os
import time

import numpy as np
from numpy import asarray
from PIL import Image
from ultralytics import YOLO

from src.utils.config import ConfigLoader
from src.utils.logger import setup_logger


setup_logger()
logger = logging.getLogger("FaceDatasetService")

CONF_THRES = 0.8


class FaceDatasetService:

    def __init__(self):

        self.config = ConfigLoader()

        self.data_dir = self.config.get_data_dir()
        self.output_file = self.config.get_faces_output()
        self.yolo_model_path = self.config.get_yolo_model_path()

        logger.info("Loading YOLO face detector...")
        self.detector = YOLO(self.yolo_model_path)

    # --------------------------------------------------

    def extract_face(self, filename, required_size=(160, 160)):

        try:
            image = Image.open(filename).convert("RGB")
            pixels = asarray(image)

            frame = pixels[:, :, ::-1]

            results = self.detector(frame, conf=CONF_THRES, verbose=False)

            if not results or results[0].boxes is None:
                logger.warning(f"No face detected → {filename}")
                return None

            boxes = results[0].boxes.xyxy.cpu().numpy()
            scores = results[0].boxes.conf.cpu().numpy()

            best_idx = np.argmax(scores)
            x1, y1, x2, y2 = map(int, boxes[best_idx])

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

    # --------------------------------------------------

    def load_faces(self, directory):

        faces = []

        for filename in os.listdir(directory):

            path = os.path.join(directory, filename)

            if os.path.isfile(path):

                face = self.extract_face(path)

                if face is not None:
                    faces.append(face)

        return faces

    # --------------------------------------------------

    def load_dataset(self):

        X, y = [], []
        start = time.time()

        logger.info(f"Starting dataset load → {self.data_dir}")

        for subdir in os.listdir(self.data_dir):

            path = os.path.join(self.data_dir, subdir)

            if not os.path.isdir(path):
                continue

            logger.info(f"Processing class → {subdir}")

            faces = self.load_faces(path)
            labels = [subdir] * len(faces)

            X.extend(faces)
            y.extend(labels)

            logger.info(f"Loaded {len(faces)} faces")

        logger.info(f"Dataset loading finished in {time.time() - start:.2f} sec")

        return asarray(X), asarray(y)

    # --------------------------------------------------

    def save_dataset(self, faces, labels):

        logger.info(f"Saving dataset → {self.output_file}")

        np.savez_compressed(self.output_file, faces, labels)

        logger.info("Dataset saved successfully")

    # --------------------------------------------------

    def run(self):

        logger.info("Face dataset pipeline started")

        faces, labels = self.load_dataset()

        logger.info(f"Faces shape: {faces.shape}")
        logger.info(f"Labels shape: {labels.shape}")

        self.save_dataset(faces, labels)

        logger.info("Face dataset pipeline completed")

    def extract_face_from_frame(self, frame, required_size=(160,160)):

        pixels = frame[:, :, ::-1]

        results = self.detector(frame, conf=CONF_THRES, verbose=False)

        if not results or results[0].boxes is None:
            return None

        boxes = results[0].boxes.xyxy.cpu().numpy()
        scores = results[0].boxes.conf.cpu().numpy()

        best_idx = np.argmax(scores)

        x1, y1, x2, y2 = map(int, boxes[best_idx])

        face_pixels = pixels[y1:y2, x1:x2]

        face_image = Image.fromarray(face_pixels).resize(required_size)

        return np.asarray(face_image)