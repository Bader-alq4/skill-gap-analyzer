# backend/core/parser.py

import re
import spacy
import fitz  # PyMuPDF
import difflib

# Load spaCy model for NER (if used for additional skill detection)
nlp = spacy.load("en_core_web_sm")

# Canonical known skills list (exact forms)
KNOWN_SKILLS = [
    "Python", "Docker", "Kubernetes", "TensorFlow", "PyTorch",
    "FastAPI", "SQL", "REST"
]
# Lowercase for fuzzy matching lookups
KNOWN_LC = [s.lower() for s in KNOWN_SKILLS]

# Regex pattern to catch exact keyword matches
pattern = re.compile(r"\b(?:" + "|".join(KNOWN_SKILLS) + r")\b", flags=re.IGNORECASE)


def normalize_skill(raw: str, cutoff: float = 0.7) -> str:
    """
    Normalize a raw skill string to a canonical skill from KNOWN_SKILLS.
    Uses substring matching, fuzzy matching, and regex for best coverage.
    If no close match exceeds cutoff, return the original raw string.
    """
    word = raw.strip()
    if not word:
        return word
    lw = word.lower()

    # 1. Exact-case-insensitive match via regex
    for skill in KNOWN_SKILLS:
        if re.fullmatch(skill, word, flags=re.IGNORECASE):
            return skill

    # 2. Substring match: e.g. 'dockerized' contains 'docker'
    for skill in KNOWN_SKILLS:
        if skill.lower() in lw:
            return skill

    # 3. Fuzzy matching with difflib
    matches = difflib.get_close_matches(lw, KNOWN_LC, n=1, cutoff=cutoff)
    if matches:
        idx = KNOWN_LC.index(matches[0])
        return KNOWN_SKILLS[idx]

    # 4. No match: return raw input
    return word


def extract_text(pdf_bytes: bytes) -> str:
    """
    Extract all text from a PDF file provided as bytes.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def extract_skills(text: str) -> list[str]:
    """
    Extract skills from plain text using regex + spaCy NER on KNOWN_SKILLS,
    then normalize each via fuzzy matching.
    """
    # 1. Regex-based exact matches
    found = {m.group(0) for m in pattern.finditer(text)}
    # 2. spaCy NER for entities matching known skills
    doc = nlp(text)
    for ent in doc.ents:
        if ent.text in KNOWN_SKILLS:
            found.add(ent.text)
    # 3. Fuzzy normalize all found skills
    normalized = [normalize_skill(s) for s in found]
    # 4. Return sorted unique list
    return sorted(set(normalized))


def extract_user_skills_manual(manual_input: str) -> list[str]:
    """
    Parse and normalize comma-separated manual input skills.
    """
    raw_skills = [s for s in manual_input.split(",") if s.strip()]
    return [normalize_skill(s) for s in raw_skills]
