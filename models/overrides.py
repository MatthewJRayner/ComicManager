from dataclasses import dataclass, replace
from models.comic import Comic    

@dataclass
class MetadataOverrides:
    # GENERAL 
    series: str | None = None
    issue: str | None = None
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
    characters: list[str] | None = None
    teams: list[str] | None = None
    locations: list[str] | None = None
    main_character_or_team: str | None = None
    
    # AUTHORS
    writers: list[str] | None = None
    pencillers: list[str] | None = None
    inkers: list[str] | None = None
    colorists: list[str] | None = None
    letterers: list[str] | None = None
    cover_artists: list[str] | None = None
    editors: list[str] | None = None
    translators: list[str] | None = None
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
    tags: list[str] | None = None
    
    # METHODS
    def apply_to(self, comic: Comic) -> Comic:
        """
        Apply the overrides to a given Comic instance and return a new Comic instance with the overrides applied.
        """
        
        new_comic = replace(comic)
        
        if self.series is not None:
            new_comic.series = self.series
        if self.issue is not None:
                new_comic.series = self.series
        if self.title is not None:
                new_comic.title = self.title
        if self.volume is not None:
                new_comic.volume = self.volume
        if self.story_arc is not None:
                new_comic.story_arc = self.story_arc
        if self.story_arc_number is not None:
                new_comic.story_arc_number = self.story_arc_number
        if self.alternate_series is not None:
                new_comic.alternate_series = self.alternate_series
        if self.series_group is not None:
                new_comic.series_group = self.series_group
        if self.genre is not None:
                new_comic.genre = self.genre
        if self.synopsis is not None:
                new_comic.synopsis = self.synopsis
        if self.characters is not None:
                new_comic.characters = self.characters.copy()
        if self.teams is not None:
                new_comic.teams = self.teams.copy()
        if self.main_character_or_team is not None:
                new_comic.main_character_or_team = self.main_character_or_team
        if self.writers is not None:
                new_comic.writers = self.writers.copy()
        if self.pencillers is not None:
                new_comic.pencillers = self.pencillers.copy()
        if self.inkers is not None:
                new_comic.inkers = self.inkers.copy()
        if self.colorists is not None:
                new_comic.colorists = self.colorists.copy()
        if self.letterers is not None:
                new_comic.letterers = self.letterers.copy()
        if self.cover_artists is not None:
                new_comic.cover_artists = self.cover_artists.copy()
        if self.editors is not None:
                new_comic.editors = self.editors.copy()
        if self.imprint is not None:
                new_comic.imprint = self.imprint
        if self.day is not None:
                new_comic.day = self.day
        if self.month is not None:
                new_comic.month = self.month
        if self.year is not None:
                new_comic.year = self.year
        if self.publisher is not None:
                new_comic.publisher = self.publisher
        if self.format is not None:
                new_comic.format = self.format
        if self.type is not None:
                new_comic.type = self.type
        if self.language_iso is not None:
                new_comic.language_iso = self.language_iso
        if self.review is not None:
                new_comic.review = self.review
        if self.notes is not None:
                new_comic.notes = self.notes
        if self.tags is not None:
                new_comic.tags = self.tags.copy()
                
        return new_comic