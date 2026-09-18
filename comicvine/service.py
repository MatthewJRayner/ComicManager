from comicvine.client import ComicVineClient
from comicvine.matcher import (
    VolumeCandidate,
    find_volume_candidates
)
from comicvine.mapper import issue_to_comic
from models.comic import Comic

class ComicVineService:
    """
    Coordinates ComicVine API access, candidate matching, and metadata mapping.
    """
    
    def __init__(self, client: ComicVineClient):
        self.client = client
        
    def get_volume_candidates(
        self,
        series: str,
        issue_year: int
    ) -> list[VolumeCandidate]:
        """
        Searches ComicVine for volumes that couldcontain the requested issue
        """
        
        volumes = self.client.search_volumes(series)
        
        return find_volume_candidates(
            series,
            issue_year,
            volumes
        )
    
    def get_comic_from_volume(
        self,
        volume_id: int,
        issue_number: str
    ) -> Comic:
        """
        Retrieves an issue from a selected volume and converts it into a Comic object.
        """
        
        issue = self.client.find_issue(
            volume_id,
            issue_number
        )
        
        if issue is None:
            raise ValueError(
                f"Issue #{issue_number} was not found"
                f"in ComicVine volume {volume_id}."
            )
            
        volume = self.client.get_volume(volume_id)
        
        full_issue = self.client.get_issues(
            issue["id"]
        )
        
        return issue_to_comic(
            full_issue,
            volume
        )
        
        
    