import logging
import cv2
import time

from src.service.face_recognition import RecognitionService

logger = logging.getLogger("WebcamRecognition")

class WebcamRecognition:

    def __init__(self, embedding_db_path):

        logger.info("Initializing Recognition Service...")
        self.service = RecognitionService(embedding_db_path)

    def run(self):

        cap = cv2.VideoCapture(0)

        logger.info("Webcam recognition started — press Q to exit")

        process_interval = 0.5   # run detection every 0.5 sec
        box_timeout = 0.6        # remove box if not updated

        last_process_time = 0
        last_detection_time = 0

        prev_box = None
        label = "Unknown"
        score = 0

        while True:

            ret, frame = cap.read()
            if not ret:
                break

            current_time = time.time()

            # Run recognition
            if current_time - last_process_time >= process_interval:

                last_process_time = current_time

                result = self.service.recognize_from_frame(frame)

                if result["box"] is not None:

                    prev_box = result["box"]
                    label = result["label"]
                    score = result["score"]
                    last_detection_time = current_time

            # Remove stale box
            if current_time - last_detection_time > box_timeout:
                prev_box = None

            # Draw box
            if prev_box is not None:

                x1 = prev_box["x1"]
                y1 = prev_box["y1"]
                x2 = prev_box["x2"]
                y2 = prev_box["y2"]

                text = f"{label} ({score:.2f})"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(
                    frame,
                    text,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0,255,0),
                    2
                )

            cv2.imshow("YOLO Face Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

