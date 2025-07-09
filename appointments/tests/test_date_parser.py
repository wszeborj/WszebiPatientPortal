from datetime import date

from django.test import TestCase

from appointments.services.date_parser import try_parsing_date


class TryParsingDateTests(TestCase):
    def test_valid_short_month_with_dot(self):
        result = try_parsing_date("Jun. 04, 2025")
        self.assertEqual(result, date(2025, 6, 4))

    def test_valid_short_month_without_dot(self):
        result = try_parsing_date("Jun 04, 2025")
        self.assertEqual(result, date(2025, 6, 4))

    def test_valid_full_month(self):
        result = try_parsing_date("June 04, 2025")
        self.assertEqual(result, date(2025, 6, 4))

    def test_invalid_format_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            try_parsing_date("2025-06-04")
        self.assertIn("Non-valid date format", str(context.exception))

    def test_completely_invalid_input(self):
        with self.assertRaises(ValueError):
            try_parsing_date("this is not a date")

    def test_valid_date_with_extra_whitespace(self):
        result = try_parsing_date("  Jun 04, 2025 ")
        self.assertEqual(result, date(2025, 6, 4))
