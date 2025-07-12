from fastapi import FastAPI
from .routes import router

app = FastAPI(title="AI Skill Gap Analyzer")
app.include_router(router, prefix="/api")
