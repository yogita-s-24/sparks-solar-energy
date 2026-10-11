"""Optional email notification for new enquiries via SMTP."""
import smtplib
import ssl
from email.message import EmailMessage

from forms import PROPERTY_LABELS


def mail_configured(config):
    return bool(config.get("MAIL_SERVER") and config.get("MAIL_TO") and (config.get("MAIL_FROM") or config.get("MAIL_USERNAME")))


def send_enquiry_email(config, enquiry, logger):
    """Send the enquiry to MAIL_TO. Returns True only if the SMTP server accepted it."""
    if not mail_configured(config):
        return False

    msg = EmailMessage()
    msg["Subject"] = f"New solar enquiry: {enquiry['name']} ({PROPERTY_LABELS.get(enquiry['property_type'], enquiry['property_type'])})"
    msg["From"] = config.get("MAIL_FROM") or config["MAIL_USERNAME"]
    msg["To"] = config["MAIL_TO"]
    if enquiry.get("email"):
        msg["Reply-To"] = enquiry["email"]
    bill = f"₹{enquiry['monthly_bill']:,}" if enquiry.get("monthly_bill") is not None else "Not provided"
    msg.set_content(
        "A new enquiry was submitted on the SPARKS SOLAR ENERGY website.\n\n"
        f"Name:          {enquiry['name']}\n"
        f"Phone:         {enquiry['phone']}\n"
        f"Email:         {enquiry.get('email') or 'Not provided'}\n"
        f"Property type: {PROPERTY_LABELS.get(enquiry['property_type'], enquiry['property_type'])}\n"
        f"Location:      {enquiry['location']}\n"
        f"Monthly bill:  {bill}\n"
        f"Submitted via: {enquiry.get('source') or 'website'}\n\n"
        f"Requirements:\n{enquiry.get('message') or '(none)'}\n"
    )

    try:
        context = ssl.create_default_context()
        if config.get("MAIL_USE_SSL"):
            server = smtplib.SMTP_SSL(config["MAIL_SERVER"], config["MAIL_PORT"], timeout=config["MAIL_TIMEOUT"], context=context)
        else:
            server = smtplib.SMTP(config["MAIL_SERVER"], config["MAIL_PORT"], timeout=config["MAIL_TIMEOUT"])
        with server:
            if config.get("MAIL_USE_TLS") and not config.get("MAIL_USE_SSL"):
                server.starttls(context=context)
            if config.get("MAIL_USERNAME"):
                server.login(config["MAIL_USERNAME"], config["MAIL_PASSWORD"])
            server.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Enquiry email could not be sent: %s", exc)
        return False
