import streamlit as st
import requests
import os

# Load environment variables if needed
from dotenv import load_dotenv
load_dotenv()

# Backend API base URL (can override with .env)
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api")


# Page configuration
st.set_page_config(
    page_title="AI Skill Gap Analyzer", layout="wide"
)

# Title and description
st.title("🚀 AI Skill Gap Analyzer & Career Path Recommender")
st.write("Upload your resume or enter skills manually to see how you match different roles, and get personalized learning recommendations.")

# Input mode selection
detection_mode = st.radio(
    "Choose input mode:",
    ["Upload Resume", "Manual Skills"],
    index=0
)

user_skills = []
resume_file = None

if detection_mode == "Upload Resume":
    resume_file = st.file_uploader("Upload your PDF resume", type=["pdf"])
    if resume_file:
        st.success("Resume uploaded. Ready to analyze.")
else:
    manual_input = st.text_input("Enter your skills, comma-separated:")
    if manual_input:
        user_skills = [s.strip() for s in manual_input.split(",") if s.strip()]

# Fetch available roles from backend
try:
    roles = requests.get(f"{API_BASE}/roles").json()
except Exception as e:
    st.error(f"Failed to load roles from API: {e}")
    st.stop()

# Role selection
default_index = 0
if "selected_role" not in st.session_state:
    st.session_state.selected_role = roles[0] if roles else ""

selected_role = st.selectbox(
    "Select a role to compare against:",
    roles,
    index=roles.index(st.session_state.selected_role) if st.session_state.selected_role in roles else 0,
    key="selected_role"
)

# Analyze button triggers API call
if st.button("🔍 Analyze My Skills"):
    # Prepare payload
    files = None
    data = {"role": selected_role}
    if detection_mode == "Upload Resume" and resume_file:
        files = {"file": (resume_file.name, resume_file.getvalue(), "application/pdf")}
    else:
        data["manual_skills"] = ",".join(user_skills)

    # Call backend
    try:
        response = requests.post(
            f"{API_BASE}/analyze", files=files, data=data
        )
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        st.error(f"API request failed: {e}")
        st.stop()

    # Display results
    st.markdown("---")
    st.metric(label="🏆 Match Score", value=f"{result['match_score']}%")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔍 Your Skills")
        st.write(result["user_skills"])
    with col2:
        st.subheader("🚧 Missing Skills")
        st.write(result["missing_skills"])

    st.subheader("📚 Recommended Learning Path")
    st.json(result["recommendations"])
