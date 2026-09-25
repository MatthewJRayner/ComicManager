import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from cbz.processor import process_cbz
from cbz.archive import read_comic_info, read_file
from metadata.validator import ComicInfoValidationError
from unittest.mock import patch

class TestProcessor(unittest.TestCase):
    
    def test_metadata_replace(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.cbz"
            
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("001.jpg", b"page one")
                archive.writestr(
                    "ComicInfo.xml",
                    b"<ComicInfo><Series>Old Batman</Series></ComicInfo>"
                )
                
            new_comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo><Series>New Batman</Series></ComicInfo>"""
            
            process_cbz(source, new_comic_info)
            
            self.assertEqual(
                read_comic_info(source),
                new_comic_info
            )
                
    def test_pages_survive(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.cbz"
            
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("001.jpg", b"page one")
                archive.writestr(
                    "ComicInfo.xml",
                    b"<ComicInfo><Series>Old Batman</Series></ComicInfo>"
                )
                
            new_comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo><Series>New Batman</Series></ComicInfo>"""
            
            process_cbz(source, new_comic_info)
            
            self.assertEqual(
                read_file(source, "001.jpg"),
                b"page one"
            )
                
    def test_temp_files_disappear(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.cbz"
            
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("001.jpg", b"page one")
                archive.writestr(
                    "ComicInfo.xml",
                    b"<ComicInfo><Series>Old Batman</Series></ComicInfo>"
                )
                
            new_comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo><Series>New Batman</Series></ComicInfo>"""
            
            process_cbz(source, new_comic_info)
            
            remaining = list(temp_path.glob("*.cbz"))
            
            self.assertEqual(
                remaining,
                [source]
            )  
            
    def test_invalid_xml(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.cbz"
            old_comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo><Series>Old Batman</Series></ComicInfo>"""
            
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("001.jpg", b"page one")
                archive.writestr(
                    "ComicInfo.xml",
                    old_comic_info
                )
                
            new_comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo><Series>New Batman</ComicInfo>"""
            
            with self.assertRaises(ComicInfoValidationError):
                process_cbz(source, new_comic_info)
                
            self.assertEqual(
                read_comic_info(source),
                old_comic_info
            )
            
    def test_failure_after_creation(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.cbz"
            old_comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo><Series>Old Batman</Series></ComicInfo>"""
            
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("001.jpg", b"page one")
                archive.writestr(
                    "ComicInfo.xml",
                    old_comic_info
                )
                
            new_comic_info = """<?xml version="1.0" encoding="utf-8"?>
            <ComicInfo><Series>New Batman</Series></ComicInfo>"""
            
            with patch(
                "cbz.processor.create_with_comic_info",
                side_effect=RuntimeError("Test Failure")
            ):
                with self.assertRaises(RuntimeError):
                    process_cbz(source, new_comic_info)
                    
            self.assertEqual(
                read_comic_info(source),
                old_comic_info
            )
            
    
if __name__ == "__main__":
    unittest.main()