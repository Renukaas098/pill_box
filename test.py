import cv2
from ultralytics import YOLO

# Load model
from src.utils.config import ConfigLoader

yolo_model_path = ConfigLoader().get_yolo_model_path()
model = YOLO(yolo_model_path)

# Confidence threshold
CONF_THRES = 0.8

cap = cv2.VideoCapture(0)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO
    results = model(frame, conf=CONF_THRES, verbose=False)

    if results[0].boxes is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()

        scores = results[0].boxes.conf.cpu().numpy()

        for box, score in zip(boxes, scores):
            if score < CONF_THRES:
                continue

            x1, y1, x2, y2 = map(int, box)

            # Crop face
            face_crop = frame[y1:y2, x1:x2]

            if face_crop.size == 0:
                continue

            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (57, 255, 20), 1)
            cv2.putText(
                frame,
                f"{score:.2f}",
                (x1, y1),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (34, 34, 178),
                2,
            )

    cv2.imshow("YOLOv8 Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
