import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from app.settings import get_settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    settings = get_settings()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with db() as conn:
        conn.executescript(
            """
            create table if not exists documents (
              id text primary key,
              filename text not null,
              title text not null,
              field text not null,
              status text not null,
              char_count integer not null,
              source_path text not null,
              created_at text not null,
              updated_at text not null
            );

            create table if not exists chunks (
              id text primary key,
              document_id text not null,
              chunk_index integer not null,
              text text not null,
              embedding text not null,
              token_count integer not null,
              created_at text not null,
              foreign key(document_id) references documents(id) on delete cascade
            );

            create table if not exists analysis_runs (
              id text primary key,
              document_id text not null,
              query text not null,
              mode text not null,
              result_json text not null,
              trace_json text not null,
              created_at text not null,
              foreign key(document_id) references documents(id) on delete cascade
            );
            """
        )


def dict_row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(value: str, default: Any) -> Any:
    try:
        return json.loads(value)
    except Exception:
        return default
