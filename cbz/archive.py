from pathlib import Path
import zipfile

def list_contents(path: Path) -> list[str]:
    """
    Returns the names of all filed contained in a CBZ archive
    """
    
    with zipfile.ZipFile(path, 'r') as archive:
        return archive.namelist()
    
def has_comic_info(path: Path) -> bool:
    """
    Returns True if the CBZ archive contains a ComicInfo.xml file, False otherwise
    """
    
    with zipfile.ZipFile(path, "r") as archive:
        return "ComicInfo.xml" in archive.namelist()
    
def read_file(path: Path, filename: str) -> bytes:
    """
    Reads a file from the CBZ archive and returns its contents as bytes
    """
    
    with zipfile.ZipFile(path, "r") as archive:
        return archive.read(filename)
    
    
def read_comic_info(path: Path) -> str | None:
    """
    Returns the existing ComicInfo.xml contents as a string,
    or None if the CBZ does not contain ComicInfo.xml.
    """
    
    if not has_comic_info(path):
        return None

    data = read_file(path, "ComicInfo.xml")
    
    return data.decode("utf-8")
    
def copy_archive(source: Path, destination: Path) -> None:
    """
    Creates a new CBZ containing the same files as the source CBZ
    """
    
    with zipfile.ZipFile(source, "r") as source_archive:
        with zipfile.ZipFile(
            destination,
            "w",
            compression=zipfile.ZIP_DEFLATED            
        ) as destination_archive:
            
            for filename in source_archive.namelist():
                data = source_archive.read(filename)
                destination_archive.writestr(filename, data)
    