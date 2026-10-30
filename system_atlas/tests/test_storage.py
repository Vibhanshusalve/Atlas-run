import unittest
from pathlib import Path
import tempfile
import shutil

import sys
sys.path.insert(0, './system_atlas')
from utils.storage import create_scan_directory, save_json
import json

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_scan_directory(self):
        scan_dir = create_scan_directory(self.test_dir)
        self.assertTrue(scan_dir.exists())
        self.assertTrue(scan_dir.is_dir())

    def test_save_json(self):
        data = {"key": "value"}
        filepath = Path(self.test_dir) / "test.json"
        save_json(data, filepath)

        self.assertTrue(filepath.exists())
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(data, loaded)

if __name__ == '__main__':
    unittest.main()
