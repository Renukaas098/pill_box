import logging
import numpy as np
import cv2
from fastapi import APIRouter, UploadFile, File, Form
from typing import List

from src.service.embedding import EmbeddingService
from src.service.face_detection import FaceDatasetService

logger = logging.getLogger("UserAPI")

router = APIRouter()

face_service = FaceDatasetService()
embedding_service = EmbeddingService()


@router.get("/user_list")
def get_registered_users():
    try:

        names = embedding_service.get_all_names()

        logger.info(f"Registered users: {names}")

        return {
            "success": True,
            "users": names
        }

    except Exception as e:

        logger.error(f"Error fetching users: {str(e)}")

        return {
            "success": False,
            "error": str(e)
        }
    
@router.post("/register-user")
async def register_user(
        name: str = Form(...),
        images: List[UploadFile] = File(...)
):

    try:

        faces = []

        for img in images:

            contents = await img.read()

            nparr = np.frombuffer(contents, np.uint8)

            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            face = face_service.extract_face_from_frame(frame)

            if face is not None:
                faces.append(face)

        if len(faces) == 0:
            return {"success": False, "error": "No face detected"}

        faces = np.array(faces)

        faces_added = embedding_service.register_user_embeddings(name, faces)

    
        embedding_service.reload_embeddings()

        return {
            "success": True,
            "user": name,
            "faces_added": faces_added
        }

    except Exception as e:

        logger.error(str(e))

        return {"success": False, "error": str(e)}
    
@router.delete("/user/{name}")
def delete_user(name: str):

    try:

        deleted = embedding_service.delete_user(name)

        if not deleted:
            return {
                "success": False,
                "message": f"user '{name}' not found"
            }
        else:
            embedding_service.reload_embeddings()

        return {
            "success": True,
            "deleted_user": name
        }

    except Exception as e:

        logger.error(str(e))

        return {
            "success": False,
            "error": str(e)
        }

