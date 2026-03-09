import logging
import time
import numpy as np
from keras_facenet import FaceNet
from src.utils.config import ConfigLoader

config = ConfigLoader()

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

        # paths from config
        self.faces_dataset_path = config.get_faces_output()
        self.embedding_output_path = config.get_embedding_output()

    # --------------------------------------------------

    def load_dataset(self):

        logger.info(f"Loading dataset → {self.faces_dataset_path}")

        data = np.load(self.faces_dataset_path, allow_pickle=True)

        faces = data["arr_0"]
        labels = data["arr_1"]

        logger.info("Dataset loaded successfully")
        logger.info(f"Faces shape: {faces.shape}")
        logger.info(f"Labels shape: {labels.shape}")

        return faces, labels

    # --------------------------------------------------

    def generate_embeddings(self, faces):

        start = time.time()

        logger.info("Generating embeddings...")
        embeddings = self.embedder.embeddings(faces)

        logger.info(f"Embeddings shape: {embeddings.shape}")
        logger.info(
            f"Embedding generation completed in {time.time() - start:.2f} sec"
        )

        return embeddings

    # --------------------------------------------------

    def save_embeddings(self, embeddings, labels):

        logger.info(f"Saving embeddings → {self.embedding_output_path}")

        np.savez_compressed(self.embedding_output_path, embeddings, labels)

        logger.info("Embeddings saved successfully")

    # --------------------------------------------------

    def get_all_names(self):

        logger.info(f"Loading names from → {self.embedding_output_path}")

        data = np.load(self.embedding_output_path, allow_pickle=True)

        labels = data["arr_1"]

        names = list(set(labels))

        logger.info(f"Users found: {names}")

        return names

    # --------------------------------------------------

    def run(self):

        logger.info("Embedding pipeline started")

        faces, labels = self.load_dataset()

        embeddings = self.generate_embeddings(faces)

        self.save_embeddings(embeddings, labels)

        logger.info("Embedding pipeline completed")

    def delete_user(self, name: str):

        logger.info(f"Deleting user → {name}")

        data = np.load(self.embedding_output_path, allow_pickle=True)

        embeddings = data["arr_0"]
        labels = data["arr_1"]

        mask = labels != name

        new_embeddings = embeddings[mask]
        new_labels = labels[mask]

        if len(new_labels) == len(labels):
            return False

        np.savez_compressed(
            self.embedding_output_path,
            new_embeddings,
            new_labels
        )

        logger.info(f"User deleted: {name}")

        return True
    
    def register_user_embeddings(self, name: str, faces: np.ndarray):

        logger.info(f"Registering user → {name}")

        embeddings = self.embedder.embeddings(faces)

        data = np.load(self.embedding_output_path, allow_pickle=True)

        existing_embeddings = data["arr_0"]
        existing_labels = data["arr_1"]

        if len(existing_embeddings) == 0:
            new_embeddings = embeddings
        else:
            new_embeddings = np.vstack([existing_embeddings, embeddings])

        new_labels = np.concatenate(
            [existing_labels, np.array([name] * len(embeddings))]
        )

        np.savez_compressed(
            self.embedding_output_path,
            new_embeddings,
            new_labels
        )

        logger.info(f"User registered successfully: {name}")

        return len(embeddings)
    def reload_embeddings(self):

        logger.info("Reloading embeddings...")

        data = np.load(self.embedding_output_path, allow_pickle=True)

        self.embeddings = data["arr_0"]
        self.labels = data["arr_1"]

        logger.info(f"Embeddings reloaded. Users: {len(set(self.labels))}")