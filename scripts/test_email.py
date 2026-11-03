"""Send a test enquiry email using the settings in .env.

Run from the project folder:  python scripts/test_email.py
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from notifications import mail_configured, send_enquiry_email

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("test_email")

config = {k: getattr(Config, k) for k in dir(Config) if k.isupper()}
if not mail_configured(config):
    sys.exit("Email is not configured. Fill in MAIL_USERNAME, MAIL_PASSWORD and MAIL_TO in .env.")

enquiry = {
    "name": "Test Customer",
    "phone": "9999999999",
    "email": None,
    "property_type": "home",
    "location": "Test location",
    "monthly_bill": 2000,
    "message": "This is a test email from scripts/test_email.py.",
    "source": "test",
}
if send_enquiry_email(config, enquiry, log):
    print(f"Sent. Check the inbox of {config['MAIL_TO']} (and the Spam folder).")
else:
    sys.exit("Sending failed. See the error above.")
