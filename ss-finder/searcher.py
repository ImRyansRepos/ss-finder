# searcher.py

from typing import List, Optional
from datetime import datetime

import numpy as np

from db import ImageDatabase, ImageRecord
from openai_client import OpenAIClient


class SearchResult:
    def __init__(self, record: ImageRecord, score: float):
        self.record = record
        self.score = score


class ImageSearcher:
    """
    Performs semantic search over indexed images using text queries.
    """

    def __init__(self, db: ImageDatabase, client: OpenAIClient):
        self.db = db
        self.client = client

    @staticmethod
    def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        denom = (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
        if denom == 0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / denom)

    def search(
        self,
        query: str,
        top_k: int = 5,
        from_datetime: Optional[datetime] = None,
        to_datetime: Optional[datetime] = None,
    ) -> List[SearchResult]:
        # Embed query
        query_embedding = np.array(self.client.embed_text(query), dtype=np.float32)

        # Get candidate images (with optional time filter)
        candidates = self.db.get_images(from_datetime=from_datetime, to_datetime=to_datetime)
        if not candidates:
            return []

        results: List[SearchResult] = []
        for rec in candidates:
            emb_vec = np.array(rec.embedding, dtype=np.float32)
            score = self._cosine_similarity(query_embedding, emb_vec)
            results.append(SearchResult(record=rec, score=score))

        # Sort by descending similarity
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
