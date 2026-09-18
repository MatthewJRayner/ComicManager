import re

from difflib import SequenceMatcher
from dataclasses import dataclass

MINIMUM_SCORE = 0.80
MINIMUM_SCORE_DIFFERENCE = 0.05

@dataclass
class VolumeMatch:
    volume: dict | None
    score: float
    status: str
    
@dataclass
class VolumeCandidate:
    volume: dict
    score: float
    
def get_start_year(candidate: dict) -> int | None:
    """
    Returns a candidate's start year as an integer, and returns None when candidate has no valid start year.
    """
    start_year = candidate.get("start_year")
    
    if start_year is None:
        return None
    
    try:
        return int(start_year)
    except (TypeError, ValueError):
        return None
    

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
    filtered_candidates = []
    
    for candidate in candidates:
        start_year = get_start_year(candidate)
        
        if start_year is None:
            filtered_candidates.append(candidate)
            continue
            
        if start_year <= issue_year:
            filtered_candidates.append(candidate)
            
    return filtered_candidates
    
    
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
    
def find_volume_candidates(
    series: str,
    issue_year: int,
    candidates: list[dict]
) -> list[VolumeCandidate]:
    """
    Retunrs ComicVine volumes that are plausible candidates for the requested series and issue year.
    """
    
    candidates = filter_by_year(candidates, issue_year)
    
    matching_candidates = []
    
    for candidate in candidates:
        score = name_similarity(series, candidate.get("name", ""))
        
        if score >= MINIMUM_SCORE:
            matching_candidates.append(
                VolumeCandidate(volume=candidate, score=score)
            )
    
    matching_candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    
    return matching_candidates

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
        return VolumeMatch(volume=None, score=0.0, status="no_match")
    
    scored_candidates = []
    
    for candidate in candidates:
        score = name_similarity(series, candidate.get("name", ""))
        scored_candidates.append((score, candidate))
        
    scored_candidates.sort(key=lambda item: item[0], reverse=True)
    
    best_score, best_candidate = scored_candidates[0]
    
    if best_score < MINIMUM_SCORE:
        return VolumeMatch(volume=None, score=best_score, status="no_match")
    
    if len(scored_candidates) == 1:
        return VolumeMatch(volume=best_candidate, score=best_score, status="matched")
    
    second_score = scored_candidates[1][0]
    
    if best_score - second_score < MINIMUM_SCORE_DIFFERENCE:
        return VolumeMatch(volume=None, score=best_score, status="ambiguous")
    
    return VolumeMatch(volume=best_candidate, score=best_score, status="matched")
    