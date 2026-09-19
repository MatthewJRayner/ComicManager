from dataclasses import dataclass

from comicvine.filename import ParsedFilename, parse_filename
from comicvine.matcher import VolumeCandidate
from comicvine.service import ComicVineService

from models.comic import Comic
from models.overrides import MetadataOverrides

from metadata.comic_info import comic_to_xml
from metadata.validator import validate_comic_info

@dataclass
class MetadataIdentification:
    """
    Contains the informations extracted from a filename and the ComicVine volumes that could match it.
    """
    parsed: ParsedFilename
    candidates: list[VolumeCandidate]
    
class MetadataPipeline:
    def __init__(self, comicvine: ComicVineService):
        self.comicvine = comicvine
        
    def identify(self, filename: str) -> MetadataIdentification:
        """
        Parses a ComicManager filename and retrieves plausible ComicVine volume candidates.
        """
        
        parsed = parse_filename(filename)
        
        candidates = self.comicvine.get_volume_candidates(
            parsed.series,
            parsed.year
        )
        
        return MetadataIdentification(
            parsed=parsed,
            candidates=candidates
        )
        
    def build_comic(
        self,
        identification: MetadataIdentification,
        volume_id: int,
        overrides: MetadataOverrides | None = None
    ) -> Comic:
        """
        Retrieves the selected ComicVine issue and converts it into a Comic object, and applies optional overrides.
        """
        
        comic = self.comicvine.get_comic_from_volume(
            volume_id,
            identification.parsed.issue
        )
        
        if overrides is not None:
            comic = overrides.apply_to(comic)
        
        return comic
    
    def build_xml(
        self,
        identification: MetadataIdentification,
        volume_id: int,
        overrides: MetadataOverrides | None = None
    ) -> str:
        """
        Builds ComicInfo.xml for a selected ComicVine volume,
        applies overrides, and validates the resulting XML.
        """
        
        comic = self.build_comic(
            identification,
            volume_id,
            overrides
        )
        
        xml = comic_to_xml(comic)
        
        validate_comic_info(xml)
        
        return xml
        
        
    