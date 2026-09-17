import unittest

from comicvine.matcher import normalize_name, filter_by_year, name_similarity, match_volume, VolumeMatch

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
        
    def test_matches_clear_best_candidate(self):
        candidates = [
            {
                "id": 1,
                "name": "Batman",
                "start_year": 2016
            },
            {
                "id": 2,
                "name": "Superman",
                "start_year": 2016
            }
        ]

        result = match_volume(
            "Batman",
            2021,
            candidates
        )

        self.assertEqual(result.status, "matched")
        self.assertEqual(result.volume["id"], 1)
    
    def test_no_match_when_score_is_too_low(self):
        candidates = [
            {
                "id": 1,
                "name": "Superman",
                "start_year": 2016
            }
        ]

        result = match_volume(
            "Batman",
            2021,
            candidates
        )

        self.assertEqual(result.status, "no_match")
        self.assertIsNone(result.volume)
        
    def test_ambiguous_when_candidates_are_too_close(self):
        candidates = [
            {
                "id": 1,
                "name": "Batman",
                "start_year": 2016
            },
            {
                "id": 2,
                "name": "Batman",
                "start_year": 2011
            }
        ]

        result = match_volume(
            "Batman",
            2021,
            candidates
        )

        self.assertEqual(result.status, "ambiguous")
        self.assertIsNone(result.volume)
        
    def test_ignores_volume_starting_after_issue_year(self):
        candidates = [
            {
                "id": 1,
                "name": "Batman",
                "start_year": 2022
            },
            {
                "id": 2,
                "name": "Batman",
                "start_year": 2016
            }
        ]

        result = match_volume(
            "Batman",
            2021,
            candidates
        )

        self.assertEqual(result.status, "matched")
        self.assertEqual(result.volume["id"], 2)
        
    def test_old_volume_can_match_later_issue(self):
        candidates = [
            {
                "id": 1,
                "name": "Batman",
                "start_year": 1940
            }
        ]
        
        result = match_volume(
            "Batman",
            2021,
            candidates
        )
        
        self.assertEqual(result.status, "matched")
        self.assertEqual(result.volume["id"], 1)
        
    def test_clear_score_difference_produces_match(self):
        candidates = [
            {
                "id": 1,
                "name": "Batman",
                "start_year": 2016
            },
            {
                "id": 2,
                "name": "Batman Beyond",
                "start_year": 2016
            }
        ]

        result = match_volume(
            "Batman",
            2021,
            candidates
        )

        self.assertEqual(result.status, "matched")
        self.assertEqual(result.volume["id"], 1)
        
    def test_candidate_without_name_does_not_crash(self):
        candidates = [
            {
                "id": 1,
                "start_year": 2016
            }
        ]

        result = match_volume(
            "Batman",
            2021,
            candidates
        )

        self.assertEqual(result.status, "no_match")
        
    def test_missing_start_year_is_not_rejected(self):
        candidates = [
            {
                "id": 1,
                "name": "Batman",
                "start_year": None
            }
        ]

        result = match_volume(
            "Batman",
            2021,
            candidates
        )

        self.assertEqual(result.status, "matched")
        self.assertEqual(result.volume["id"], 1)
        
    def test_no_candidates_returns_no_match(self):
        result = match_volume(
            "Batman",
            2021,
            []
        )

        self.assertEqual(result.status, "no_match")
        self.assertIsNone(result.volume)
        self.assertEqual(result.score, 0)
        
    def test_string_start_year_is_handled(self):
        candidates = [
            {
                "id": 1,
                "name": "Batman",
                "start_year": "2016"
            }
        ]

        result = filter_by_year(candidates, 2021)

        self.assertEqual(len(result), 1)
        
    def test_invalid_start_year_is_kept(self):
        candidates = [
            {
                "id": 1,
                "name": "Batman",
                "start_year": "unknown"
            }
        ]

        result = filter_by_year(candidates, 2021)

        self.assertEqual(len(result), 1)
        
    def test_missing_start_year_is_kept(self):
        candidates = [
            {
                "id": 1,
                "name": "Batman"
            }
        ]

        result = filter_by_year(candidates, 2021)

        self.assertEqual(len(result), 1)
        
if __name__ == "__main__":
    unittest.main()