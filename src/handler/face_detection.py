from src.service.face_detection import FaceDatasetService


def face_detection_handler():

    service = FaceDatasetService()
    service.run()


