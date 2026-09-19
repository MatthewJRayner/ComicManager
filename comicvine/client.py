import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.environ["COMICVINE_API_KEY"]
BASE_URL = "https://comicvine.gamespot.com/api"

class ComicVineClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ["COMICVINE_API_KEY"]
        
    def _get(self, endpoint: str, params: dict) -> dict:
        params = {
            **params,
            "api_key": self.api_key,
            "format": "json",
        }
        
        headers = {
            "User-Agent": "ComicManager/1.0"
        }
        
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            params=params,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("error") != "OK":
            raise RuntimeError(
                f"ComicVine API error: {data.get('error')}"
            )
        
        return data
    
    def search_volumes(self, name: str) -> list[dict]:
        """
        Searches ComicVine for volumes matching a name.
        """
        
        data = self._get(
            "search",
            {
                "query": name,
                "resources": "volume",
                "field_list": "id,name,start_year,publisher,count_of_issues",
                "limit": 40
            }
        )
        
        return data.get("results", [])
    
    def find_issue(
        self,
        volume_id: int,
        issue_number: str
    ) -> dict | None:
        """
        Finds an issue withing a specifc ComicVine volume. Returns the first matching issue, or None if no issue exists
        """
        
        data = self._get(
            "issues",
            {
                "filter": f"volume:{volume_id},issue_number:{issue_number}",
                "field_list": "id,name,issue_number,store_date,volume",
            }
        )
        
        results = data.get("results", [])
        
        if not results:
            return None
        
        return results[0]
    
    def get_issue(self, issue_id: int) -> dict:
        """
        Retrieves the complete ComicVine issue record.
        """
        
        data = self._get(
            f"issue/4000-{issue_id}",
            {
                "field_list": (
                    "id,"
                    "name,"
                    "issue_number,"
                    "description,"
                    "store_date,"
                    "volume,"
                    "person_credits,"
                    "character_credits,"
                    "team_credits,"
                    "location_credits,"
                    "story_arc_credits,"
                    "site_detail_url"
                )
            }
        )
        
        return data["results"]
    
    def get_volume(self, volume_id: int) -> dict:
        """
        Retrieves the complete ComicVine volume record.
        """
        
        data = self._get(
            f"volume/4050-{volume_id}",
            {
                "field_list": (
                    "id,"
                    "name,"
                    "start_year,"
                    "publisher,"
                    "count_of_issues,"
                    "description,"
                    "site_detail_url"
                )
            }
        )
        
        return data["results"]
        
    
        
        