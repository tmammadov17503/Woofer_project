import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Woofer.storage import (
    JsonPetProfileRepository,
    StorageConfigurationError,
    resolve_storage_config,
)


class StorageTests(unittest.TestCase):
    def test_json_repository_saves_without_mutating_input(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "registry.json"
            repo = JsonPetProfileRepository(db_path)
            payload = {
                "nickname": "Max",
                "breed_detected": "Golden Retriever",
                "health_notes": "No allergies.",
            }

            saved = repo.save(payload)

            self.assertNotIn("profile_id", payload)
            self.assertEqual(saved["nickname"], "Max")
            self.assertIn("profile_id", saved)
            self.assertIn("created_at", saved)
            self.assertEqual(repo.load_all(), [saved])

    def test_json_repository_updates_existing_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonPetProfileRepository(Path(temp_dir) / "registry.json")
            saved = repo.save({"nickname": "Bella", "weight": 12})

            updated = repo.update(saved["profile_id"], {"weight": 13})
            pets = repo.load_all()

            self.assertTrue(updated)
            self.assertEqual(pets[0]["weight"], 13)
            self.assertIn("last_updated", pets[0])

    def test_json_repository_handles_invalid_file_safely(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "registry.json"
            db_path.write_text("{broken", encoding="utf-8")
            repo = JsonPetProfileRepository(db_path)

            self.assertEqual(repo.load_all(), [])

    def test_plain_mongodb_uri_is_ignored_for_safety(self):
        with patch.dict(os.environ, {"MONGODB_URI": "mongodb://wrong-service"}, clear=True):
            config = resolve_storage_config(json_path="registry.json")

        self.assertEqual(config.backend, "json")
        self.assertIsNone(config.mongodb_uri)

    def test_mongodb_backend_requires_woofer_specific_uri(self):
        with patch.dict(os.environ, {"WOOFER_STORAGE_BACKEND": "mongodb"}, clear=True):
            with self.assertRaises(StorageConfigurationError):
                resolve_storage_config(json_path="registry.json")

    def test_auto_backend_selects_mongodb_only_for_woofer_uri(self):
        with patch.dict(
            os.environ,
            {
                "WOOFER_STORAGE_BACKEND": "auto",
                "WOOFER_MONGODB_URI": "mongodb://woofer-db",
                "WOOFER_MONGO_DB_NAME": "woofer_private_beta",
            },
            clear=True,
        ):
            config = resolve_storage_config(json_path="registry.json")

        self.assertEqual(config.backend, "mongodb")
        self.assertEqual(config.mongodb_uri, "mongodb://woofer-db")
        self.assertEqual(config.mongo_db_name, "woofer_private_beta")

    def test_json_repository_ignores_non_list_payloads(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "registry.json"
            db_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
            repo = JsonPetProfileRepository(db_path)

            self.assertEqual(repo.load_all(), [])


if __name__ == "__main__":
    unittest.main()

