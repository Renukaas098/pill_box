import logging

from src.service.webcam_recognition import WebcamRecognition

logger = logging.getLogger("webcam_handler")


def webcam_recognition_handler():

    logger.info("Starting webcam recognition handler...")
    recognizer = WebcamRecognition()

    recognizer.run()
