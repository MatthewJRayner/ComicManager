import unittest
import zipfile

from pathlib import Path
from tempfile import TemporaryDirectory

from comicvine.matcher import VolumeCandidate
from models.comic import Comic
from pipeline.cbz_metadata import CBZMetadataPipeline

class FakeComicVineService:

    def get_volume_candidates(
        self,
        series: str,
        issue_year: int
    ):
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
        return Comic(
            series="Batman",
            issue=issue_number,
            year=2021,
            publisher="DC Comics"
        )
        
class TestCBZMetadataPipeline(unittest.TestCase):

    def test_process(self):
        with TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            source = temp_path / "Batman #1 (2021).cbz"

            with zipfile.ZipFile(
                source,
                "w"
            ) as archive:
                archive.writestr(
                    "001.jpg",
                    b"page one"
                )

            comicvine = FakeComicVineService()

            pipeline = CBZMetadataPipeline(
                comicvine
            )

            identification = pipeline.identify(
                source
            )

            pipeline.process(
                source=source,
                identification=identification,
                volume_id=123
            )
            
            with zipfile.ZipFile(
                source,
                "r"
            ) as archive:

                self.assertIn(
                    "ComicInfo.xml",
                    archive.namelist()
                )

                comic_info = archive.read(
                    "ComicInfo.xml"
                ).decode("utf-8")
                
                self.assertIn(
                "<Series>Batman</Series>",
                comic_info
                )

                self.assertIn(
                    "<Number>1</Number>",
                    comic_info
                )

                self.assertIn(
                    "<Year>2021</Year>",
                    comic_info
                )

                self.assertIn(
                    "<Publisher>DC Comics</Publisher>",
                    comic_info
                )