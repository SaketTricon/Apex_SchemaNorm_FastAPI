from functools import lru_cache
from typing import Sequence

import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
	return SentenceTransformer(MODEL_NAME)


def create_embeddings(texts: Sequence[str]) -> NDArray[np.float32]:
	if not texts:
		raise ValueError("At least one text is required to create embeddings")

	embeddings = _get_model().encode(
		list(texts),
		normalize_embeddings=True,
		convert_to_numpy=True,
		show_progress_bar=False,
	)
	return np.asarray(embeddings, dtype=np.float32)
