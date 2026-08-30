from pathlib import Path
from tempfile import NamedTemporaryFile

from cbz.archive import create_with_comic_info, replace_archive, read_comic_info
from metadata.validator import validate_comic_info

def process_cbz(
    source: Path,
    comic_info: str
) -> None:
    """
    Replaces the ComicInfo.xml in a CBZ automatically
    """
    
    validate_comic_info(comic_info)
    
    with NamedTemporaryFile(
        suffix=".cbz",
        dir=source.parent,
        delete=False
    ) as temp_file:
        temp_path = Path(temp_file.name)
        
    try:
        create_with_comic_info(
            source,
            temp_path,
            comic_info
        )
        
        updated_info = read_comic_info(temp_path)
        validate_comic_info(updated_info)
        
        replace_archive(
            source,
            temp_path
        )
    
    finally:
        if temp_path.exists():
            temp_path.unlink()
    