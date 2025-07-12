from backend.core import parser

def test_skill_extraction():
    text = """
    I have experience with Python, Docker, and TensorFlow. 
    I also used Kubernetes in my last job and am learning FastAPI.
    """
    skills = parser.extract_skills(text)
    expected = ["Docker", "FastAPI", "Kubernetes", "Python", "TensorFlow"]
    assert sorted(skills) == sorted(expected)
