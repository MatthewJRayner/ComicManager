from dataclasses import dataclass
from pathlib import Path

from comicvine.matcher import VolumeCandidate
from comicvine.filename import parse_filename, ParsedFilename
from comicvine.service import ComicVineService

@dataclass
class BatchIdentification:
    series: str
    items: list[tuple[Path, ParsedFilename]]
    candidates: list[VolumeCandidate]
    selected_volume_id: int | None = None
    
def get_series_names(sources: list[Path]) -> set[str]:
    """
    Returns the unique series names represented by the CBZ files.
    """
    series_names = set()
    
    for source in sources:
        parsed = parse_filename(source.name)
        series_names.add(parsed.series)
        
    return series_names
    
class BatchPipeline:
    def __init__(self, comicvine: ComicVineService):
        self.comicvine = comicvine
        
    def identify(self, sources: list[Path]) -> BatchIdentification:
        """
        Identifies ComicVine candidates for every CBZ in the batch.
        """
        
        series_names = get_series_names(sources)
        
        if len(series_names) > 1:
            raise ValueError(
                "Multiple series detected in batch: "
                + ", ".join(sorted(series_names))
            )
            
        if not series_names:
            raise ValueError("Batch contains no files.")
        
        series = next(iter(series_names))
        
        items = []
        
        for source in sources:
            parsed = parse_filename(source.name)
            items.append((source, parsed))

        issue_year = items[0][1].year
        
        candidates = self.comicvine.get_volume_candidates(series, issue_year)
            
        return BatchIdentification(
            series=series,
            items=items,
            candidates=candidates
        )
    
    def select_volume(self, identification: BatchIdentification, volume_id: int) -> None:
        """
        Records the ComicVine volume selected for a batch item.
        """
        
        candidate_ids = {
            candidate.volume.get("id")
            for candidate in identification.candidates
        }
        
        if volume_id not in candidate_ids:
            raise ValueError(
                f"Volume {volume_id} is not a candidate "
                f"for {identification.series}"
            )
            
        identification.selected_volume_id = volume_id
        
    
    
    