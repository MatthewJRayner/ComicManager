from pathlib import Path
from lxml import etree

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "ComicInfo.xsd"

class ComicInfoValidationError(Exception):
    """
    Custom exception raised when the ComicInfo XML validation fails.
    """

def validate_comic_info(xml: str) -> None:
    """
    Validate the given XML string against the ComicInfo.xsd schema.
    
    Raises:
        ComicInfoValidationError: If the XML is invalid or does not conform to the ComicInfo schema.
    """
    
    try:
        xml_doc = etree.fromstring(xml.encode('utf-8'))
    except etree.XMLSyntaxError as e:
        raise ComicInfoValidationError(
            f"Invalid XML syntax: {e}"
        ) from e
        
    try:
        schema_doc = etree.parse(str(SCHEMA_PATH))
        schema = etree.XMLSchema(schema_doc)
    except (OSError, etree.XMLSchemaParseError) as e:
        raise ComicInfoValidationError(
            f"Could not load ComicInfo schema: {e}"
        ) from e
    
    if not schema.validate(xml_doc):
        error_log = schema.error_log
        
        messages = "\n".join(
            f"- {error.message}"
            for error in error_log
        )
        
        raise ComicInfoValidationError(
            f"ComicInfo XML failed schema validation:\n{messages}"
        )