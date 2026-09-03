import unittest

from comicvine.matcher import normalize_name, filter_by_year, name_similarity

class TestMatcher(unittest.TestCase):
    def test_matcher_normalizes(self):
        input_name_1 = "BATMAN"
        input_name_2 = "batman"
        input_name_3 = "Bat-Man"
        
        self.assertEqual(
            normalize_name(input_name_1),
            normalize_name(input_name_2),
            normalize_name(input_name_3)
        )
        
    def test_removes_volumes_starting_after_issue_year(self):
        candidates = [
            {"id": 1, "name": "Batman", "start_year": 2016},
            {"id": 2, "name": "Batman", "start_year": 2022},
        ]

        result = filter_by_year(candidates, 2021)

        self.assertEqual(
            [candidate["id"] for candidate in result],
            [1]
        )
        
    def test_keeps_old_volume_for_later_issue(self):
        candidates = [
            {"id": 1, "name": "Batman", "start_year": 1940},
        ]

        result = filter_by_year(candidates, 2021)

        self.assertEqual(len(result), 1)
        
    def test_identical_names(self):
        result = name_similarity("Batman", "Batman")

        self.assertEqual(result, 1.0)

    def test_case_does_not_matter(self):
        result = name_similarity("Batman", "BATMAN")

        self.assertEqual(result, 1.0)

    def test_different_names_have_lower_similarity(self):
        result = name_similarity("Batman", "Superman")

        self.assertLess(result, 1.0)
        
if __name__ == "__main__":
    unittest.main()