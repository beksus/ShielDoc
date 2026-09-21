import unittest

from app.analyzer import analyze_pages


class AnalyzerTests(unittest.TestCase):
    def test_combines_email_and_phone_detections(self):
        text = "Email: demo@example.com. Phone: +7 000 000 00 00."

        entities = analyze_pages([
            {"page": 2, "text": text},
        ])

        self.assertEqual(
            [(entity.type, entity.value) for entity in entities],
            [
                ("EMAIL", "demo@example.com"),
                ("PHONE", "+7 000 000 00 00"),
            ],
        )

        for entity in entities:
            self.assertEqual(entity.page, 2)
            self.assertEqual(
                text[entity.start:entity.end],
                entity.value,
            )

    def test_handles_docx_record_without_page(self):
        entities = analyze_pages([
            {"paragraph": 1, "text": "Phone: +998 00 000-00-00"},
        ])

        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].type, "PHONE")
        self.assertIsNone(entities[0].page)

    def test_empty_input(self):
        self.assertEqual(analyze_pages([]), [])

    def test_combines_email_phone_and_inn(self):
        text = (
            "Email: demo@example.com. "
            "Phone: +7 000 000 00 00. "
            "ИНН: 0000000018."
        )

        entities = analyze_pages([
            {"page": 2, "text": text},
        ])

        self.assertEqual(
            [(entity.type, entity.value) for entity in entities],
            [
                ("EMAIL", "demo@example.com"),
                ("PHONE", "+7 000 000 00 00"),
                ("INN", "0000000018"),
            ],
        )

        for entity in entities:
            self.assertEqual(entity.page, 2)
            self.assertEqual(
                text[entity.start:entity.end],
                entity.value,
            )


    def test_combines_all_four_detectors(self):
        text = (
            "Email: demo@example.com. "
            "Phone: +7 000 000 00 00. "
            "ИНН: 0000000018. "
            "Паспорт: серия 0000 номер 000000."
        )

        entities = analyze_pages([
            {"page": 2, "text": text},
        ])

        self.assertEqual(
            [(entity.type, entity.value) for entity in entities],
            [
                ("EMAIL", "demo@example.com"),
                ("PHONE", "+7 000 000 00 00"),
                ("INN", "0000000018"),
                ("PASSPORT", "0000 номер 000000"),
            ],
        )

        for entity in entities:
            self.assertEqual(entity.page, 2)
            self.assertEqual(
                text[entity.start:entity.end],
                entity.value,
            )

    def test_passport_in_docx_record(self):
        text = "Паспорт: 0000 000000"

        entities = analyze_pages([
            {"paragraph": 1, "text": text},
        ])

        self.assertEqual(len(entities), 1)

        entity = entities[0]
        self.assertEqual(entity.type, "PASSPORT")
        self.assertEqual(entity.value, "0000 000000")
        self.assertIsNone(entity.page)
        self.assertEqual(
            text[entity.start:entity.end],
            entity.value,
        )

    def test_combines_person_and_email(self):
        # Invented name and reserved example domain.
        text = (
            "ФИО: Тестов Пример Макетович. "
            "Email: demo@example.com."
        )

        entities = analyze_pages([
            {"page": 1, "text": text},
        ])

        self.assertEqual(
            [(entity.type, entity.value) for entity in entities],
            [
                ("EMAIL", "demo@example.com"),
                ("PERSON", "Тестов Пример Макетович"),
            ],
        )

        for entity in entities:
            self.assertEqual(entity.page, 1)
            self.assertEqual(
                text[entity.start:entity.end],
                entity.value,
            )

    def test_person_in_docx_record(self):
        text = "ФИО: Тестов Пример Макетович"

        entities = analyze_pages([
            {"paragraph": 1, "text": text},
        ])

        self.assertEqual(len(entities), 1)

        entity = entities[0]
        self.assertEqual(entity.type, "PERSON")
        self.assertIsNone(entity.page)
        self.assertEqual(
            text[entity.start:entity.end],
            "Тестов Пример Макетович",
        )

    def test_combines_address_and_email(self):
        # Invented address and reserved example domain.
        address = "г. Тестоград, ул. Примерная, д. 0"
        text = (
            f"Адрес: {address}\n"
            "Email: demo@example.com"
        )

        entities = analyze_pages([
            {"page": 1, "text": text},
        ])

        self.assertEqual(
            [(entity.type, entity.value) for entity in entities],
            [
                ("EMAIL", "demo@example.com"),
                ("ADDRESS", address),
            ],
        )

        for entity in entities:
            self.assertEqual(entity.page, 1)
            self.assertEqual(
                text[entity.start:entity.end],
                entity.value,
            )

    def test_address_in_docx_record(self):
        text = "Адрес: г. Тестоград, д. 0"

        entities = analyze_pages([
            {"paragraph": 1, "text": text},
        ])

        self.assertEqual(len(entities), 1)

        entity = entities[0]
        self.assertEqual(entity.type, "ADDRESS")
        self.assertEqual(entity.value, "г. Тестоград, д. 0")
        self.assertIsNone(entity.page)
        self.assertEqual(
            text[entity.start:entity.end],
            entity.value,
        )