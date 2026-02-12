import logging
from src.service.face_recognition import RecognitionService

from src.utils.logger import setup_logger

setup_logger()


# ------------------------------------------------------
# Logger setup
# ------------------------------------------------------
logger = logging.getLogger("RecognitionHandler")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ------------------------------------------------------
# Handler
# ------------------------------------------------------
def recognition_handler(image_path, db_path):

    logger.info("Recognition handler started")

    service = RecognitionService(db_path)

    result = service.recognize(image_path)

    logger.info("Recognition result")
    logger.info(f"Match → {result['label']}")
    logger.info(f"Similarity → {result['score']:.3f}")

    logger.info("Recognition handler completed")

    return result
