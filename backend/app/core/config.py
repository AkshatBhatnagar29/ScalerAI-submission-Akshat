import os
from pathlib import Path


MOCK_USERNAME = os.getenv("MOCK_USERNAME", "admin")
MOCK_PASSWORD = os.getenv("MOCK_PASSWORD", "admin123")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
SESSION_COOKIE_NAME = "route53_session"
SESSION_MAX_AGE = 60 * 60 * 8
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax").lower()
if COOKIE_SAMESITE not in {"lax", "strict", "none"}:
    raise ValueError("COOKIE_SAMESITE must be one of: lax, strict, none")
BACKEND_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(BACKEND_DIR / 'data' / 'route53.db').as_posix()}")
