import unittest
from comicvine.service import ComicVineService

class FakeComicVineClient:
    
    def search_volumes(self, name):
        return [
            {
                "id": 1,
                "name": "Batman",
                "start_year": "1940"
            },
            {
                "id": 2,
                "name": "Batman",
                "start_year": "2016"
            }
        ]
        
    def find_issue(self, volume_id, issue_number):
        return {
            "id": 123,
            "issue_number": issue_number
        }

    def get_volume(self, volume_id):
        return {
            "id": volume_id,
            "name": "Batman",
            "publisher": {
                "id": 10,
                "name": "DC Comics"
            }
        }

    def get_issues(self, issue_id):
        return {
            "issue_number": "1",
            "name": "The Beginning",
            "cover_date": "2021-01-01",
            "person_credits": [],
            "character_credits": [],
            "team_credits": [],
            "location_credits": [],
            "story_arc_credits": [],
            "volume": {
                "id": 2,
                "name": "Batman"
            }
        }

class TestService(unittest.TestCase):
    def test_get_volume_candidates(self):
        client = FakeComicVineClient()

        service = ComicVineService(client)

        results = service.get_volume_candidates(
            "Batman",
            2021
        )

        self.assertEqual(
            len(results),
            2
        )

        self.assertEqual(
            results[0].volume["id"],
            1
    )
        
    def test_get_comic_from_volume(self):
        client = FakeComicVineClient()

        service = ComicVineService(client)

        comic = service.get_comic_from_volume(
            volume_id=2,
            issue_number="1"
        )

        self.assertEqual(
            comic.series,
            "Batman"
        )

        self.assertEqual(
            comic.issue,
            "1"
        )

        self.assertEqual(
            comic.title,
            "The Beginning"
        )

        self.assertEqual(
            comic.year,
            2021
        )
    
    