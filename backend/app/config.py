"""
Central place for environment-driven settings.
Everything is read once at import time so the rest of the app
just does `from app.config import settings`.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_EXTRACTION_MODEL: str = os.getenv("GROQ_EXTRACTION_MODEL", "gemma2-9b-it")
    GROQ_REASONING_MODEL: str = os.getenv("GROQ_REASONING_MODEL", "llama-3.3-70b-versatile")

    DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://complaint_qms_user:WZJ9P6UQ5ccEG0NUZcRsM06QBFSavbMn@dpg-d9krqttbedkc73bbk560-a.singapore-postgres.render.com:5432/complaint_qms"
)
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "https://ai-pharma-complaint-management-syst-eight.vercel.app")


settings = Settings()
