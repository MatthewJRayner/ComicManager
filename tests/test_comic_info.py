import unittest
import xml.etree.ElementTree as ET

from models.comic import Comic
from metadata.comic_info import comic_to_xml
from metadata.validator import validate_comic_info, ComicInfoValidationError

class TestComicInfo(unittest.TestCase):
    
    def test_valid_minimal_comic_info(self):
        
        comic = Comic(
            series="Batman",
            issue="1"
        )
        
        xml = comic_to_xml(comic)
        
        validate_comic_info(xml)
        
    def test_valid_complete_comic_info(self):
        comic = Comic(
            series="Batman",
            issue="1",
            title="The Court of Owls",
            count=12,
            volume=3,
            alternate_series="Batman: The New 52",
            alternate_number="1",
            alternate_count=12,
            synopsis="Batman investigates a mysterious organisation...",
            notes="Test comic",
            year=2021,
            month=9,
            day=14,
            writers=["Scott Snyder"],
            pencillers=["Greg Capullo"],
            inkers=["Jonathan Glapion"],
            colorists=["FCO Plascencia"],
            letterers=["Jared K. Fletcher"],
            cover_artists=["Greg Capullo"],
            editors=["Mike Marts"],
            translators=["John Doe, Cook Poo"],
            publisher="DC Comics",
            imprint="DC Comics",
            genre="Superhero",
            web="https://example.com",
            page_count=32,
            language_iso="en",
            format="Comic",
            black_and_white=False,
            manga="No",
            characters=["Batman", "Joker"],
            teams=["Justice League"],
            locations=["Gotham City"],
            scan_information="Test scan",
            story_arc="Court of Owls",
            story_arc_number="1",
            age_rating="Teen",
            community_rating=4.5,
            main_character_or_team="Batman",
            review="Excellent",
            tags=["Superhero", "Batman"]
        )
        
        xml = comic_to_xml(comic)
        
        validate_comic_info(xml)

    def test_xml_is_valid(self):
        comic = Comic(
            series="Batman",
            issue="1",
            title="The Court of Owls",
            volume="3",
            year=2021,
            publisher="DC Comics"
        )

        xml = comic_to_xml(comic)

        root = ET.fromstring(xml)

        self.assertEqual(root.tag, "ComicInfo")

    def test_invalid_xml(self):
        xml = """
        <ComicInfo>
            <Title>Batman</Title>
            <Number>1</Number>
        """
        
        with self.assertRaises(ComicInfoValidationError):
            validate_comic_info(xml)

    def test_invalid_community_rating(self):
        comic = Comic(
            series="Batman",
            issue="1",
            community_rating=6.0
        )

        xml = comic_to_xml(comic)

        with self.assertRaises(ComicInfoValidationError):
            validate_comic_info(xml)

    def test_invalid_manga_value(self):
        comic = Comic(
            series="Batman",
            issue="1",
            manga="DefinitelyManga"
        )

        xml = comic_to_xml(comic)

        with self.assertRaises(ComicInfoValidationError):
            validate_comic_info(xml)

    def test_list_fields_are_comma_separated(self):
        comic = Comic(
            series="Batman",
            issue="1",
            characters=["Batman", "Joker"],
            writers=["Scott Snyder", "James Tynion IV"]
        )

        xml = comic_to_xml(comic)

        root = ET.fromstring(xml)

        self.assertEqual(
            root.find("Characters").text,
            "Batman, Joker"
        )

        self.assertEqual(
            root.find("Writer").text,
            "Scott Snyder, James Tynion IV"
        )

if __name__ == "__main__":
    unittest.main()