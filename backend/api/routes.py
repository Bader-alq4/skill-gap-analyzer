# backend/api/routes.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional

from backend.core.parser import extract_text, extract_skills, extract_user_skills_manual
from backend.core.analyzer import load_role_skills, compute_match_score, compute_missing
from backend.core.recommender import get_recommendations
from .schemas import AnalyzeRequest, AnalyzeResponse

router = APIRouter()
# Load role definitions once at startup
roles_map = load_role_skills()

@router.get("/roles", response_model=List[str])
def list_roles():
    """
    Return all available role names for the frontend dropdown.
    """
    return list(roles_map.keys())

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    file: Optional[UploadFile] = File(None),
    role: str = Form(...),
    manual_skills: Optional[str] = Form(None)
):
    """
    Analyze a resume PDF or manual skills list against a chosen role.
    Returns match score, extracted or manual user skills, missing skills, and LLM recommendations.
    """
    # 1. Determine user skills
    if file:
        # PDF upload path
        pdf_bytes = await file.read()
        text = extract_text(pdf_bytes)
        user_skills = extract_skills(text)
    else:
        # Manual entry path, using fuzzy normalization
        user_skills = extract_user_skills_manual(manual_skills or "")

    # 2. Validate role
    if role not in roles_map:
        raise HTTPException(status_code=400, detail="Unknown role")

    # 3. Perform analysis
    role_skills = roles_map[role]
    score = compute_match_score(user_skills, role_skills)
    missing = compute_missing(user_skills, role_skills)
    recs = get_recommendations(missing)

    # 4. Return structured response
    return AnalyzeResponse(
        match_score=score,
        user_skills=user_skills,
        missing_skills=missing,
        recommendations=recs
    )
