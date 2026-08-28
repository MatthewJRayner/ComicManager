from dataclasses import dataclass, field

@dataclass
class Comic:
    # GENERAL 
    series: str
    issue: str
    count: int | None = None
    title: str | None = None
    volume: str | None = None
    story_arc: str | None = None
    story_arc_number: str | None = None
    alternate_series: str | None = None
    alternate_number: str | None = None
    alternate_count: str | None = None
    series_group: str | None = None
    genre: str | None = None
    
    # PLOT
    synopsis: str | None = None
    characters: list[str] = field(default_factory=list)
    teams: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    main_character_or_team: str | None = None
    
    # AUTHORS
    writers: list[str] = field(default_factory=list)
    pencillers: list[str] = field(default_factory=list)
    inkers: list[str] = field(default_factory=list)
    colorists: list[str] = field(default_factory=list)
    letterers: list[str] = field(default_factory=list)
    cover_artists: list[str] = field(default_factory=list)
    editors: list[str] = field(default_factory=list)
    translators: list[str] = field(default_factory=list)
    imprint: str | None = None
    
    # PUBLISHING
    day: int | None = None
    month: int | None = None
    year: int | None = None
    publisher: str | None = None
    format: str | None = None
    type: str | None = None
    language_iso: str | None = None
    web: str | None = None
    page_count: int | None = None
    black_and_white: bool | None = None
    manga: str | None = None
    scan_information: str | None = None
    age_rating: str | None = None
    community_rating: float | None = None
    gtin: str | None = None
    
    # NOTES
    review: str | None = None
    notes: str | None = None
    tags: list[str] = field(default_factory=list)