class CPUEmbeddingFunction:
    def __init__(self, model):
        self.model = model

    def __call__(self, input):
        """
        Encode a list of strings into embeddings.
        Must return list[list[float]] for ChromaDB compatibility.
        """
        embeddings = self.model.encode(input, convert_to_tensor=False)
        return embeddings.tolist()

    def name(self):
        return "CPUEmbeddingFunction"
