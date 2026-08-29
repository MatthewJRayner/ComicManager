import xml.etree.ElementTree as ET 
from models.comic import Comic

def add_element(parent, name: str, value: str | None) -> None:
    """
    Adds a sub-element to the parent element if the value is not None
    """
    
    if value is not None:
        ET.SubElement(parent, name).text = str(value)
        
def add_list_element(parent, name: str, values: list[str]) -> None:
    """
    Adds sub-elements to the parent element for each value in the list if the list is not empty
    """
    if values:
        ET.SubElement(parent, name).text = ', '.join(values)
        
def add_bool_element(parent, name: str, value: bool | None) -> None:
    """
    Adds a ComicInfo boolean sub-element to the parent elements if the value is not None using Yes/No representation
    """
    
    if value is not None:
        text = "Yes" if value else "No"
        ET.SubElement(parent, name).text = text
    

def comic_to_xml(comic: Comic) -> str:
    """
    Converts a Comic object to a ComicInfo.xml string representation.
    """
    
    root = ET.Element("ComicInfo")
    
    # XSD ORDER
    add_element(root, "Title", comic.title)
    add_element(root, "Series", comic.series)
    add_element(root, "Number", comic.issue)
    add_element(root, "Count", comic.count)
    add_element(root, "Volume", comic.volume)
    add_element(root, "AlternateSeries", comic.alternate_series)
    add_element(root, "AlternateNumber", comic.alternate_number)
    add_element(root, "AlternateCount", comic.alternate_count)
    add_element(root, "Summary", comic.synopsis)
    add_element(root, "Notes", comic.notes)
    add_element(root, "Year", comic.year)
    add_element(root, "Month", comic.month)
    add_element(root, "Day", comic.day)
    add_list_element(root, "Writer", comic.writers)
    add_list_element(root, "Penciller", comic.pencillers)
    add_list_element(root, "Inker", comic.inkers)
    add_list_element(root, "Colorist", comic.colorists)
    add_list_element(root, "Letterer", comic.letterers)
    add_list_element(root, "CoverArtist", comic.cover_artists)
    add_list_element(root, "Editor", comic.editors)
    add_list_element(root, "Translator", comic.translators)
    add_element(root, "Publisher", comic.publisher)
    add_element(root, "Imprint", comic.imprint)
    add_element(root, "Genre", comic.genre)
    add_list_element(root, "Tags", comic.tags)
    add_element(root, "Web", comic.web)
    add_element(root, "PageCount", comic.page_count)
    add_element(root, "LanguageISO", comic.language_iso)
    add_element(root, "Format", comic.format)
    add_bool_element(root, "BlackAndWhite", comic.black_and_white)
    add_element(root, "Manga", comic.manga)
    add_list_element(root, "Characters", comic.characters)
    add_list_element(root, "Teams", comic.teams)
    add_list_element(root, "Locations", comic.locations)
    add_element(root, "ScanInformation", comic.scan_information)
    add_element(root, "StoryArc", comic.story_arc)
    add_element(root, "StoryArcNumber", comic.story_arc_number)
    add_element(root, "SeriesGroup", comic.series_group)
    add_element(root, "AgeRating", comic.age_rating)
    add_element(root, "CommunityRating", comic.community_rating)
    add_element(root, "MainCharacterOrTeam", comic.main_character_or_team)
    add_element(root, "Review", comic.review)
    add_element(root, "GTIN", comic.gtin)
    
    ET.indent(root, space="  ", level=0)  # Pretty print the XML with indentation
    
    xml = ET.tostring(root, encoding='unicode', method='xml')
    
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml