import unittest
from pathlib import Path

from comicvine.matcher import VolumeCandidate
from pipeline.batch import (
    BatchIdentification,
    BatchPipeline,
)


class FakeComicVineService:
    """
    Fake ComicVine service used to test BatchPipeline
    without making real API requests.
    """

    def __init__(self, candidates):
        self.candidates = candidates
        self.calls = []

    def get_volume_candidates(
        self,
        series: str,
        issue_year: int
    ):
        # Record every call so the tests can verify that
        # the ComicVine search only happens once per batch.
        self.calls.append(
            {
                "series": series,
                "issue_year": issue_year,
            }
        )

        return self.candidates


class TestBatchPipeline(unittest.TestCase):

    def setUp(self):
        """
        Create a fake ComicVine service and pipeline for each test.
        """

        self.candidates = [
            VolumeCandidate(
                volume={
                    "id": 123,
                    "name": "Batman",
                },
                score=0.95,
            ),
            VolumeCandidate(
                volume={
                    "id": 456,
                    "name": "Batman",
                },
                score=0.88,
            ),
        ]

        self.comicvine = FakeComicVineService(
            self.candidates
        )

        self.pipeline = BatchPipeline(
            self.comicvine
        )

    def test_identify_batch(self):
        """
        A batch containing several issues from the same series
        should produce one BatchIdentification.
        """

        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
            Path("Batman #3 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.assertIsInstance(
            identification,
            BatchIdentification
        )

        self.assertEqual(
            identification.series,
            "Batman"
        )

        self.assertEqual(
            len(identification.items),
            3
        )

        self.assertEqual(
            identification.candidates,
            self.candidates
        )

        self.assertIsNone(
            identification.selected_volume_id
        )

    def test_identify_searches_comicvine_once(self):
        """
        The batch should perform one ComicVine volume search,
        rather than searching once for every CBZ.
        """

        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
            Path("Batman #3 (2017).cbz"),
        ]

        self.pipeline.identify(sources)

        self.assertEqual(
            len(self.comicvine.calls),
            1
        )

        self.assertEqual(
            self.comicvine.calls[0],
            {
                "series": "Batman",
                "issue_year": 2017,
            }
        )

    def test_identify_preserves_parsed_files(self):
        """
        Each file should retain its ParsedFilename information
        so that issue numbers and years are available later.
        """

        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #002 (2017).cbz"),
            Path("Batman #3 (2018).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.assertEqual(
            identification.items[0][1].issue,
            "1"
        )

        self.assertEqual(
            identification.items[1][1].issue,
            "002"
        )

        self.assertEqual(
            identification.items[2][1].issue,
            "3"
        )

        self.assertEqual(
            identification.items[2][1].year,
            2018
        )

    def test_identify_rejects_multiple_series(self):
        """
        A batch containing different series should be rejected.

        The user can remove the unwanted files and then run
        identification again.
        """

        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
            Path("Superman #1 (2017).cbz"),
        ]

        with self.assertRaises(ValueError):
            self.pipeline.identify(sources)

        # ComicVine should not be contacted when the batch
        # has already failed the series-name validation.
        self.assertEqual(
            len(self.comicvine.calls),
            0
        )

    def test_select_valid_volume(self):
        """
        A volume that appears in the candidate list should
        be accepted.
        """

        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.pipeline.select_volume(
            identification,
            123
        )

        self.assertEqual(
            identification.selected_volume_id,
            123
        )

    def test_select_invalid_volume(self):
        """
        A volume that wasn't returned as a candidate should
        not be selectable.
        """

        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        with self.assertRaises(ValueError):
            self.pipeline.select_volume(
                identification,
                999
            )

        # The invalid selection must not alter the state.
        self.assertIsNone(
            identification.selected_volume_id
        )

    def test_empty_batch(self):
        """
        An empty batch should be rejected rather than producing
        an invalid BatchIdentification.
        """

        with self.assertRaises(ValueError):
            self.pipeline.identify([])

        self.assertEqual(
            len(self.comicvine.calls),
            0
        )


if __name__ == "__main__":
    unittest.main()