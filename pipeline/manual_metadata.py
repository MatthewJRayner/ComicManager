from models.comic import Comic
from models.overrides import MetadataOverrides
from metadata.comic_info import comic_to_xml
from metadata.validator import validate_comic_info


class ManualMetadataPipeline:
    def build_xml(
        self,
        comic: Comic,
        overrides: MetadataOverrides | None = None
    ) -> str:
        if overrides is not None:
            comic = overrides.apply_to(comic)

        xml = comic_to_xml(comic)
        validate_comic_info(xml)

        return xml