"""Production entry point.

    waitress-serve --listen=0.0.0.0:8000 wsgi:app      (Windows or Linux)
    gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app             (Linux)
"""
from app import app

if app.config["SECRET_KEY"] == "dev-only-change-me":
    raise RuntimeError("Set SECRET_KEY in the environment or .env before running in production.")
