from src.service.embedding import EmbeddingService
from src.utils.config import ConfigLoader


def handler():

    config = ConfigLoader()

    face_data = config.get_faces_output()
    embedding_path = config.get_embedding_output()

    service = EmbeddingService()
    service.run(face_data, embedding_path)


if __name__ == "__main__":
    handler()
