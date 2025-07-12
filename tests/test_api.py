from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_list_roles():
    resp = client.get("/api/roles")
    assert resp.status_code == 200
    assert "Data Scientist" in resp.json()

def test_analyze_manual():
    resp = client.post(
        "/api/analyze",
        data={"role": "Backend Engineer", "manual_skills": "Python,FastAPI"}
    )
    assert resp.status_code == 200
    json = resp.json()
    assert "match_score" in json
    assert isinstance(json["missing_skills"], list)
    assert isinstance(json["recommendations"], dict)
