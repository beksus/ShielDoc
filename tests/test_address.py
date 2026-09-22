import unittest

from app.detectors.address import detect_addresses


class AddressDetectorTests(unittest.TestCase):
    def test_labeled_address_and_offsets(self):
        # Invented address.
        value = "г. Тестоград, ул. Примерная, д. 0"
        text = f"Контакты\nАдрес: {value}  \nКонец"

        entities = detect_addresses(text, page=2)

        self.assertEqual(len(entities), 1)
        entity = entities[0]

        self.assertEqual(entity.type, "ADDRESS")
        self.assertEqual(entity.value, value)
        self.assertEqual(entity.page, 2)
        self.assertEqual(entity.start, text.index(value))
        self.assertEqual(
            text[entity.start:entity.end],
            value,
        )

    def test_indented_uppercase_label(self):
        entity = detect_addresses(
            "  АДРЕС:\tг. Тестоград, д. 0"
        )[0]

        self.assertEqual(entity.value, "г. Тестоград, д. 0")
        self.assertIsNone(entity.page)

    def test_rejects_empty_or_unlabeled_values(self):
        for text in (
            "",
            "Адрес:   ",
            "Адрес:\n",
            "г. Тестоград, д. 0",
            "Наш адрес: г. Тестоград, д. 0",
        ):
            with self.subTest(text=text):
                self.assertEqual(detect_addresses(text), [])

    def test_ignores_exact_redaction_marker(self):
        self.assertEqual(
            detect_addresses("Адрес: [REDACTED]"),
            [],
        )

        # Additional address text must still be detected.
        text = "Адрес: [REDACTED], кв. 0"
        entities = detect_addresses(text)

        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].value, "[REDACTED], кв. 0")