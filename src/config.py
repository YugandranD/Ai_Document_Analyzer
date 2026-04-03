"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Authentication
API_KEY = os.getenv("API_KEY", "sk_track2_987654321")

# Groq AI
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Tesseract OCR path (Windows default)
TESSERACT_PATH = os.getenv(
    "TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Redis / Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
