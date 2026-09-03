import os
import requests

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
        
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            params=params,
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
            }
        )
        
        return data.get("results", [])
        