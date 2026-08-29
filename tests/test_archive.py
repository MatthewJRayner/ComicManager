import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from cbz.archive import list_contents, has_comic_info, read_comic_info, copy_archive

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
             