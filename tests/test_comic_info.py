import unittest
import xml.etree.ElementTree as ET

from models.comic import Comic
from metadata.comic_info import comic_to_xml

class TestComicInfo(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()