from datetime import date
from models.comic import Comic

def parse_store_date(store_date: str | None) -> tuple[int | None, int | None, int | None]:
    """
    Converts a ComicVine YYYY-MM-DD date into day, month, year values/
    
    Returns None values when no valid date supplied.
    """
    
    if not store_date:
        return None, None, None
    
    try:
        parsed_date = date.fromisoformat(store_date)
    except ValueError:
        return None, None, None
    
    return (
        parsed_date.day,
        parsed_date.month,
        parsed_date.year
    )
    
def map_person_credits(
    credits: list[dict]
) -> dict[str, list[str]]:
    """
    Maps ComicVine person credits into the corresponding Comic fields.
    
    A person may have multiple roles, so the same person can appear in multiple output lists.
    """
    
    mapped = {
        "writers": [],
        "pencillers": [],
        "inkers": [],
        "colorists": [],
        "letterers": [],
        "cover_artists": [],
        "editors": [],
        "translators": [],
    }
    
    role_mapping = {
        "writer": "writers",
        "penciler": "pencillers",
        "inker": "inkers",
        "colorist": "colorists",
        "letterer": "letterers",
        "editor": "editors",
        "translator": "translators",
        "cover": "cover_artists",
    }
    
    for credit in credits:
        name = credit.get("name")
        role_string = credit.get("role", "")
        
        if not name:
            continue
        
        roles = [
            role.strip().lower()
            for role in role_string.split(",")
        ]
        
        for role in roles:
            field_name = role_mapping.get(role)
            
            if field_name is not None:
                mapped[field_name].append(name)
                
    return mapped

def extract_names(credits: list[dict]) -> list[str]:
    """
    Extracts character/team/location names from ComicVine credits records.
    """
    
    return [
        credit["name"]
        for credit in credits
        if credit.get("name")
    ]
    
def extract_first_name(credits: list[dict]) -> str | None:
    """
    Returns the first named credit, or None if no credit exists.
    """

    for credit in credits:
        name = credit.get("name")

        if name:
            return name

    return None

def extract_publisher_name(volume: dict) -> str | None:
    """
    Extracts the publisher name from a ComicVine volume.
    """
    
    publisher = volume.get("publisher")
    
    if not publisher:
        return None
    
    return publisher.get("name")
    
    
    
def issue_to_comic(issue: dict, volume:dict) -> Comic:
    """
    Convers a ComicVine issue response into a Comic object.
    """
    
    volume = issue.get("volume", {})
    
    series = volume.get("name")
    
    if not series:
        raise ValueError("ComicVine issue does not contain a volume name.")
    
    issue_number = issue.get("issue_number", "")
    
    if issue_number is None:
        raise ValueError("ComicVine issue does not contain an issue number.")
    
    day, month, year = parse_store_date(issue.get("store_date"))
    
    credits = map_person_credits(issue.get("person_credits", []))
    
    return Comic(
        series=series,
        issue=issue_number,
        title=issue.get("name"),

        synopsis=issue.get("description"),

        characters=extract_names(
            issue.get("character_credits", [])
        ),

        teams=extract_names(
            issue.get("team_credits", [])
        ),

        locations=extract_names(
            issue.get("location_credits", [])
        ),

        story_arc=extract_first_name(
            issue.get("story_arc_credits", [])
        ),

        writers=credits["writers"],
        pencillers=credits["pencillers"],
        inkers=credits["inkers"],
        colorists=credits["colorists"],
        letterers=credits["letterers"],
        cover_artists=credits["cover_artists"],
        editors=credits["editors"],
        translators=credits["translators"],

        day=day,
        month=month,
        year=year,

        publisher=extract_publisher_name(volume),

        web=issue.get("site_detail_url"),
    )
    
    