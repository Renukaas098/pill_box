import argparse
import logging

from src.handler.embedding import handler as embedding_handler
from src.handler.face_detection import face_detection_handler
from src.handler.face_recognition import recognition_handler
from src.handler.webcam_recognition import webcam_recognition_handler
from src.utils.config import ConfigLoader
from src.utils.logger import setup_logger

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)


def main():

    setup_logger()

    parser = argparse.ArgumentParser(description="Face Pipeline Controller")

    parser.add_argument(
        "mode",
        choices=["detect", "embed", "recognize", "webcam"],
        help="Pipeline mode to run",
    )

    parser.add_argument("--image", help="Image path for recognition")

    args = parser.parse_args()

    config = ConfigLoader()

    # --------------------------------------------------
    # Face detection pipeline
    # --------------------------------------------------
    if args.mode == "detect":
        face_detection_handler()

    # --------------------------------------------------
    # Embedding pipeline
    # --------------------------------------------------
    elif args.mode == "embed":
        embedding_handler()

    # --------------------------------------------------
    # Recognition pipeline
    # --------------------------------------------------
    elif args.mode == "recognize":
        if not args.image:
            print("❌ Please provide --image path")
            return

        db_path = config.get_embedding_output()

        recognized_name = recognition_handler(args.image, db_path)
        logger.info(f"Recognized name: {recognized_name}")

    # --------------------------------------------------
    # Webcam recognition pipeline
    # --------------------------------------------------
    elif args.mode == "webcam":
        webcam_recognition_handler()


# ------------------------------------------------------

if __name__ == "__main__":
    main()
