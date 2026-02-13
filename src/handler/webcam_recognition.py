import logging

from src.service.webcam_recognition import WebcamRecognition
from src.utils.config import ConfigLoader

logger = logging.getLogger("webcam_handler")


def webcam_recognition_handler():

    logger.info("Starting webcam recognition handler...")

    config = ConfigLoader()

    db_path = config.get_embedding_output()

    recognizer = WebcamRecognition(db_path)

    recognizer.run()
