# indexer.py

import os
from datetime import datetime
from pathlib import Path
from typing import Iterable

from concurrent.futures import ThreadPoolExecutor, as_completed

from db import ImageDatabase
from openai_client import OpenAIClient


class ImageIndexer:
    """
    Walks a directory, finds .png/.jpg images, generates captions + embeddings,
    and stores them in the database. Supports parallel processing.
    """

    VALID_EXTENSIONS = {".png", ".jpg", ".jpeg"}

    def __init__(self, db: ImageDatabase, client: OpenAIClient):
        self.db = db
        self.client = client

    def _iter_image_files(self, root_dir: str) -> Iterable[str]:
        root = Path(root_dir)
        if not root.exists():
            raise FileNotFoundError(f"Directory not found: {root_dir}")

        print(f"Scanning for images under: {root_dir}")
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                ext = Path(name).suffix.lower()
                if ext in self.VALID_EXTENSIONS:
                    yield str(Path(dirpath) / name)

    def _process_single_image(self, path: str) -> str:
        """
        Worker function for a single image path.
        Returns a short status string for logging.
        """
        if self.db.has_image(path):
            return f"[SKIP] Already indexed: {path}"

        # Get file modification time as created_at
        stat = os.stat(path)
        created_at = datetime.utcfromtimestamp(stat.st_mtime)

        try:
            caption = self.client.caption_image(path)
            embedding = self.client.embed_text(caption)
            self.db.add_image(path, caption, created_at, embedding)
            return f"[OK] {path} | {caption}"
        except Exception as e:
            return f"[ERROR] {path} | {e}"

    def index_directory(self, root_dir: str, max_workers: int = 4) -> None:
        """
        Index images in a directory using a pool of worker threads.
        max_workers controls how many requests run in parallel.
        Shows progress while scanning.
        """
        # Discover images with progress
        paths = []
        count = 0
        for p in self._iter_image_files(root_dir):
            paths.append(p)
            count += 1
            if count % 50 == 0:
                print(f"Found {count} images so far...")

        total = len(paths)
        if total == 0:
            print(f"No .png/.jpg images found in {root_dir}")
            return

        print(f"Found {total} images in {root_dir}. Indexing with {max_workers} workers...")

        completed = 0
        skipped = 0
        errors = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {executor.submit(self._process_single_image, p): p for p in paths}
            for future in as_completed(future_to_path):
                msg = future.result()
                print(msg)

                if msg.startswith("[SKIP]"):
                    skipped += 1
                elif msg.startswith("[ERROR]"):
                    errors += 1
                else:
                    completed += 1

        print("\n=== Indexing summary ===")
        print(f"Indexed: {completed}")
        print(f"Skipped (already in DB): {skipped}")
        print(f"Errors: {errors}")
        print(f"Total seen: {total}")
