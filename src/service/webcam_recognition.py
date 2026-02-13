import logging

import cv2
import numpy as np
from keras_facenet import FaceNet
from numpy.linalg import norm
from ultralytics import YOLO

from src.utils.config import ConfigLoader

logger = logging.getLogger("WebcamRecognition")


class WebcamRecognition:
    def __init__(self, embedding_db_path, threshold=0.7):

        config = ConfigLoader()

        logger.info("Loading YOLO model...")
        self.detector = YOLO(config.get_yolo_model_path())

        logger.info("Loading FaceNet...")
        self.embedder = FaceNet()

        logger.info("Loading embedding database...")
        data = np.load(embedding_db_path, allow_pickle=True)

        self.known_embeddings = data["arr_0"]
        self.known_labels = data["arr_1"]

        self.threshold = threshold
        self.conf_thres = 0.8

    # --------------------------------------------------

    @staticmethod
    def cosine_similarity(a, b):
        return np.dot(a, b) / (norm(a) * norm(b))

    # --------------------------------------------------

    def recognize_face(self, face):

        emb = self.embedder.embeddings([face])[0]

        best_score = -1
        best_label = "Unknown"

        for known_emb, label in zip(self.known_embeddings, self.known_labels):
            score = self.cosine_similarity(emb, known_emb)

            if score > best_score:
                best_score = score
                best_label = label

        if best_score < self.threshold:
            best_label = "Unknown"

        return best_label, best_score

    # --------------------------------------------------

    def run(self):

        cap = cv2.VideoCapture(0)

        logger.info("Webcam recognition started — press Q to exit")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = self.detector(frame, conf=self.conf_thres, verbose=False)

            if results[0].boxes is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()

                for box in boxes:
                    x1, y1, x2, y2 = map(int, box)

                    face = frame[y1:y2, x1:x2]

                    if face.size == 0:
                        continue

                    face = cv2.resize(face, (160, 160))
                    face = face[:, :, ::-1]  # BGR → RGB

                    label, score = self.recognize_face(face)

                    text = f"{label} ({score:.2f})"

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        text,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2,
                    )

            cv2.imshow("YOLO Face Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
