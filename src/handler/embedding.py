from src.service.embedding import EmbeddingService



def handler():
    service = EmbeddingService()
    service.run()


if __name__ == "__main__":
    handler()
