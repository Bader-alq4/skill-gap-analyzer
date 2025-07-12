# averaged Sentence-BERT embeddings

from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embeddings(items: list[str]) -> np.ndarray:
    return model.encode(items, convert_to_numpy=True)

def average_embedding(items: list[str]) -> np.ndarray:
    embeds = get_embeddings(items)
    return np.mean(embeds, axis=0)
