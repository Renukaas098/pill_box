import logging

import numpy as np
from keras_facenet import FaceNet
from numpy.linalg import norm
from PIL import Image
from ultralytics import YOLO
import time

from src.utils.config import ConfigLoader

logger = logging.getLogger("RecognitionService")
logger.setLevel(logging.INFO)

yolo_model_path = ConfigLoader().get_yolo_model_path()


if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class RecognitionService:
    def __init__(self):
        config = ConfigLoader()
        self.embedding_path = config.get_embedding_output()
        self.logs = []

        logger.info("Loading embedding database...")
        data = np.load(self.embedding_path, allow_pickle=True)

        self.known_embeddings = data["arr_0"]
        self.known_labels = data["arr_1"]

        logger.info(f"Database loaded → {self.known_embeddings.shape}")

        self.detector = YOLO(yolo_model_path)

        self.CONF_THRES = 0.5
        self.embedder = FaceNet()

    # --------------------------------------------------

    @staticmethod
    def cosine_similarity(a, b):
        return np.dot(a, b) / (norm(a) * norm(b))

    # --------------------------------------------------

    def extract_face(self, filename, size=(160, 160)):

        try:
            img = np.array(Image.open(filename).convert("RGB"))

            # YOLO expects BGR
            frame = img[:, :, ::-1]

            results = self.detector(frame, conf=self.CONF_THRES, verbose=False)

            if not results or results[0].boxes is None:
                logger.warning("No face detected")
                return None

            boxes = results[0].boxes.xyxy.cpu().numpy()
            scores = results[0].boxes.conf.cpu().numpy()

            # choose highest confidence face
            best_idx = np.argmax(scores)
            x1, y1, x2, y2 = map(int, boxes[best_idx])

            # clamp bounds
            h, w, _ = frame.shape
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            face = img[y1:y2, x1:x2]

            if face.size == 0:
                return None

            face = Image.fromarray(face).resize(size)

            return np.asarray(face)

        except Exception as e:
            logger.error(f"Face extraction failed: {e}")
            return None

    # --------------------------------------------------

    def recognize(self, image_path, threshold=0.7):

        logger.info(f"Recognizing → {image_path}")

        face = self.extract_face(image_path)

        if face is None:
            return {"label": "No face", "score": 0}

        embedding = self.embedder.embeddings([face])[0]

        best_score = -1
        best_label = "Unknown"

        for known_emb, label in zip(self.known_embeddings, self.known_labels):
            score = self.cosine_similarity(embedding, known_emb)

            if score > best_score:
                best_score = score
                best_label = label

        if best_score < threshold:
            best_label = "Unknown"

        result = {"label": best_label, "score": float(best_score)}

        logger.info(f"Result → {result}")

        return result

    # --------------------------------------------------

    def recognize_from_frame(self, frame, threshold=0.7):

        try:
            logger.info("Recognizing from frame")

            img = frame[:, :, ::-1]  # BGR → RGB

            results = self.detector(frame, conf=self.CONF_THRES, verbose=False)

            if not results or results[0].boxes is None:
                return {"faces": []}

            boxes = results[0].boxes.xyxy.cpu().numpy()

            faces_result = []

            h, w, _ = frame.shape

            for box in boxes:

                x1, y1, x2, y2 = map(int, box)

                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                width = x2 - x1
                height = y2 - y1

                face = img[y1:y2, x1:x2]

                if face.size == 0:
                    continue

                face = Image.fromarray(face).resize((160, 160))
                face = np.asarray(face)

                embedding = self.embedder.embeddings([face])[0]

                best_score = -1
                best_label = "Unknown"

                for known_emb, label in zip(self.known_embeddings, self.known_labels):

                    score = self.cosine_similarity(embedding, known_emb)

                    if score > best_score:
                        best_score = score
                        best_label = label

                if best_score < threshold:
                    best_label = "Unknown"

                faces_result.append({
                                    "label": best_label,
                                    "score": float(best_score),
                                    "box": {
                                        "x1": x1,
                                        "y1": y1,
                                        "x2": x2,
                                        "y2": y2
                                    }
                                })

            return {
                "image_width": w,
                "image_height": h,
                "faces": faces_result
            }

        except Exception as e:

            logger.error(f"Frame recognition failed: {e}")

            return {"faces": []}
        

    def add_detection_log(self, name):

        entry = {
            "user": name,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        self.logs.append(entry)

        # keep last 100 logs only
        if len(self.logs) > 100:
            self.logs.pop(0)

    # --------------------------------------------------

    def get_detection_logs(self):

        return self.logs
    
    def reload_embeddings(self):

        logger.info("Reloading embeddings...")

        data = np.load(self.embedding_path, allow_pickle=True)

        self.known_embeddings = data["arr_0"]
        self.known_labels = data["arr_1"]

        logger.info(f"Embeddings reloaded. Users: {len(set(self.known_labels))}")

        
    def get_model_status(self):

        users = len(set(self.known_labels))
        embeddings_count = len(self.known_embeddings)

        return {
            "face_detector": "YOLO",
            "embedding_model": "FaceNet",
            "users_registered": users,
            "embeddings_loaded": embeddings_count,
            "status": "ready"
        }
            
    

