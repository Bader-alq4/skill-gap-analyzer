# backend/core/parser.py

import re
import json
from pathlib import Path
import spacy
import fitz  # PyMuPDF
import difflib
from backend.core.analyzer import load_role_skills

# ----------------------------------------------------------------------------
# 1. Load skills from external JSON and roles.json, then union them
# ----------------------------------------------------------------------------

def load_known_skills(path: Path | str = None) -> list[str]:
    """
    Load a list of canonical skills from known_skills.json.
    Defaults to 'known_skills.json' in this directory.
    """
    if path is None:
        path = Path(__file__).parent / "known_skills.json"
    return json.loads(Path(path).read_text())

# a) Skills explicitly defined in known_skills.json
_known = set(load_known_skills())
# b) Skills listed per-role in roles.json
_roles = set(
    skill
    for skills in load_role_skills().values()
    for skill in skills
)
# c) Combine into a single canonical set
KNOWN_SKILLS = sorted(_known | _roles)

# Lowercase list for fuzzy matching
KNOWN_LC = [s.lower() for s in KNOWN_SKILLS]

# Compile a regex to catch any exact-skill mention
pattern = re.compile(
    r"\b(?:" + "|".join(map(re.escape, KNOWN_SKILLS)) + r")\b",
    flags=re.IGNORECASE,
)
# ----------------------------------------------------------------------------
# 2. Normalization & Extraction Helpers
# ----------------------------------------------------------------------------

def normalize_skill(raw: str, cutoff: float = 0.7) -> str:
    """
    Normalize a raw skill string to a canonical skill from KNOWN_SKILLS:
    1. exact match, 2. substring, 3. difflib fuzzy match, or 4. return raw
    """
    word = raw.strip()
    if not word:
        return word
    lw = word.lower()

    # 1. Exact-case-insensitive match
    for skill in KNOWN_SKILLS:
        if re.fullmatch(skill, word, flags=re.IGNORECASE):
            return skill

    # 2. Substring match
    for skill in KNOWN_SKILLS:
        if skill.lower() in lw:
            return skill

    # 3. Fuzzy match
    match = difflib.get_close_matches(lw, KNOWN_LC, n=1, cutoff=cutoff)
    if match:
        idx = KNOWN_LC.index(match[0])
        return KNOWN_SKILLS[idx]

    # 4. No match
    return word


def extract_text(pdf_bytes: bytes) -> str:
    """
    Extract all text from a PDF file provided as bytes.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def extract_skills(text: str) -> list[str]:
    """
    Extract skills from text by:
      1. regex exact matches
      2. spaCy NER against KNOWN_SKILLS
      3. fuzzy normalization
    """
    found = {m.group(0) for m in pattern.finditer(text)}
    doc = nlp(text)
    for ent in doc.ents:
        if ent.text in KNOWN_SKILLS:
            found.add(ent.text)
    normalized = [normalize_skill(s) for s in found]
    return sorted(set(normalized))


def extract_user_skills_manual(manual_input: str) -> list[str]:
    """
    Parse and normalize comma-separated manual input skills.
    """
    raw_skills = [s for s in manual_input.split(",") if s.strip()]
    return [normalize_skill(s) for s in raw_skills]

# Load spaCy model after function definitions to avoid startup errors in tests
nlp = spacy.load("en_core_web_sm")
