import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from models.comic import Comic
from models.overrides import MetadataOverrides
from metadata.comic_info import comic_to_xml
from metadata.validator import validate_comic_info
from cbz.archive import list_contents, has_comic_info, read_comic_info, read_file, copy_archive, create_with_comic_info

class TestArchive(unittest.TestCase):
    
    def test_list_contents(self):
        with TemporaryDirectory() as temp_dir:
            cbz_path = Path(temp_dir) / "test.cbz"
            
            with zipfile.ZipFile(cbz_path, 'w') as archive:
                archive.writestr("001.jpg", b"fake image data")
                archive.writestr("002.jpg", b"fake image data")
                archive.writestr("ComicInfo.xml", "<ComicInfo />")
                
            contents = list_contents(cbz_path)
            
            self.assertEqual(
                contents,
                ["001.jpg", "002.jpg", "ComicInfo.xml"]
            )
            
    def test_empty_archive(self):
        with TemporaryDirectory() as temp_dir:
            cbz_path = Path(temp_dir) / "empty.cbz"
            
            with zipfile.ZipFile(cbz_path, 'w') as archive:
                pass  # Create an empty archive
                
            contents = list_contents(cbz_path)
            
            self.assertEqual(contents, [])
        
    def test_missing_archive(self):
        with TemporaryDirectory() as temp_dir:
            cbz_path = Path(temp_dir) / "nonexistent.cbz"
            
            with self.assertRaises(FileNotFoundError):
                list_contents(Path("does_not_exist.cbz"))
                
    def test_detect_existing_comicinfo(self):
        with TemporaryDirectory() as temp_dir:
            cbz_path = Path(temp_dir) / "test.cbz"
            
            with zipfile.ZipFile(cbz_path, 'w') as archive:
                archive.writestr("001.jpg", b"fake image data")
                archive.writestr("002.jpg", b"fake image data")
                archive.writestr("ComicInfo.xml", "<ComicInfo />")
                
            self.assertTrue(has_comic_info(cbz_path))
    
    def test_detect_missing_comicinfo(self):
        with TemporaryDirectory() as temp_dir:
            cbz_path = Path(temp_dir) / "test.cbz"
            
            with zipfile.ZipFile(cbz_path, 'w') as archive:
                archive.writestr("001.jpg", b"fake image data")
                archive.writestr("002.jpg", b"fake image data")
                
            self.assertFalse(has_comic_info(cbz_path))
        
    def test_read_comicinfo(self):
        with TemporaryDirectory() as temp_dir:
            comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo>
                <Series>Batman</Series>
                <Number>1</Number>
            </ComicInfo>
            """
            
            cbz_path = Path(temp_dir) / "test.cbz"
            with zipfile.ZipFile(cbz_path, "w") as archive:
                archive.writestr("ComicInfo.xml", comic_info.encode("utf-8"))
                
            result = read_comic_info(cbz_path)
            
            self.assertEqual(result, comic_info)  
    
    def test_read_missing_comic_info(self):
        with TemporaryDirectory() as temp_dir:
            cbz_path = Path(temp_dir) / "test.cbz"
            
            with zipfile.ZipFile(cbz_path, 'w') as archive:
                archive.writestr("001.jpg", b"fake image data")
                archive.writestr("002.jpg", b"fake image data")
                
            self.assertIsNone(read_comic_info(cbz_path))
            
    def test_copy_archive(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.cbz"
            destination = temp_path / "destination.cbz"
            
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("001.jpg", b"page one")
                archive.writestr("002.jpg", b"page two")
                archive.writestr(
                    "ComicInfo.xml",
                    b"<ComicInfo><Series>Batman</Series></ComicInfo>"
                )
                
            copy_archive(source, destination)
            
            self.assertTrue(destination.exists())
            
            self.assertEqual(
                list_contents(source),
                list_contents(destination)
            )
    
    def test_add_comicinfo_to_cbz_with_no_metadata(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.cbz"
            destination = temp_path / "destination.cbz"
            
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("001.jpg", b"page one")
                archive.writestr("002.jpg", b"page two")
                
            comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo>
                <Series>Batman</Series>
                <Number>1</Number>
            </ComicInfo>
            """
            
            create_with_comic_info(
                source,
                destination,
                comic_info
            )
            
            self.assertTrue(has_comic_info(destination))
            self.assertEqual(read_comic_info(destination), comic_info)
            
    def test_replace_existing_comicinfo(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.cbz"
            destination = temp_path / "destination.cbz"
            
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("001.jpg", b"page one")
                archive.writestr("002.jpg", b"page two")
                archive.writestr(
                    "ComicInfo.xml",
                    b"<ComicInfo><Series>Old Batman</Series></ComicInfo>"
                )
                
            new_comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo><Series>New Batman</Series></ComicInfo>"""
            
            create_with_comic_info(
                source,
                destination,
                new_comic_info
            )
            
            self.assertEqual(read_comic_info(destination), new_comic_info)
            
            contents = list_contents(destination)
            
            self.assertEqual(
                contents.count("ComicInfo.xml"),
                1
            )
            
    def test_original_not_changed(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.cbz"
            destination = temp_path / "destination.cbz"
            
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("001.jpg", b"page one")
                archive.writestr("002.jpg", b"page two")
                archive.writestr(
                    "ComicInfo.xml",
                    b"<ComicInfo><Series>Old Batman</Series></ComicInfo>"
                )
                
            new_comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo><Series>New Batman</Series></ComicInfo>"""
            
            original_info = read_comic_info(source)
            
            create_with_comic_info(
                source,
                destination,
                new_comic_info
            )
            
            self.assertEqual(
                read_comic_info(source),
                original_info
            )
            
            self.assertEqual(
                read_file(source, "001.jpg"),
                read_file(destination, "001.jpg")
            )

            self.assertEqual(
                read_file(source, "002.jpg"),
                read_file(destination, "002.jpg")
            )
            
    def test_comic_info_integration(self):
        old_comic = Comic(
            series="Batman",
            issue="1",
            volume=5,
            year=2024,
            publisher="DC Comics"
        )
        old_comic_info = comic_to_xml(old_comic)
        
        new_comic = Comic(
            series="Superman",
            issue="453",
            volume=2,
            year=1957,
            publisher="DC Comics"
        )
        overrides = MetadataOverrides(
            volume=3
        )
        updated_comic = overrides.apply_to(new_comic)
        updated_comic_info = comic_to_xml(updated_comic)
        
        validate_comic_info(old_comic_info)
        validate_comic_info(updated_comic_info)
        
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.cbz"
            destination = temp_path / "destination.cbz"
            
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("001.jpg", b"page one")
                archive.writestr("002.jpg", b"page two")
                archive.writestr("ComicInfo.xml", old_comic_info)
                
            create_with_comic_info(
                source,
                destination,
                updated_comic_info
            )
            
            self.assertEqual(read_comic_info(destination), updated_comic_info)
            
if __name__ == "__main__":
    unittest.main()