import logging
import time

import numpy as np
from keras_facenet import FaceNet
import ssl
import certifi

ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())


# ------------------------------------------------------
# Logger setup
# ------------------------------------------------------
logger = logging.getLogger("EmbeddingService")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class EmbeddingService:
    def __init__(self):
        logger.info("Loading FaceNet embedder...")
        self.embedder = FaceNet()

    # --------------------------------------------------

    def load_dataset(self, dataset_path):

        logger.info(f"Loading dataset → {dataset_path}")

        data = np.load(dataset_path, allow_pickle=True)

        faces = data["arr_0"]
        labels = data["arr_1"]

        logger.info("Dataset loaded successfully")
        logger.info(f"Faces: {faces.shape}")
        logger.info(f"Labels: {labels.shape}")

        return faces, labels

    # --------------------------------------------------

    def generate_embeddings(self, faces):

        start = time.time()

        logger.info("Generating embeddings...")
        embeddings = self.embedder.embeddings(faces)

        logger.info(f"Embeddings shape: {embeddings.shape}")
        logger.info(f"Embedding generation completed in {time.time() - start:.2f} sec")

        return embeddings

    # --------------------------------------------------

    def save_embeddings(self, output_path, embeddings, labels):

        logger.info(f"Saving embeddings → {output_path}")

        np.savez_compressed(output_path, embeddings, labels)

        logger.info("Embeddings saved successfully")

    # --------------------------------------------------

    def run(self, dataset_path, output_path):

        logger.info("Embedding pipeline started")

        faces, labels = self.load_dataset(dataset_path)

        embeddings = self.generate_embeddings(faces)

        self.save_embeddings(output_path, embeddings, labels)

        logger.info("Embedding pipeline completed")
