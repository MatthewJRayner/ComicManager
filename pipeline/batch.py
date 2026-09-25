from dataclasses import dataclass
from pathlib import Path
from enum import Enum

from comicvine.matcher import VolumeCandidate
from comicvine.filename import parse_filename, ParsedFilename
from comicvine.service import ComicVineService
from models.comic import Comic
from models.overrides import MetadataOverrides
from metadata.comic_info import comic_to_xml
from metadata.validator import validate_comic_info
from cbz.processor import process_cbz, process_cbz_to

@dataclass
class ResolvedItem:
    source: Path
    parsed: ParsedFilename
    comic: Comic
    
@dataclass
class BatchItemStatus(Enum):
    SUCCESS = "success"
    UNRESOLVED = "unresolved"
    FAILED = "failed"
    
@dataclass
class BatchIdentification:
    series: str
    items: list[tuple[Path, ParsedFilename]]
    candidates: list[VolumeCandidate]
    selected_volume_id: int | None = None
    
@dataclass
class BatchItemResult:
    source: Path
    parsed: ParsedFilename
    comic: Comic | None = None
    error: str | None = None
    
@dataclass
class BatchProcessResult:
    source: Path
    parsed: ParsedFilename
    status: BatchItemStatus
    error: str | None = None
    
    @property
    def success(self) -> bool:
        return self.status == BatchItemStatus.SUCCESS

@dataclass
class BatchResult:
    series: str
    selected_volume_id: int
    results: list[BatchProcessResult]
    
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
    def __init__(self, comicvine: ComicVineService, cbz_processor=process_cbz, cbz_processor_to=process_cbz_to):
        self.comicvine = comicvine
        self.cbz_processor = cbz_processor
        self.cbz_processor_to = cbz_processor_to
        
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
        
    def resolve_issues(self, identification: BatchIdentification) -> list[BatchItemResult]:
        if identification.selected_volume_id is None:
            raise ValueError("A ComicVine volume must be selected before resolving issues.")
        
        results = []
        
        for source, parsed in identification.items:
            try:
                comic = self.comicvine.get_comic_from_volume(identification.selected_volume_id, parsed.issue)
                
                results.append(
                    BatchItemResult(source=source, parsed=parsed, comic=comic)
                )
            except Exception as error:
                results.append(
                    BatchItemResult(source=source, parsed=parsed, error=str(error))
                )
        
        return results
    
    def apply_overrides(self, results: list[BatchItemResult], overrides: MetadataOverrides | None = None) -> list[BatchItemResult]:
        """
        Applies the same metadta overrides to every successfully resolved Comic in the batch.
        """
        
        if overrides is None:
            return results
        
        for result in results:
            if result.comic is not None:
                result.comic = overrides.apply_to(result.comic)
                
        return results 
    
    def process(self, results: list[BatchItemResult], overrides: MetadataOverrides | None = None, output_directory: Path | None = None) -> list[BatchProcessResult]:
        if overrides is not None:
            results = self.apply_overrides(results, overrides)
            
        process_results = []
        
        for result in results:
            if result.comic is None:
                process_results.append(
                    BatchProcessResult(source=result.source, parsed=result.parsed, status=BatchItemStatus.UNRESOLVED, error=result.error)
                )

            try:
                comic_info = comic_to_xml(result.comic)
                
                validate_comic_info(comic_info)
                
                if output_directory is None:
                    self.cbz_processor(result.source, comic_info)
                    
                else:
                    destination = (
                        output_directory /
                        result.source.name
                    )
                    
                    self.cbz_processor_to(
                        results.source,
                        destination,
                        comic_info
                    )
                
                process_results.append(
                    BatchProcessResult(source=result.source, parsed=result.parsed, status=BatchItemStatus.SUCCESS)
                )
                
            except Exception as error:
                process_results.append(
                    BatchProcessResult(
                        source=result.source, status=BatchItemStatus.FAILED, parsed=result.parsed, error=str(error)
                    )
                )
                
        return process_results
    
    def build_result(self, identification: BatchIdentification, process_results: list[BatchProcessResult]) -> BatchResult:
        if identification.selected_volume_id is None:
            raise ValueError("A ComicVine volume must be selected before building a batch result.")
        
        return BatchResult(
            series=identification.series,
            selected_volume_id=identification.selected_volume_id,
            results=process_results
        )
            
        
        
    
    
    