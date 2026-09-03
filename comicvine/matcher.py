import re

from difflib import SequenceMatcher
from dataclasses import dataclass

@dataclass
class VolumeMatch:
    volume: dict | None
    score: float
    confident: bool

def normalize_name(name: str) -> str:
    """
    Normalizes a series name for comparison by removing non-alphanumeric characters and converting to lowercase.
    """
    
    name = name.lower()
    name = re.sub(r"[^\w\s]", " ", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()

def filter_by_year(
    candidates: list[dict],
    issue_year: int
) -> list[dict]:
    """
    Removes volumes that started after the issue year. 
    """
    
    return [
        candidate
        for candidate in candidates
        if (
            candidate.get("start_year") is None
            or candidate["start_year"] <= issue_year
        )
    ]
    
    
def name_similarity(
    name_a: str,
    name_b: str
) -> float:
    """
    Returns a similarity score between 0 and 1 for two series names.
    """
    normalized_a = normalize_name(name_a)
    normalized_b = normalize_name(name_b)
    
    return SequenceMatcher(
        None,
        normalized_a,
        normalized_b
    ).ratio()
    
def match_volume(
    series: str,
    issue_year: int,
    candidates: list[dict]
) -> VolumeMatch:
    """
    Finds the best ComicVine volume candidate for a series and issue year.
    Returns a VolumeMatch object containing the best match, its score, and whether the match is confident.
    """
    
    candidates = filter_by_year(candidates, issue_year)
    
    if not candidates:
        return VolumeMatch(volume=None, score=0.0, confident=False)
    
    scored_candidates = []
    
    for candidate in candidates:
        score = name_similarity(series, candidate.get("name", ""))
        scored_candidates.append((score, candidate))
        
    scored_candidates.sort(key=lambda item: item[0], reverse=True)
    
    best_score, best_candidate = scored_candidates[0]
    
    return VolumeMatch(volume=best_candidate, score=best_score, confident=False) # Will revists later to determine confidence levels
    