import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


DEFAULT_DB_FILE = "woofer_care_registry.json"
DEFAULT_MONGO_DB_NAME = "woofer"
DEFAULT_MONGO_COLLECTION = "pet_profiles"
SUPPORTED_BACKENDS = {"auto", "json", "mongodb"}


class StorageConfigurationError(RuntimeError):
    """Raised when the requested storage backend cannot be configured safely."""


@dataclass(frozen=True)
class StorageConfig:
    backend: str
    json_path: Path
    mongodb_uri: Optional[str] = None
    mongo_db_name: str = DEFAULT_MONGO_DB_NAME
    mongo_collection: str = DEFAULT_MONGO_COLLECTION


def _now_iso() -> str:
    return datetime.now().isoformat()


def _new_profile_id() -> str:
    return str(uuid.uuid4())[:8].upper()


def _safe_secret_get(secrets: Any, key: str, default: Optional[str] = None) -> Optional[str]:
    if secrets is None:
        return default

    try:
        value = secrets.get(key)
        if value:
            return str(value)
    except Exception:
        pass

    try:
        storage_section = secrets.get("storage")
        if storage_section:
            value = storage_section.get(key)
            if value:
                return str(value)
    except Exception:
        pass

    return default


def _setting(secrets: Any, key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key) or _safe_secret_get(secrets, key, default)


def resolve_storage_config(
    json_path: str = DEFAULT_DB_FILE,
    secrets: Any = None,
) -> StorageConfig:
    requested_backend = (_setting(secrets, "WOOFER_STORAGE_BACKEND", "json") or "json").lower()
    if requested_backend not in SUPPORTED_BACKENDS:
        raise StorageConfigurationError(
            f"Unsupported WOOFER_STORAGE_BACKEND '{requested_backend}'. "
            "Use 'json', 'mongodb', or 'auto'."
        )

    mongodb_uri = _setting(secrets, "WOOFER_MONGODB_URI")
    backend = "mongodb" if requested_backend == "auto" and mongodb_uri else requested_backend
    if backend == "auto":
        backend = "json"

    if backend == "mongodb" and not mongodb_uri:
        raise StorageConfigurationError(
            "MongoDB storage requires WOOFER_MONGODB_URI. "
            "Do not reuse generic MONGODB_URI values from other bots or services."
        )

    return StorageConfig(
        backend=backend,
        json_path=Path(json_path),
        mongodb_uri=mongodb_uri,
        mongo_db_name=_setting(secrets, "WOOFER_MONGO_DB_NAME", DEFAULT_MONGO_DB_NAME)
        or DEFAULT_MONGO_DB_NAME,
        mongo_collection=_setting(secrets, "WOOFER_MONGO_COLLECTION", DEFAULT_MONGO_COLLECTION)
        or DEFAULT_MONGO_COLLECTION,
    )


class JsonPetProfileRepository:
    public_label = "Local JSON"

    def __init__(self, json_path: Path):
        self.json_path = json_path

    def save(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        db = self.load_all()
        saved_profile = {
            **dict(data),
            "created_at": _now_iso(),
            "profile_id": _new_profile_id(),
        }
        self._write_all([*db, saved_profile])
        return saved_profile

    def load_all(self) -> List[Dict[str, Any]]:
        if not self.json_path.exists():
            return []

        try:
            with self.json_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return []

        if not isinstance(data, list):
            return []

        return [item for item in data if isinstance(item, dict)]

    def update(self, profile_id: str, updates: Mapping[str, Any]) -> bool:
        pets = self.load_all()
        updated_pets = []
        found = False

        for pet in pets:
            if pet.get("profile_id") == profile_id:
                updated_pets.append({
                    **pet,
                    **dict(updates),
                    "last_updated": _now_iso(),
                })
                found = True
            else:
                updated_pets.append(pet)

        if found:
            self._write_all(updated_pets)

        return found

    def _write_all(self, pets: List[Dict[str, Any]]) -> None:
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.json_path.with_suffix(f"{self.json_path.suffix}.tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(pets, handle, indent=4, ensure_ascii=False)
        temp_path.replace(self.json_path)


class MongoPetProfileRepository:
    public_label = "MongoDB"

    def __init__(self, config: StorageConfig):
        try:
            from pymongo import MongoClient
        except ImportError as exc:
            raise StorageConfigurationError(
                "MongoDB storage requires pymongo. Install requirements.txt before enabling it."
            ) from exc

        self.client = MongoClient(config.mongodb_uri, serverSelectionTimeoutMS=5000)
        self.collection = self.client[config.mongo_db_name][config.mongo_collection]
        self.collection.create_index("profile_id", unique=True)

    def save(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        saved_profile = {
            **dict(data),
            "created_at": _now_iso(),
            "profile_id": _new_profile_id(),
        }
        self.collection.insert_one(dict(saved_profile))
        return saved_profile

    def load_all(self) -> List[Dict[str, Any]]:
        records = self.collection.find({}, {"_id": 0}).sort("created_at", 1)
        return [dict(record) for record in records]

    def update(self, profile_id: str, updates: Mapping[str, Any]) -> bool:
        update_doc = {
            **dict(updates),
            "last_updated": _now_iso(),
        }
        result = self.collection.update_one(
            {"profile_id": profile_id},
            {"$set": update_doc},
            upsert=False,
        )
        return result.matched_count > 0


def create_pet_profile_repository(
    json_path: str = DEFAULT_DB_FILE,
    secrets: Any = None,
):
    config = resolve_storage_config(json_path=json_path, secrets=secrets)
    if config.backend == "mongodb":
        return MongoPetProfileRepository(config)
    return JsonPetProfileRepository(config.json_path)
