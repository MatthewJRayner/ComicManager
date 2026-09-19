from pathlib import Path

from cbz.processor import process_cbz
from comicvine.service import ComicVineService
from models.overrides import MetadataOverrides
from pipeline.metadata import MetadataIdentification, MetadataPipeline

class CBZMetadataPipeline:
    """
    Coordinates ComicVine metadata generation with safe CBZ modification.
    """
    def __init__(self, comicvine: ComicVineService):
        self.metadata = MetadataPipeline(comicvine)
        
    def identify(
        self,
        source: Path
    ) -> MetadataIdentification:
        """
        Identifies possible ComicVine volumes fro the CBZ filename without modifying the archive.
        """
        
        return self.metadata.identify(
            source.name
        )
        
    def process(
        self,
        source: Path,
        identification: MetadataIdentification,
        volume_id: int,
        overrides: MetadataOverrides | None = None
    ) -> None:
        """
        Generates validated ComicInfo.xml for the selected ComicVine volume and writes it into the destination CBZ.
        """
        
        comic_info = self.metadata.build_xml(
            identification,
            volume_id,
            overrides
        )
        
        process_cbz(
            source,
            comic_info
        )
        
        
    