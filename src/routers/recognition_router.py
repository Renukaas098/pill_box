import logging
import numpy as np
import cv2

from fastapi import APIRouter, UploadFile, File
from src.service.service_registry import recognition_service

logger = logging.getLogger("RecognitionAPI")

router = APIRouter()




@router.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    try:

        contents = await image.read()

        nparr = np.frombuffer(contents, np.uint8)

        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return {
                "success": False,
                "error": "Invalid image"
            }

        result = recognition_service.recognize_from_frame(frame)

        logger.info(f"Recognition result: {result}")

        return {
            "success": True,
            "result": result
        }

    except Exception as e:

        logger.error(f"Recognition error: {str(e)}")

        return {
            "success": False,
            "error": str(e)
        }
    
@router.post("/reload_embeddings")
def reload_embeddings():

    try:

        recognition_service.reload_embeddings()

        return {
            "success": True,
            "message": "Embeddings reloaded successfully"
        }

    except Exception as e:

        logger.error(str(e))

        return {
            "success": False,
            "error": str(e)
        }
    
@router.get("/detection_log")
def get_detection_log():

    try:

        logs = recognition_service.get_detection_logs()

        return {
            "success": True,
            "logs": logs
        }

    except Exception as e:

        logger.error(str(e))

        return {
            "success": False,
            "error": str(e)
        }
    
@router.get("/model_status")
def model_status():

    try:

        status = recognition_service.get_model_status()

        return {
            "success": True,
            "model": status
        }

    except Exception as e:

        logger.error(str(e))

        return {
            "success": False,
            "error": str(e)
        }