import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import Settings


def _sqlite_path(database_url: str) -> str:
    if database_url == "sqlite:///:memory:":
        return ":memory:"
    if database_url.startswith("sqlite:///"):
        return database_url[len("sqlite:///") :]
    raise ValueError("Only sqlite:/// database URLs are supported in this template.")


def _connect(settings: Settings) -> sqlite3.Connection:
    path = _sqlite_path(settings.database_url)
    if path != ":memory:":
        parent = Path(path).parent
        if str(parent):
            parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def initialize_storage(settings: Settings) -> None:
    with _connect(settings) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS line_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                event_type TEXT NOT NULL,
                source_id TEXT,
                message_text TEXT,
                reply_text TEXT,
                raw_event TEXT NOT NULL
            )
            """
        )
        connection.commit()


def record_event(
    settings: Settings,
    event_type: str,
    source_id: str | None,
    message_text: str | None,
    reply_text: str | None,
    raw_event: dict[str, Any],
) -> None:
    initialize_storage(settings)
    created_at = datetime.now(timezone.utc).isoformat()
    raw_event_json = json.dumps(raw_event, ensure_ascii=False, sort_keys=True)

    with _connect(settings) as connection:
        connection.execute(
            """
            INSERT INTO line_events (
                created_at,
                event_type,
                source_id,
                message_text,
                reply_text,
                raw_event
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                event_type,
                source_id,
                message_text,
                reply_text,
                raw_event_json,
            ),
        )
        connection.commit()
