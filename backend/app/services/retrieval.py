import json

from app.services.embeddings import cosine_similarity, embed_text, keyword_score
from app.services.store import db
from app.settings import get_settings


async def retrieve(document_id: str, query: str, top_k: int | None = None) -> tuple[list[dict], dict]:
    settings = get_settings()
    limit = top_k or settings.top_k
    query_embedding = await embed_text(query)

    with db() as conn:
        rows = conn.execute(
            "select id, chunk_index, text, embedding from chunks where document_id = ?",
            (document_id,),
        ).fetchall()

    scored = []
    for row in rows:
        embedding = json.loads(row["embedding"])
        vector = cosine_similarity(query_embedding, embedding)
        keyword = keyword_score(query, row["text"])
        combined = (0.72 * vector) + (0.28 * keyword)
        scored.append(
            {
                "chunk_id": row["id"],
                "chunk_index": row["chunk_index"],
                "text": row["text"],
                "score": round(combined, 4),
                "vector_score": round(vector, 4),
                "keyword_score": round(keyword, 4),
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    results = scored[:limit]
    trace = {
        "mode": "hybrid_vector_keyword",
        "candidates": len(scored),
        "returned": len(results),
        "top_chunks": [
            {
                "chunk_index": item["chunk_index"],
                "score": item["score"],
                "vector_score": item["vector_score"],
                "keyword_score": item["keyword_score"],
            }
            for item in results
        ],
    }
    return results, trace
