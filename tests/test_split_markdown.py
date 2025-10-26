# -*- coding: utf-8 -*-
import unittest
from simple_rag.utils import split_markdown

class TestSplitMarkdown(unittest.TestCase):

    def test_simple_split(self):
        md = "This is a test paragraph.\n\nThis is another test paragraph."
        chunks = split_markdown(md, chunk_size=50)
        self.assertEqual(len(chunks), 2)
        self.assertTrue(chunks[0].startswith("This is a test paragraph."))
        self.assertTrue(chunks[1].startswith("This is another"))

    def test_header_split(self):
        md = "# Header 1\n\nThis is content under header 1.\n\n## Header 2\n\nThis is content under header 2."
        chunks = split_markdown(md, chunk_size=100)
        self.assertEqual(len(chunks), 2)
        self.assertTrue(chunks[0].startswith("# Header 1"))
        self.assertTrue(chunks[1].startswith("## Header 2"))

    def test_content_before_header(self):
        md = "This is some content before any header.\n\n# Header 1\n\nThis is content under header 1."
        chunks = split_markdown(md, chunk_size=100)
        self.assertEqual(len(chunks), 2)
        self.assertTrue(chunks[0].startswith("This is some content"))
        self.assertTrue(chunks[1].startswith("# Header 1"))

    def test_long_content_split(self):
        md = "# Header\n\n" + "a " * 500
        chunks = split_markdown(md, chunk_size=200)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(c.startswith("# Header") for c in chunks))

    def test_code_block(self):
        md = "```python\nprint('hello world')\n```"
        chunks = split_markdown(md)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], md)

    def test_empty_string(self):
        md = ""
        chunks = split_markdown(md)
        self.assertEqual(len(chunks), 0)

if __name__ == '__main__':
    unittest.main()
