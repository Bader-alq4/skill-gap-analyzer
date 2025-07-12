import json
from pathlib import Path
import numpy as np
from .embedder import get_embeddings


def load_role_skills(path: str = None) -> dict[str, list[str]]:
    """
    Load a mapping of roles to required skills from a JSON file.
    Defaults to 'roles.json' in the backend/ directory.
    """
    if path is None:
        path = Path(__file__).parent.parent / "roles.json"
    return json.loads(Path(path).read_text())


def compute_missing(user_skills: list[str], role_skills: list[str]) -> list[str]:
    """
    Return sorted list of skills required by the role that the user does not have,
    comparing skills case-insensitively but returning them in their original casing.
    """
    # Map lowercased role skills to original
    lc_role_map = {skill.lower(): skill for skill in role_skills}
    role_lc_set = set(lc_role_map.keys())

    # Lowercase user skills for comparison
    user_lc_set = {s.lower().strip() for s in user_skills}

    # Determine missing in lower-case
    missing_lc = role_lc_set - user_lc_set

    # Map back to original casing, sort alphabetically
    missing = sorted(lc_role_map[lc] for lc in missing_lc)
    return missing


def compute_per_skill_score(user_skills: list[str], role_skills: list[str]) -> float:
    """
    Compute a semantic match score between user_skills and role_skills by averaging
    the best cosine similarity for each required skill.
    Exact string matches (case-insensitive) get full credit.
    Returns a percentage (0.0 to 100.0).
    """
    if not role_skills or not user_skills:
        return 0.0

    # Embed all unique skills
    all_skills = list({s for s in user_skills + role_skills})
    embeds = get_embeddings(all_skills)
    idx = {skill: i for i, skill in enumerate(all_skills)}

    # Precompute norms
    norms = np.linalg.norm(embeds, axis=1)

    # Compute per-role-skill similarity
    sims = []
    for r in role_skills:
        r_idx = idx[r]
        r_vec = embeds[r_idx]
        r_norm = norms[r_idx]

        best = 0.0
        for u in user_skills:
            # Case-insensitive exact match
            if u.strip().lower() == r.strip().lower():
                best = 1.0
                break
            u_idx = idx[u]
            u_vec = embeds[u_idx]
            u_norm = norms[u_idx]
            sim = float(np.dot(r_vec, u_vec) / (r_norm * u_norm + 1e-8))
            best = max(best, sim)
        sims.append(best)

    score = float(np.mean(sims)) * 100.0
    return round(score, 2)


def compute_match_score(user_skills: list[str], role_skills: list[str]) -> float:
    """
    Alias to compute_per_skill_score for backward compatibility.
    """
    return compute_per_skill_score(user_skills, role_skills)
