import unittest

from app.detectors.inn import has_valid_inn_checksum
from app.detectors.inn import detect_inns, has_valid_inn_checksum


class INNChecksumTests(unittest.TestCase):
    def test_accepts_correct_checksums(self):
        # Artificial checksum fixtures, not assigned taxpayer identifiers.
        for number in ("0000000018", "000000000184"):
            with self.subTest(number=number):
                self.assertTrue(has_valid_inn_checksum(number))

    def test_rejects_wrong_checksums(self):
        for number in (
            "0000000019",    # Wrong check digit.
            "000000000185",  # Wrong second check digit.
            "000000000194",  # Wrong first check digit.
        ):
            with self.subTest(number=number):
                self.assertFalse(has_valid_inn_checksum(number))

    def test_rejects_invalid_input(self):
        for number in (
            "",
            "123",
            "12345678901",
            "abcdefghij",
            "0000000000",
            "000000000000",
        ):
            with self.subTest(number=number):
                self.assertFalse(has_valid_inn_checksum(number))

class INNDetectorTests(unittest.TestCase):
    def test_detects_candidates_with_correct_offsets(self):
        # Artificial checksum fixtures, not assigned taxpayer identifiers.
        text = "ИНН: 0000000018; ИНН: 000000000184."

        entities = detect_inns(text, page=3)

        self.assertEqual(
            [entity.value for entity in entities],
            ["0000000018", "000000000184"],
        )

        for entity in entities:
            self.assertEqual(entity.type, "INN")
            self.assertEqual(entity.page, 3)
            self.assertEqual(
                text[entity.start:entity.end],
                entity.value,
            )

    def test_rejects_wrong_checksum(self):
        self.assertEqual(detect_inns("ИНН: 0000000019"), [])

    def test_rejects_embedded_candidates(self):
        for text in (
            "00000000180",
            "0000000001840",
            "abc0000000018",
            "0000000018abc",
            "+0000000018",
        ):
            with self.subTest(text=text):
                self.assertEqual(detect_inns(text), [])

    def test_no_inn(self):
        self.assertEqual(detect_inns("No tax identifier here."), [])