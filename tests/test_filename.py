import unittest

from comicvine.filename import ParsedFilename, parse_filename

class TestParseFilename(unittest.TestCase):
    
    def test_standard_filename(self):
        result = parse_filename(
            "Batman #1 (2021).cbz"
        )

        self.assertEqual(result.series, "Batman")
        self.assertEqual(result.issue, "1")
        self.assertEqual(result.year, 2021)

    def test_three_digit_issue(self):
        result = parse_filename(
            "Superman #453 (1957).cbz"
        )

        self.assertEqual(result.series, "Superman")
        self.assertEqual(result.issue, "453")
        self.assertEqual(result.year, 1957)

    def test_padded_issue(self):
        result = parse_filename(
            "Batman #001 (2021).cbz"
        )

        self.assertEqual(result.series, "Batman")
        self.assertEqual(result.issue, "001")
        self.assertEqual(result.year, 2021)

    def test_series_with_spaces(self):
        result = parse_filename(
            "The Amazing Spider-Man #15 (1964).cbz"
        )

        self.assertEqual(
            result.series,
            "The Amazing Spider-Man"
        )
        self.assertEqual(result.issue, "15")
        self.assertEqual(result.year, 1964)
        
    def test_invalid_filename(self):
        with self.assertRaises(ValueError):
            parse_filename("Batman.cbz")

    def test_missing_year(self):
        with self.assertRaises(ValueError):
            parse_filename("Batman #1.cbz")

    def test_issue_too_long(self):
        with self.assertRaises(ValueError):
            parse_filename("Batman #1234 (2021).cbz")
            
    def test_case_insensitive_extension(self):
        result = parse_filename(
            "Batman #1 (2021).CBZ"
        )

        self.assertEqual(result.series, "Batman")
        self.assertEqual(result.issue, "1")
        self.assertEqual(result.year, 2021)