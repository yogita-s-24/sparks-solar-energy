"""Application settings for the SPARKS SOLAR ENERGY website.

Secrets and deployment-specific values come from environment variables
(see .env.example). Business details and calculator assumptions live here so
they can be updated in one place without touching templates.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# --------------------------------------------------------------------------
# Verified business information. Only change these with confirmed details.
# --------------------------------------------------------------------------
BUSINESS = {
    "name": "SPARKS SOLAR ENERGY",
    "short_name": "Sparks Solar",
    "tagline": "Power Your Future. Shine Brighter with Solar.",
    "description": (
        "SPARKS SOLAR ENERGY plans and installs solar energy solutions for homes, "
        "farms, shops, offices and industries from Deolali Pravara, Rahuri taluka, "
        "Ahilya Nagar district, Maharashtra."
    ),
    "phone_display": "+91 9356806280",
    "phone_tel": "+919356806280",
    # Digits only, with country code, for https://wa.me/<number>
    "whatsapp_number": "919356806280",
    "whatsapp_message": (
        "Hello SPARKS SOLAR ENERGY, I would like to know more about solar "
        "installation for my property."
    ),
    "email": os.environ.get("BUSINESS_EMAIL", ""),
    "address": {
        # Shop/building line from the business flyer. Confirm before launch.
        "street": os.environ.get("BUSINESS_STREET", ""),
        "locality": "Deolali Pravara",
        "taluka": "Tal. Rahuri",
        "district": "Dist. Ahilya Nagar",
        "region": "Maharashtra",
        "postal_code": os.environ.get("BUSINESS_POSTAL_CODE", ""),
        "country": "India",
        "country_code": "IN",
    },
    # Only list profiles that have been confirmed to belong to the business.
    "instagram_url": os.environ.get(
        "INSTAGRAM_URL", "https://www.instagram.com/sparkssolarenergy/"
    ),
    "maps_url": (
        "https://www.google.com/maps/search/?api=1&query="
        "Deolali+Pravara%2C+Rahuri%2C+Ahilya+Nagar%2C+Maharashtra"
    ),
}


# --------------------------------------------------------------------------
# Solar estimator assumptions (illustrative only, never a quotation).
# "offset_low"/"offset_high" are the share of the current electricity bill a
# suitably sized system *might* offset. Adjust them to match your own
# experience with local tariffs and installations.
# --------------------------------------------------------------------------
CALCULATOR = {
    "min_bill": 200,
    "max_bill": 1000000,
    "default_bill": 3000,
    "slider_max": 50000,
    "property_types": {
        "residential": {"label": "Residential", "offset_low": 0.40, "offset_high": 0.80},
        "agricultural": {"label": "Agricultural", "offset_low": 0.30, "offset_high": 0.70},
        "commercial": {"label": "Commercial", "offset_low": 0.25, "offset_high": 0.60},
    },
}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:5000").rstrip("/")

    DATABASE = os.environ.get("DATABASE_PATH", "")  # default: instance/enquiries.sqlite3
    DUPLICATE_WINDOW_MINUTES = int(os.environ.get("DUPLICATE_WINDOW_MINUTES", "10"))

    # Email notifications for new enquiries (optional).
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = env_bool("MAIL_USE_TLS", True)
    MAIL_USE_SSL = env_bool("MAIL_USE_SSL", False)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_FROM = os.environ.get("MAIL_FROM", "")
    MAIL_TO = os.environ.get("MAIL_TO", "")
    MAIL_TIMEOUT = 10

    # Shows clearly marked "to be confirmed" boxes for missing business details.
    SHOW_PLACEHOLDERS = env_bool("SHOW_PLACEHOLDERS", True)

    WTF_CSRF_TIME_LIMIT = 60 * 60 * 6
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
    SEND_FILE_MAX_AGE_DEFAULT = 60 * 60 * 24 * 7
    MAX_CONTENT_LENGTH = 64 * 1024

    BUSINESS = BUSINESS
    CALCULATOR = CALCULATOR


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test"
    MAIL_SERVER = ""
