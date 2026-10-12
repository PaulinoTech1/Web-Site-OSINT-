"""Unit tests for devtools-auto.py pure helpers.

No browser needed. Run with:
    python -m unittest discover -s tests -v
"""

import importlib.util
import os
import unittest

_spec = importlib.util.spec_from_file_location(
    "devtools_auto",
    os.path.join(os.path.dirname(__file__), "..", "devtools-auto.py"),
)
_dto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_dto)


class TestParseContentLength(unittest.TestCase):
    def test_valid_header(self):
        self.assertEqual(
            _dto.parse_content_length({"content-length": "12345"}), 12345
        )

    def test_missing_header(self):
        self.assertEqual(_dto.parse_content_length({}), 0)

    def test_malformed_header(self):
        self.assertEqual(
            _dto.parse_content_length({"content-length": "garbage"}), 0
        )

    def test_empty_header(self):
        self.assertEqual(
            _dto.parse_content_length({"content-length": ""}), 0
        )

    def test_zero_header(self):
        self.assertEqual(
            _dto.parse_content_length({"content-length": "0"}), 0
        )

    def test_returns_int(self):
        result = _dto.parse_content_length({"content-length": "99"})
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
