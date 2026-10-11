import tempfile
import unittest
from pathlib import Path

from app.settings import DeepSeekSettings, SettingsStore


class SettingsTests(unittest.TestCase):
    def test_store_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            store = SettingsStore(path)
            store.save(DeepSeekSettings("key", "https://example.com", "model-a"))
            loaded = store.load()
        self.assertEqual(loaded.api_key, "key")
        self.assertEqual(loaded.model, "model-a")


if __name__ == "__main__":
    unittest.main()
