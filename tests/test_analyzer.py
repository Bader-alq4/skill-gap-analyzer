from backend.core.analyzer import load_role_skills, compute_match_score, compute_missing

def test_load_roles():
    roles = load_role_skills()
    assert "Data Scientist" in roles
    assert "Python" in roles["Data Scientist"]

def test_match_and_missing():
    user = ["Python", "SQL"]
    role = ["Python", "SQL", "Docker"]
    score = compute_match_score(user, role)
    assert isinstance(score, float) and 0 <= score <= 100
    missing = compute_missing(user, role)
    assert missing == ["Docker"]
