from models.comic import Comic
from models.overrides import MetadataOverrides
from metadata.comic_info import comic_to_xml

def main():
    comic = Comic(
        series="Batman",
        issue="1",
        title="The Court of Owls",
        volume="3",
        story_arc="Court of Owls",
        story_arc_number="1",
        alternate_series="Batman: The New 52",
        series_group="Batman",
        genre="Superhero",
        synopsis="...",
        characters=["Batman", "Joker"],
        teams=["Justice League"],
        locations=["Gotham City"],
        main_character_or_team="Batman",
        writers=["Scott Snyder"],
        pencillers=["Greg Capullo"],
        inkers=["Jonathan Glapion"],
        colorists=["FCO Plascencia"],
        letterers=["Steve Wands"],
        cover_artists=["Greg Capullo"],
        editors=["Mike Marts"],
        imprint="DC Comics",
        day=14,
        month=9,
        year=2021,
        publisher="DC Comics",
        format="Comic",
        language_iso="en",
        review="Excellent",
        notes="Test comic",
        tags=["Superhero", "Batman"]
    )

    overrides = MetadataOverrides(
        volume="5",
    )

    updated = overrides.apply_to(comic)

    xml = comic_to_xml(updated)
    
    print(xml)
    
if __name__ == "__main__":
    main()