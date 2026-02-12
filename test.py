import logging

from src.utils.logger import setup_logger

setup_logger()

logger = logging.getLogger("RecognitionService")

logger.error("Hello world")
