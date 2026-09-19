import re
from dataclasses import dataclass

@dataclass
class ParsedFilename:
    """
    Represents the metadata extracetd from a ComicManager CBZ filename.
    """
    series: str
    issue: str
    year: int

FILENAME_PATTERN = re.compile(
    r"^(.*?)\s+#(\d{1,3})\s+\((\d{4})\)\.cbz$",
    re.IGNORECASE
)

def parse_filename(filename: str) -> ParsedFilename:
    """
    Extracts series, issue number, and publication year from a ComicManager CBZ filename.
    """
    
    match = FILENAME_PATTERN.match(filename)
    
    if match is None:
        raise ValueError(
            f"Filename does not match the expected format of 'NAME #ISSUE_NUM (YEAR)': {filename}"
        )
        
    series = match.group(1).strip()
    issue = match.group(2)
    year = int(match.group(3))
    
    return ParsedFilename(
        series=series,
        issue=issue,
        year=year
    )
    
    