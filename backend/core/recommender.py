# backend/core/recommender.py

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, RateLimitError
import os, json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. Strong system prompt + few-shot example
SYSTEM_PROMPT = """
You are a JSON-only career advisor. When given a list of missing skills,
you must reply *exactly* with a single JSON object and *nothing else*.
Do not provide any extra text or markdown.

Example format:
User: The user is missing these skills: Pandas, SQL.
Assistant:
{
  "courses": ["Intro to Pandas", "SQL for Data Analysis", "Data Engineering Fundamentals"],
  "projects": ["Analyze sales data with Pandas", "Build a SQL dashboard", "ETL pipeline project"],
  "certifications": ["Pandas Certification", "SQL Certification", "Data Engineering Certificate"]
}

Now, respond in that exact JSON-only format.
"""

# 2. User template remains simple—skills will be filled in
USER_TEMPLATE = "The user is missing these skills: {skills}."

def get_recommendations(missing: list[str]) -> dict:
    if not missing:
        return {"courses": [], "projects": [], "certifications": []}

    messages = [
        {"role": "system",  "content": SYSTEM_PROMPT.strip()},
        {"role": "user",    "content": USER_TEMPLATE.format(skills=", ".join(missing))}
    ]

    try:
        # 3. Lock randomness to zero for determinism
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.0,
            top_p=1.0,
            max_tokens=250
        )
        content = resp.choices[0].message.content.strip()

        # Sanity check: must be a JSON object
        if not (content.startswith("{") and content.endswith("}")):
            raise ValueError(f"Unexpected format: {content!r}")

        return json.loads(content)

    except (RateLimitError, OpenAIError) as e:
        return {
            "courses": [f"[LLM error: {e}]"],
            "projects": [],
            "certifications": []
        }
    except (ValueError, json.JSONDecodeError):
        return {
            "courses": ["[Failed to parse LLM output — ensure it’s valid JSON]"],
            "projects": [],
            "certifications": []
        }
