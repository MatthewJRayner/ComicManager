import unittest
from pathlib import Path

from comicvine.matcher import VolumeCandidate
from pipeline.batch import (
    BatchIdentification,
    BatchPipeline,
)
from models.comic import Comic
from models.overrides import MetadataOverrides
from metadata.comic_info import comic_to_xml


class FakeComicVineService:
    """
    Fake ComicVine service used to test BatchPipeline
    without making real API requests.
    """

    def __init__(self, candidates):
        self.candidates = candidates
        self.calls = []
        self.issue_calls = []
        self.failing_issues = set()

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
    
    def get_comic_from_volume(
        self,
        volume_id: int,
        issue_number: str
    ):
        self.issue_calls.append(
            {
                "volume_id": volume_id,
                "issue_number": issue_number,
            }
        )
        
        if issue_number in self.failing_issues:
            raise ValueError("Issue not found")
        
        return Comic(
            series="Batman",
            issue=issue_number
        )

class FakeCBZProcessor:
    """
    Fake CBZ processor used to test BatchPipeline without
    modifying real CBZ files.
    """

    def __init__(self):
        self.calls = []
        self.failing_sources = set()

    def __call__(
        self,
        source: Path,
        comic_info: str
    ):
        self.calls.append(
            {
                "source": source,
                "comic_info": comic_info,
            }
        )

        if source in self.failing_sources:
            raise ValueError(
                "CBZ processing failed"
            )


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
        
        self.cbz_processor = FakeCBZProcessor()

        self.pipeline = BatchPipeline(
            self.comicvine,
            self.cbz_processor
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
        
    def test_resolve_issues(self):
        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
            Path("Batman #3 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.pipeline.select_volume(
            identification,
            123
        )

        results = self.pipeline.resolve_issues(
            identification
        )

        self.assertEqual(
            len(results),
            3
        )

        self.assertIsNotNone(
            results[0].comic
        )

        self.assertIsNotNone(
            results[1].comic
        )

        self.assertIsNotNone(
            results[2].comic
        )

        self.assertEqual(
            results[0].comic.issue,
            "1"
        )

        self.assertEqual(
            results[1].comic.issue,
            "2"
        )

        self.assertEqual(
            results[2].comic.issue,
            "3"
        )
        
    def test_resolve_issues_uses_selected_volume(self):
        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
            Path("Batman #3 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.pipeline.select_volume(
            identification,
            123
        )

        self.pipeline.resolve_issues(
            identification
        )

        self.assertEqual(
            self.comicvine.issue_calls,
            [
                {
                    "volume_id": 123,
                    "issue_number": "1",
                },
                {
                    "volume_id": 123,
                    "issue_number": "2",
                },
                {
                    "volume_id": 123,
                    "issue_number": "3",
                },
            ]
        )
        
    def test_resolve_issues_continues_after_failure(self):
        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
            Path("Batman #3 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.pipeline.select_volume(
            identification,
            123
        )

        # Make issue #2 fail.
        self.comicvine.failing_issues.add("2")

        results = self.pipeline.resolve_issues(
            identification
        )

        self.assertEqual(
            len(results),
            3
        )

        # Issue #1 succeeded.
        self.assertIsNotNone(
            results[0].comic
        )

        self.assertIsNone(
            results[0].error
        )

        # Issue #2 failed.
        self.assertIsNone(
            results[1].comic
        )

        self.assertEqual(
            results[1].error,
            "Issue not found"
        )

        # Issue #3 still succeeded.
        self.assertIsNotNone(
            results[2].comic
        )

        self.assertIsNone(
            results[2].error
        )
            
    def test_resolve_issues_requires_selected_volume(self):
        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        with self.assertRaises(ValueError):
            self.pipeline.resolve_issues(
                identification
            )

        # No issue lookup should have occurred.
        self.assertEqual(
            len(self.comicvine.issue_calls),
            0
        )
        
    def test_apply_overrides_to_batch(self):
        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
            Path("Batman #3 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.pipeline.select_volume(
            identification,
            123
        )

        results = self.pipeline.resolve_issues(
            identification
        )

        overrides = MetadataOverrides(
            volume=3
        )

        self.pipeline.apply_overrides(
            results,
            overrides
        )

        self.assertEqual(
            results[0].comic.volume,
            3
        )

        self.assertEqual(
            results[1].comic.volume,
            3
        )

        self.assertEqual(
            results[2].comic.volume,
            3
        )
        
    def test_apply_overrides_without_overrides(self):
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

        results = self.pipeline.resolve_issues(
            identification
        )

        self.pipeline.apply_overrides(
            results,
            None
        )

        self.assertIsNone(
            results[0].comic.volume
        )

        self.assertIsNone(
            results[1].comic.volume
        )
        
    def test_apply_overrides_skips_failed_items(self):
        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
            Path("Batman #3 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.pipeline.select_volume(
            identification,
            123
        )

        self.comicvine.failing_issues.add("2")

        results = self.pipeline.resolve_issues(
            identification
        )

        overrides = MetadataOverrides(
            volume=3
        )

        self.pipeline.apply_overrides(
            results,
            overrides
        )

        self.assertEqual(
            results[0].comic.volume,
            3
        )

        self.assertIsNone(
            results[1].comic
        )

        self.assertEqual(
            results[1].error,
            "Issue not found"
        )

        self.assertEqual(
            results[2].comic.volume,
            3
        )
        
    def test_process_successfully_processes_resolved_items(self):
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

        results = self.pipeline.resolve_issues(
            identification
        )

        overrides = MetadataOverrides(
            volume=3
        )

        self.pipeline.apply_overrides(
            results,
            overrides
        )

        process_results = self.pipeline.process(
            results
        )

        self.assertEqual(
            len(process_results),
            2
        )

        self.assertTrue(
            process_results[0].success
        )

        self.assertTrue(
            process_results[1].success
        )

        self.assertIsNone(
            process_results[0].error
        )

        self.assertIsNone(
            process_results[1].error
        )
        
    def test_process_builds_xml_from_overridden_comic(self):
        sources = [
            Path("Batman #1 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.pipeline.select_volume(
            identification,
            123
        )

        results = self.pipeline.resolve_issues(
            identification
        )

        overrides = MetadataOverrides(
            volume=3
        )

        self.pipeline.apply_overrides(
            results,
            overrides
        )

        self.pipeline.process(
            results
        )

        self.assertEqual(
            len(self.cbz_processor.calls),
            1
        )

        comic_info = self.cbz_processor.calls[0][
            "comic_info"
        ]

        self.assertIn(
            "<Series>Batman</Series>",
            comic_info
        )

        self.assertIn(
            "<Number>1</Number>",
            comic_info
        )

        self.assertIn(
            "<Volume>3</Volume>",
            comic_info
        )
        
    def test_process_skips_unresolved_items(self):
        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
            Path("Batman #3 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.pipeline.select_volume(
            identification,
            123
        )

        self.comicvine.failing_issues.add("2")

        results = self.pipeline.resolve_issues(
            identification
        )

        process_results = self.pipeline.process(
            results
        )

        self.assertEqual(
            len(process_results),
            4
        )

        self.assertTrue(
            process_results[0].success
        )

        self.assertFalse(
            process_results[1].success
        )

        self.assertEqual(
            process_results[1].error,
            "Issue not found"
        )

        self.assertFalse(
            process_results[2].success
        )

        # Only #1 and #3 should have reached the CBZ processor.
        self.assertEqual(
            len(self.cbz_processor.calls),
            2
        )
        
    def test_process_continues_after_cbz_failure(self):
        sources = [
            Path("Batman #1 (2017).cbz"),
            Path("Batman #2 (2017).cbz"),
            Path("Batman #3 (2017).cbz"),
        ]

        identification = self.pipeline.identify(
            sources
        )

        self.pipeline.select_volume(
            identification,
            123
        )

        results = self.pipeline.resolve_issues(
            identification
        )

        self.cbz_processor.failing_sources.add(
            sources[1]
        )

        process_results = self.pipeline.process(
            results
        )

        self.assertEqual(
            len(process_results),
            3
        )

        self.assertTrue(
            process_results[0].success
        )

        self.assertFalse(
            process_results[1].success
        )

        self.assertEqual(
            process_results[1].error,
            "CBZ processing failed"
        )

        self.assertTrue(
            process_results[2].success
        )

        # All three were attempted even though #2 failed.
        self.assertEqual(
            len(self.cbz_processor.calls),
            3
        )
    


if __name__ == "__main__":
    unittest.main()