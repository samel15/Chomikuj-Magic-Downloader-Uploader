#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from chomikuj.common_local_name import encode_local_component


WINDOWS_FORBIDDEN_CHARS = '<>:"/\\|?*'


class EncodeLocalComponentTest(unittest.TestCase):
    def test_preserves_safe_unicode_and_extension(self):
        cases = {
            "Edyta Górniak.rar": "Edyta Górniak.rar",
            "Maanam - Wyjątkowo Zimny Maj [VIDEO].zip": "Maanam - Wyjątkowo Zimny Maj [VIDEO].zip",
            "Czesław Niemen - Sen o Warszawie.zip": "Czesław Niemen - Sen o Warszawie.zip",
            "Zażółć gęślą jaźń.rar": "Zażółć gęślą jaźń.rar",
        }

        for original, expected in cases.items():
            with self.subTest(original=original):
                self.assertEqual(encode_local_component(original, allow_extension=True), expected)

    def test_encodes_each_windows_forbidden_character(self):
        encoded = encode_local_component(f"a{WINDOWS_FORBIDDEN_CHARS}b", allow_extension=True)

        for char in WINDOWS_FORBIDDEN_CHARS:
            with self.subTest(char=char):
                self.assertNotIn(char, encoded)

        self.assertEqual(encoded, "a~3c~3e~3a~22~2f~5c~7c~3f~2ab")

    def test_encodes_leading_and_trailing_dots_and_spaces(self):
        self.assertEqual(encode_local_component(" file .txt", allow_extension=True), "~20file~20.txt")
        self.assertEqual(encode_local_component(".file.txt", allow_extension=True), "~2efile.txt")
        self.assertEqual(encode_local_component("file. .txt", allow_extension=True), "file.~20.txt")
        self.assertEqual(encode_local_component("file .txt", allow_extension=True), "file~20.txt")

    def test_encodes_reserved_windows_names_before_extension(self):
        cases = {
            "CON": "~43ON",
            "con.txt": "~63on.txt",
            "con.rar": "~63on.rar",
            "CON.tar.gz": "~43ON.tar.gz",
            "AUX.backup.old": "~41UX.backup.old",
            "NUL.foo.bar": "~4eUL.foo.bar",
            "NUL.rar": "~4eUL.rar",
            "COM1.archive.zip": "~43OM1.archive.zip",
            "COM1.zip": "~43OM1.zip",
            "lpt9.foo.txt": "~6cpt9.foo.txt",
            "lpt9": "~6cpt9",
            "COM¹": "~43OM¹",
            "COM².txt": "~43OM².txt",
            "COM³.archive.zip": "~43OM³.archive.zip",
            "LPT¹": "~4cPT¹",
            "LPT².txt": "~4cPT².txt",
            "LPT³.rar": "~4cPT³.rar",
        }

        for original, expected in cases.items():
            with self.subTest(original=original):
                self.assertEqual(encode_local_component(original, allow_extension=True), expected)

    def test_sanitized_names_can_be_created_on_filesystem(self):
        names = [
            "Edyta Górniak.rar",
            f"a{WINDOWS_FORBIDDEN_CHARS}b.zip",
            "CON.tar.gz",
            " file .txt",
        ]

        with tempfile.TemporaryDirectory() as tmp:
            for name in names:
                with self.subTest(name=name):
                    encoded_name = encode_local_component(name, allow_extension=True)
                    path = Path(tmp) / encoded_name
                    path.touch()
                    self.assertTrue(path.exists())

    def test_escapes_tilde_to_avoid_collisions(self):
        self.assertEqual(encode_local_component("a~3cb.txt", allow_extension=True), "a~7e3cb.txt")
        self.assertEqual(encode_local_component("a<b.txt", allow_extension=True), "a~3cb.txt")


if __name__ == "__main__":
    unittest.main()
