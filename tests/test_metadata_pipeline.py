import unittest

from comicvine.filename import ParsedFilename
from comicvine.matcher import VolumeCandidate
from models.overrides import MetadataOverrides
from models.comic import Comic
from pipeline.metadata import MetadataPipeline

class FakeComicVineService:

    def __init__(self):
        self.get_volume_candidates_calls = []
        self.get_comic_from_volume_calls = []

    def get_volume_candidates(
        self,
        series: str,
        issue_year: int
    ):
        self.get_volume_candidates_calls.append(
            (series, issue_year)
        )

        return [
            VolumeCandidate(
                volume={
                    "id": 123,
                    "name": "Batman",
                    "start_year": 2021
                },
                score=1.0
            )
        ]

    def get_comic_from_volume(
        self,
        volume_id: int,
        issue_number: str
    ):
        self.get_comic_from_volume_calls.append(
            (volume_id, issue_number)
        )

        return Comic(
            series="Batman",
            issue=issue_number,
            year=2021,
            publisher="DC Comics"
        )
        
class TestMetadataPipeline(unittest.TestCase):

    def test_identify(self):
        service = FakeComicVineService()
        pipeline = MetadataPipeline(service)

        result = pipeline.identify(
            "Batman #1 (2021).cbz"
        )

        self.assertEqual(
            result.parsed.series,
            "Batman"
        )

        self.assertEqual(
            result.parsed.issue,
            "1"
        )

        self.assertEqual(
            result.parsed.year,
            2021
        )

        self.assertEqual(
            len(result.candidates),
            1
        )

        self.assertEqual(
            service.get_volume_candidates_calls,
            [("Batman", 2021)]
        )
        
    def test_build_comic(self):
        service = FakeComicVineService()
        pipeline = MetadataPipeline(service)

        identification = pipeline.identify(
            "Batman #1 (2021).cbz"
        )

        comic = pipeline.build_comic(
            identification,
            volume_id=123
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
            comic.publisher,
            "DC Comics"
        )

        self.assertEqual(
            service.get_comic_from_volume_calls,
            [(123, "1")]
        )
        
    def test_build_comic_with_overrides(self):
        service = FakeComicVineService()
        pipeline = MetadataPipeline(service)

        identification = pipeline.identify(
            "Batman #1 (2021).cbz"
        )

        overrides = MetadataOverrides(
            volume=3
        )

        comic = pipeline.build_comic(
            identification,
            volume_id=123,
            overrides=overrides
        )

        self.assertEqual(
            comic.volume,
            3
        )
        
    def test_build_xml(self):
        service = FakeComicVineService()
        pipeline = MetadataPipeline(service)

        identification = pipeline.identify(
            "Batman #1 (2021).cbz"
        )

        xml = pipeline.build_xml(
            identification,
            volume_id=123
        )

        self.assertIn(
            "<Series>Batman</Series>",
            xml
        )

        self.assertIn(
            "<Number>1</Number>",
            xml
        )

        self.assertIn(
            "<Year>2021</Year>",
            xml
        )

        self.assertIn(
            "<Publisher>DC Comics</Publisher>",
            xml
        )
        
    def test_identify_invalid_filename(self):
        service = FakeComicVineService()
        pipeline = MetadataPipeline(service)

        with self.assertRaises(ValueError):
            pipeline.identify(
                "Batman.cbz"
            )