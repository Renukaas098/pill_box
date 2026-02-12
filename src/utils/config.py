import os


class ConfigLoader:
    def __init__(self):

       base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
       self.dataset_dir = os.path.join(base, "dataset")
       self.faces_output = os.path.join(
            base, "processed", "faces", "faces-only-dataset.npz"
        )
       self.embedding_output = os.path.join(
            base, "processed", "embeddings", "faces-embeddings.npz"
        )
    def get_data_dir(self):
        return self.dataset_dir

    def get_faces_output(self):
        return self.faces_output

    def get_embedding_output(self):
        return self.embedding_output
    def get_output_file(self):
        return self.output_file
