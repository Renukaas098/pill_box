from src.service.face_detection import build_face_dataset
from src.utils.config import ConfigLoader


def face_detection_handler():

    config = ConfigLoader()

    data_dir = config.get_data_dir()
    output_file = config.get_faces_output()

    build_face_dataset(data_dir, output_file)


if __name__ == "__main__":
    face_detection_handler()
