# db.py

import sqlite3
import pickle
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime


class ImageRecord:
    def __init__(
        self,
        image_id: int,
        path: str,
        caption: str,
        created_at: datetime,
        embedding: List[float],
    ):
        self.id = image_id
        self.path = path
        self.caption = caption
        self.created_at = created_at
        self.embedding = embedding


class ImageDatabase:
    """
    Handles storage and retrieval of image metadata + embeddings in SQLite.
    """

    def __init__(self, db_path: str = "images.db"):
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    caption TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    embedding BLOB NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def add_image(
        self,
        path: str,
        caption: str,
        created_at: datetime,
        embedding: List[float],
    ) -> None:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT OR IGNORE INTO images (path, caption, created_at, embedding)
                VALUES (?, ?, ?, ?)
                """,
                (
                    path,
                    caption,
                    created_at.isoformat(),
                    pickle.dumps(embedding),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def has_image(self, path: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM images WHERE path = ? LIMIT 1",
                (path,),
            )
            row = cur.fetchone()
            return row is not None
        finally:
            conn.close()

    def get_images(
        self,
        from_datetime: Optional[datetime] = None,
        to_datetime: Optional[datetime] = None,
    ) -> List[ImageRecord]:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            query = "SELECT id, path, caption, created_at, embedding FROM images"
            params: Tuple = ()

            if from_datetime and to_datetime:
                query += " WHERE created_at BETWEEN ? AND ?"
                params = (from_datetime.isoformat(), to_datetime.isoformat())
            elif from_datetime:
                query += " WHERE created_at >= ?"
                params = (from_datetime.isoformat(),)
            elif to_datetime:
                query += " WHERE created_at <= ?"
                params = (to_datetime.isoformat(),)

            cur.execute(query, params)
            rows = cur.fetchall()

            records: List[ImageRecord] = []
            for row in rows:
                image_id, path, caption, created_at_str, emb_blob = row
                created_at = datetime.fromisoformat(created_at_str)
                embedding = pickle.loads(emb_blob)
                records.append(
                    ImageRecord(
                        image_id=image_id,
                        path=path,
                        caption=caption,
                        created_at=created_at,
                        embedding=embedding,
                    )
                )
            return records
        finally:
            conn.close()
