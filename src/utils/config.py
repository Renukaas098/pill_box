import os


class ConfigLoader:
    def __init__(self):

        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # -------------------------------
        # paths
        # -------------------------------
        self.dataset_dir = os.path.join(base, "dataset")

        self.faces_output = os.path.join(
            base, "processed", "faces", "faces-only-dataset.npz"
        )

        self.embedding_output = os.path.join(
            base, "processed", "embeddings", "faces-embeddings.npz"
        )

        # -------------------------------
        # ensure folders exist
        # -------------------------------
        self._ensure_directory(self.dataset_dir)
        self._ensure_parent_directory(self.faces_output)
        self._ensure_parent_directory(self.embedding_output)

    # -----------------------------------
    # helpers
    # -----------------------------------

    @staticmethod
    def _ensure_directory(path):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def _ensure_parent_directory(file_path):
        parent = os.path.dirname(file_path)
        os.makedirs(parent, exist_ok=True)

    # -----------------------------------
    # getters
    # -----------------------------------

    def get_data_dir(self):
        return self.dataset_dir

    def get_faces_output(self):
        return self.faces_output

    def get_embedding_output(self):
        return self.embedding_output
