from src.utils.config import ConfigLoader
from src.service.face_detection import build_face_dataset


def face_detection_handler():

    config = ConfigLoader()

    data_dir = config.get_data_dir()
    output_file = config.get_output_file()

    build_face_dataset(data_dir, output_file)


if __name__ == "__main__":
    face_detection_handler()
