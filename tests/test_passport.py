import unittest

from app.detectors.passport import detect_passports


class PassportDetectorTests(unittest.TestCase):
    def test_supported_formats(self):
        # Synthetic placeholders, not real passport details.
        cases = (
            ("Паспорт: 0000 000000", "0000 000000"),
            ("Паспорт 00 00 000000", "00 00 000000"),
            ("ПАСПОРТ № 0000 000000", "0000 000000"),
            ("Паспорт:\u00a00000\u00a0000000", "0000\u00a0000000"),
        )

        for text, expected in cases:
            with self.subTest(text=text):
                entities = detect_passports(text, page=2)

                self.assertEqual(len(entities), 1)
                entity = entities[0]

                self.assertEqual(entity.type, "PASSPORT")
                self.assertEqual(entity.value, expected)
                self.assertEqual(entity.page, 2)
                self.assertEqual(entity.start, text.index(expected))
                self.assertEqual(
                    text[entity.start:entity.end],
                    expected,
                )

    def test_requires_passport_label(self):
        for text in (
            "0000 000000",
            "ИНН: 0000000018",
            "Заказ: 0000 000000",
            "Загранпаспорт: 0000 000000",
        ):
            with self.subTest(text=text):
                self.assertEqual(detect_passports(text), [])

    def test_rejects_wrong_lengths(self):
        for text in (
            "Паспорт: 000 000000",
            "Паспорт: 00000 000000",
            "Паспорт: 0000 00000",
            "Паспорт: 0000 0000000",
        ):
            with self.subTest(text=text):
                self.assertEqual(detect_passports(text), [])

    def test_default_page_is_none(self):
        entity = detect_passports("Паспорт: 0000 000000")[0]

        self.assertIsNone(entity.page)

    def test_explicit_series_and_number_labels(self):
        cases = (
            (
                "Паспорт: серия 0000 номер 000000",
                "0000 номер 000000",
            ),
            (
                "Паспорт серия 00 00 № 000000",
                "00 00 № 000000",
            ),
        )

        for text, expected in cases:
            with self.subTest(text=text):
                entities = detect_passports(text)

                self.assertEqual(len(entities), 1)
                entity = entities[0]

                self.assertEqual(entity.value, expected)
                self.assertEqual(entity.start, text.index(expected))
                self.assertEqual(
                    text[entity.start:entity.end],
                    expected,
                )