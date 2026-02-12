import logging

import numpy as np
from keras_facenet import FaceNet
from mtcnn.mtcnn import MTCNN
from numpy.linalg import norm
from PIL import Image

logger = logging.getLogger("RecognitionService")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class RecognitionService:
    def __init__(self, embedding_db_path):

        logger.info("Loading embedding database...")
        data = np.load(embedding_db_path, allow_pickle=True)

        self.known_embeddings = data["arr_0"]
        self.known_labels = data["arr_1"]

        logger.info(f"Database loaded → {self.known_embeddings.shape}")

        self.detector = MTCNN()
        self.embedder = FaceNet()

    # --------------------------------------------------

    @staticmethod
    def cosine_similarity(a, b):
        return np.dot(a, b) / (norm(a) * norm(b))

    # --------------------------------------------------

    def extract_face(self, filename, size=(160, 160)):

        try:
            img = np.array(Image.open(filename).convert("RGB"))
            faces = self.detector.detect_faces(img)

            if not faces:
                logger.warning("No face detected")
                return None

            x, y, w, h = faces[0]["box"]
            x, y = abs(x), abs(y)

            face = img[y : y + h, x : x + w]
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
