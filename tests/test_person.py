import unittest

from app.detectors.person import detect_persons


class PersonDetectorTests(unittest.TestCase):
    def test_labeled_name_and_offsets(self):
        # Invented test name.
        text = "ФИО: Тестов Пример Макетович."

        entities = detect_persons(text, page=2)

        self.assertEqual(len(entities), 1)
        entity = entities[0]

        self.assertEqual(entity.type, "PERSON")
        self.assertEqual(entity.value, "Тестов Пример Макетович")
        self.assertEqual(entity.page, 2)
        self.assertEqual(entity.start, 5)
        self.assertEqual(
            text[entity.start:entity.end],
            entity.value,
        )

    def test_lowercase_label_and_hyphenated_name(self):
        text = "фио: Тестов-Макетов Пример Образцович"

        entity = detect_persons(text)[0]

        self.assertEqual(
            entity.value,
            "Тестов-Макетов Пример Образцович",
        )
        self.assertIsNone(entity.page)

    def test_unsupported_formats(self):
        for text in (
            "Тестов Пример Макетович",
            "ФИО: Тестов П. М.",
            "ФИО: Тестов Пример",
            "ФИО: тестов пример макетович",
            "ФИО: Тестов Пример\nМакетович",
        ):
            with self.subTest(text=text):
                self.assertEqual(detect_persons(text), [])

    def test_empty_text(self):
        self.assertEqual(detect_persons(""), [])