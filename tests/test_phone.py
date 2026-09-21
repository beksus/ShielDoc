import unittest

from app.detectors.phone import detect_phones


class PhoneDetectorTests(unittest.TestCase):
    def test_supported_codes_and_offsets(self):
        # Artificial digit sequences, not real contact data.
        for code, length in (
            ("7", 10),
            ("992", 9),
            ("993", 8),
            ("996", 9),
            ("998", 9),
        ):
            with self.subTest(code=code):
                number = "+" + code + "0" * length
                text = f"Phone: {number}."

                entities = detect_phones(text, page=2)

                self.assertEqual(len(entities), 1)
                entity = entities[0]

                self.assertEqual(entity.type, "PHONE")
                self.assertEqual(entity.value, number)
                self.assertEqual(entity.page, 2)
                self.assertEqual(entity.start, 7)
                self.assertEqual(entity.end, 7 + len(number))
                self.assertEqual(
                    text[entity.start:entity.end],
                    number,
                )

    def test_rejects_incorrect_lengths(self):
        for code, length in (
            ("7", 10),
            ("992", 9),
            ("993", 8),
            ("996", 9),
            ("998", 9),
        ):
            for difference in (-1, 1):
                number = "+" + code + "0" * (length + difference)

                with self.subTest(number=number):
                    self.assertEqual(detect_phones(number), [])

    def test_no_phone(self):
        self.assertEqual(detect_phones("No phone number here."), [])

    def test_formatted_numbers(self):
        # Artificial sequences for testing format recognition only.
        for number in (
            "+7 000 000 00 00",
            "+992 00 000 0000",
            "+993 00 000000",
            "+996 000 000-000",
            "+998 00 000-00-00",
            "+7\u00a0000\u00a0000\u00a000\u00a000",
        ):
            with self.subTest(number=number):
                text = f"Phone: {number}."
                entities = detect_phones(text)

                self.assertEqual(len(entities), 1)

                entity = entities[0]
                self.assertEqual(entity.value, number)
                self.assertIsNone(entity.page)
                self.assertEqual(
                    text[entity.start:entity.end],
                    number,
                )

    def test_rejects_extra_digit_after_separator(self):
        text = "+7 000 000 00 00-0"

        self.assertEqual(detect_phones(text), [])

    def test_does_not_join_numbers_across_lines(self):
        text = "+7 000 000\n00 00"

        self.assertEqual(detect_phones(text), [])

    def test_parenthesized_code(self):
        for number in (
            "+7 (000) 000-00-00",
            "+7(000)0000000",
        ):
            with self.subTest(number=number):
                text = f"Phone: {number}."
                entities = detect_phones(text, page=1)

                self.assertEqual(len(entities), 1)

                entity = entities[0]
                self.assertEqual(entity.value, number)
                self.assertEqual(entity.page, 1)
                self.assertEqual(
                    text[entity.start:entity.end],
                    number,
                )

    def test_rejects_malformed_parenthesized_code(self):
        for number in (
            "+7 (000 000-00-00",
            "+7 000) 000-00-00",
            "+7 (00) 000-00-00",
            "+7 (000) 000-00-000",
        ):
            with self.subTest(number=number):
                self.assertEqual(detect_phones(number), [])