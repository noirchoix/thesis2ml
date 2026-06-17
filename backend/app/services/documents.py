import json
import re
import uuid
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader

from app.services.embeddings import embed_text
from app.services.store import db, dict_row, utc_now
from app.settings import get_settings


def clean_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", text)).strip()


def chunk_text(text: str) -> list[str]:
    settings = get_settings()
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 2 <= settings.chunk_size:
            current = f"{current}\n\n{paragraph}".strip()
            continue
        if current:
            chunks.append(current)
        if len(paragraph) <= settings.chunk_size:
            current = paragraph
        else:
            start = 0
            while start < len(paragraph):
                end = start + settings.chunk_size
                chunks.append(paragraph[start:end])
                start = max(end - settings.chunk_overlap, end)
            current = ""
    if current:
        chunks.append(current)
    return chunks


async def extract_upload_text(file: UploadFile, destination: Path) -> str:
    raw = await file.read()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    suffix = destination.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(destination))
        return clean_text("\n\n".join(page.extract_text() or "" for page in reader.pages))
    return clean_text(raw.decode("utf-8", errors="ignore"))


async def ingest_upload(file: UploadFile, field: str) -> dict:
    settings = get_settings()
    document_id = str(uuid.uuid4())
    filename = file.filename or "uploaded-thesis.txt"
    destination = settings.storage_dir / f"{document_id}_{Path(filename).name}"
    now = utc_now()

    with db() as conn:
        conn.execute(
            "insert into documents values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (document_id, filename, Path(filename).stem, field, "processing", 0, str(destination), now, now),
        )

    try:
        text = await extract_upload_text(file, destination)
        chunks = chunk_text(text)
        with db() as conn:
            conn.execute(
                "update documents set status = ?, char_count = ?, updated_at = ? where id = ?",
                ("indexed", len(text), utc_now(), document_id),
            )
            for index, chunk in enumerate(chunks):
                embedding = await embed_text(chunk)
                conn.execute(
                    "insert into chunks values (?, ?, ?, ?, ?, ?, ?)",
                    (
                        str(uuid.uuid4()),
                        document_id,
                        index,
                        chunk,
                        json.dumps(embedding),
                        max(1, len(chunk.split())),
                        utc_now(),
                    ),
                )
    except Exception:
        with db() as conn:
            conn.execute("update documents set status = ?, updated_at = ? where id = ?", ("failed", utc_now(), document_id))
        raise

    return get_document(document_id) or {"id": document_id, "status": "indexed"}


def list_documents() -> list[dict]:
    with db() as conn:
        rows = conn.execute("select * from documents order by created_at desc").fetchall()
    return [dict(row) for row in rows]


def get_document(document_id: str) -> dict | None:
    with db() as conn:
        return dict_row(conn.execute("select * from documents where id = ?", (document_id,)).fetchone())


def get_document_text(document_id: str, limit: int = 24000) -> str:
    with db() as conn:
        rows = conn.execute(
            "select text from chunks where document_id = ? order by chunk_index asc",
            (document_id,),
        ).fetchall()
    return "\n\n".join(row["text"] for row in rows)[:limit]
