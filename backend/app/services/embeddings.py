import hashlib
import math
from typing import Iterable

import httpx
import numpy as np

from app.settings import get_settings


def _hash_embedding(text: str, dimensions: int = 384) -> list[float]:
    vector = np.zeros(dimensions, dtype=np.float32)
    tokens = [token.strip(".,;:()[]{}").lower() for token in text.split()]
    for token in tokens:
        if len(token) < 2:
            continue
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = float(np.linalg.norm(vector))
    if norm == 0:
        vector[0] = 1.0
        norm = 1.0
    return (vector / norm).astype(float).tolist()


async def embed_text(text: str) -> list[float]:
    settings = get_settings()
    providers = [settings.embedding_provider, settings.fallback_embedding_provider]
    for provider in providers:
        try:
            if provider == "voyage" and settings.voyageai_api_key:
                async with httpx.AsyncClient(timeout=45) as client:
                    response = await client.post(
                        "https://api.voyageai.com/v1/embeddings",
                        headers={"Authorization": f"Bearer {settings.voyageai_api_key}"},
                        json={"model": settings.voyage_embedding_model, "input": [text]},
                    )
                    response.raise_for_status()
                    return response.json()["data"][0]["embedding"]
            if provider == "gemini" and settings.gemini_api_key:
                url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{settings.gemini_embedding_model}:embedContent?key={settings.gemini_api_key}"
                )
                async with httpx.AsyncClient(timeout=45) as client:
                    response = await client.post(url, json={"content": {"parts": [{"text": text}]}})
                    response.raise_for_status()
                    return response.json()["embedding"]["values"]
        except Exception:
            continue
    return _hash_embedding(text)


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    av = np.array(list(a), dtype=np.float32)
    bv = np.array(list(b), dtype=np.float32)
    denom = float(np.linalg.norm(av) * np.linalg.norm(bv))
    if denom == 0:
        return 0.0
    return float(np.dot(av, bv) / denom)


def keyword_score(query: str, text: str) -> float:
    query_terms = {term.lower().strip(".,;:()[]{}") for term in query.split() if len(term) > 2}
    if not query_terms:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for term in query_terms if term in text_lower)
    return hits / math.sqrt(len(query_terms))
