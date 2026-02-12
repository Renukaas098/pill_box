from src.utils.config import ConfigLoader
from src.service.embedding import EmbeddingService


def handler():

    config = ConfigLoader()

    dataset_path = config.get_data_dir()
    output_path = config.get_embedding_output()

    service = EmbeddingService()
    service.run(dataset_path, output_path)


if __name__ == "__main__":
    handler()
