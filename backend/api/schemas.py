from pydantic import BaseModel
from typing import List, Dict

class AnalyzeRequest(BaseModel):
    role: str
    manual_skills: List[str] = []

class AnalyzeResponse(BaseModel):
    match_score: float
    user_skills: List[str]
    missing_skills: List[str]
    recommendations: Dict[str, List[str]]
