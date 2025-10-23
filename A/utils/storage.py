"""Storage utilities supporting MongoDB and JSON fallbacks."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pymongo import MongoClient  # type: ignore
    from pymongo.errors import PyMongoError  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    MongoClient = None  # type: ignore
    PyMongoError = Exception  # type: ignore

STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"
STORAGE_DIR.mkdir(exist_ok=True)


class StorageManager:
    """Simple abstraction over MongoDB or JSON storage backends."""

    def __init__(self, backend: str, collection: Optional[Any] = None) -> None:
        self.backend = backend
        self.collection = collection

    def save_run(
        self,
        idea_text: str,
        agents_output: Dict[str, Any],
        blueprint: Dict[str, Any],
        pitch: str = "",
    ) -> str:
        """Persist a single run and return its identifier."""

        run_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")

        record = {
            "idea_text": idea_text,
            "agents_output": agents_output,
            "blueprint": blueprint,
            "pitch": pitch,
            "created_at": datetime.utcnow().isoformat(),
        }

        if self.backend == "mongo" and self.collection is not None:
            try:
                self.collection.insert_one({"_id": run_id, **record})
                return run_id
            except PyMongoError:
                pass

        file_path = STORAGE_DIR / f"{run_id}.json"
        with file_path.open("w", encoding="utf-8") as handle:
            json.dump({"_id": run_id, **record}, handle, indent=2)
        return run_id

    def list_runs(self, limit: int = 50) -> List[Dict[str, str]]:
        """Return a reverse-chronological list of past runs."""

        if self.backend == "mongo" and self.collection is not None:
            try:
                cursor = (
                    self.collection.find({}, {"idea_text": 1, "created_at": 1})
                    .sort("created_at", -1)
                    .limit(limit)
                )
                return [
                    {
                        "id": str(doc.get("_id")),
                        "idea_text": doc.get("idea_text", ""),
                        "created_at": doc.get("created_at", ""),
                    }
                    for doc in cursor
                ]
            except PyMongoError:
                # Fall back to file listing on errors.
                pass

        runs = []
        for file in sorted(STORAGE_DIR.glob("*.json"), reverse=True):
            try:
                with file.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
                runs.append(
                    {
                        "id": str(data.get("_id", file.stem)),
                        "idea_text": data.get("idea_text", ""),
                        "created_at": data.get("created_at", ""),
                    }
                )
            except json.JSONDecodeError:
                continue
        return runs[:limit]

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single run by identifier."""

        if self.backend == "mongo" and self.collection is not None:
            try:
                doc = self.collection.find_one({"_id": run_id})
                if doc is None:
                    try:
                        from bson import ObjectId  # type: ignore

                        doc = self.collection.find_one({"_id": ObjectId(run_id)})
                    except Exception:
                        doc = None
                return doc
            except PyMongoError:
                pass

        file_path = STORAGE_DIR / f"{run_id}.json"
        if not file_path.exists():
            return None
        with file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


def get_db() -> StorageManager:
    """Return an initialized StorageManager based on environment configuration."""

    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri and MongoClient is not None:
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
            db_name = os.getenv("MONGO_DB_NAME", "akcero")
            db = client[db_name]
            collection = db["ideas"]
            # Attempt a ping to confirm connectivity.
            client.admin.command("ping")
            return StorageManager(backend="mongo", collection=collection)
        except Exception:
            pass

    return StorageManager(backend="file")
