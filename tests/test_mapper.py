import unittest

from comicvine.mapper import issue_to_comic, map_person_credits, parse_cover_date, extract_publisher_name

ISSUE = {
    "character_credits": [
        {
            "id": 1699,
            "name": "Batman"
        }
    ],
    "cover_date": "2017-05-31",
    "description": "<p>Translates Batman #1-2.</p>",
    "id": 664516,
    "issue_number": "1",
    "location_credits": [],
    "name": None,
    "person_credits": [
        {
            "name": "David Finch",
            "role": "penciler, cover"
        },
        {
            "name": "Jordie Bellaire",
            "role": "colorist, cover"
        },
        {
            "name": "Ralph Kruhm",
            "role": "translator"
        },
        {
            "name": "Tom King",
            "role": "writer"
        },
        {
            "name": "Walproject",
            "role": "letterer"
        }
    ],
    "site_detail_url": "https://comicvine.gamespot.com/batman-1/4000-664516/",
    "story_arc_credits": [],
    "team_credits": [],
    "volume": {
        "id": 109498,
        "name": "Batman"
    }
}

VOLUME = {
    "id": 109498,
    "name": "Batman",
    "start_year": "2016",
    "publisher": {
        "id": 10,
        "name": "DC Comics"
    }
}

class TestMapper(unittest.TestCase):
    def test_issue_to_comic(self):
        comic = issue_to_comic(ISSUE, VOLUME)

        self.assertEqual(comic.series, "Batman")
        self.assertEqual(comic.issue, "1")
        self.assertIsNone(comic.title)

        self.assertEqual(comic.day, 31)
        self.assertEqual(comic.month, 5)
        self.assertEqual(comic.year, 2017)

        self.assertEqual(comic.characters, ["Batman"])

        self.assertEqual(
            comic.writers,
            ["Tom King"]
        )

        self.assertEqual(
            comic.pencillers,
            ["David Finch"]
        )

        self.assertEqual(
            comic.colorists,
            ["Jordie Bellaire"]
        )

        self.assertEqual(
            comic.letterers,
            ["Walproject"]
        )

        self.assertEqual(
            comic.translators,
            ["Ralph Kruhm"]
        )

        self.assertEqual(
            comic.cover_artists,
            ["David Finch", "Jordie Bellaire"]
        )
        
    def test_person_with_multiple_roles(self):
        credits = [
            {
                "name": "David Finch",
                "role": "penciler, cover"
            }
        ]

        result = map_person_credits(credits)

        self.assertEqual(
            result["pencillers"],
            ["David Finch"]
        )

        self.assertEqual(
            result["cover_artists"],
            ["David Finch"]
        )
        
    def test_parse_cover_date(self):
        result = parse_cover_date("2017-05-31")

        self.assertEqual(
            result,
            (31, 5, 2017)
        )
        
    def test_parse_cover_date_missing(self):
        result = parse_cover_date(None)

        self.assertEqual(
            result,
            (None, None, None)
        )
        
    def test_parse_cover_date_invalid(self):
        result = parse_cover_date("not-a-date")

        self.assertEqual(
            result,
            (None, None, None)
        )
        
    def test_extract_publisher_name(self):
        volume = {
            "publisher": {
                "id": 10,
                "name": "DC Comics"
            }
        }

        result = extract_publisher_name(volume)

        self.assertEqual(result, "DC Comics")
        
    def test_extract_publisher_name_missing(self):
        volume = {
            "publisher": None
        }

        result = extract_publisher_name(volume)

        self.assertIsNone(result)