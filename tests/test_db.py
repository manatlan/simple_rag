# -*- coding: utf-8 -*-
import unittest
import os
import shutil
from simple_rag.rag_db import DB

class TestDB(unittest.TestCase):

    def setUp(self):
        # Create a unique path for each test to ensure isolation
        self.db_path = f".test_db_{unittest.TestCase.id(self)}"
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path)
        self.db = DB("TestDB", path=self.db_path)
        self.test_file = "test_doc.md"
        with open(self.test_file, "w") as f:
            f.write("# Test Document\n\nThis is a test document.")

    def tearDown(self):
        # Clean up the unique database directory and test file
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path, ignore_errors=True)
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_db_initialization(self):
        self.assertIsNotNone(self.db)
        self.assertTrue(os.path.exists(self.db_path))

    def test_feed_and_find(self):
        self.db.feed("test_source", "# Title\n\nSome content.")
        results = self.db.find("content")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source, "test_source")
        self.assertIn("Some content", results[0].content)

    def test_feed_file(self):
        self.db.feed_file(self.test_file)
        results = self.db.find("document")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source, self.test_file)

    def test_feed_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.db.feed_file("non_existent_file.md")

    def test_repr(self):
        self.db.feed("source1", "content1")
        self.db.feed("source2", "content2")
        self.assertIn("source1", repr(self.db))
        self.assertIn("source2", repr(self.db))

if __name__ == '__main__':
    unittest.main()
