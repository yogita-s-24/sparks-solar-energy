"""Enquiry form with server-side validation and input clean-up."""
import re
import unicodedata

from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

PROPERTY_TYPES = [
    ("", "Select property type"),
    ("residential", "Residential (home)"),
    ("agricultural", "Agricultural (farm / pump)"),
    ("commercial", "Commercial (shop / office / industry)"),
    ("other", "Other / not sure"),
]
PROPERTY_LABELS = dict(PROPERTY_TYPES[1:])

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+'-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")


def clean_text(value, multiline=False):
    """Strip control characters and collapse whitespace."""
    if value is None:
        return None
    value = unicodedata.normalize("NFC", str(value))
    allowed = {"\n"} if multiline else set()
    value = "".join(
        ch for ch in value
        if ch in allowed or unicodedata.category(ch)[0] != "C"
    )
    if multiline:
        lines = [" ".join(line.split()) for line in value.replace("\r", "").split("\n")]
        value = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
        return value.strip()
    return " ".join(value.split())


def normalize_indian_phone(value):
    """Return +91XXXXXXXXXX for a valid Indian mobile number, else None."""
    digits = re.sub(r"[\s\-().]", "", value or "")
    if digits.startswith("+"):
        digits = digits[1:]
    if not digits.isdigit():
        return None
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 10 and digits[0] in "6789":
        return "+91" + digits
    return None


class EnquiryForm(FlaskForm):
    name = StringField(
        "Your name",
        filters=[clean_text],
        validators=[DataRequired("Please tell us your name."), Length(2, 80, "Name should be 2–80 characters.")],
    )
    phone = StringField(
        "Phone number",
        filters=[clean_text],
        validators=[DataRequired("Please enter a phone number so we can call you back.")],
    )
    email = StringField(
        "Email (optional)",
        filters=[clean_text],
        validators=[Optional(), Length(max=120, message="Email is too long.")],
    )
    property_type = SelectField(
        "Property type",
        choices=PROPERTY_TYPES,
        validate_choice=False,  # checked in validate_property_type with a friendlier message
        validators=[DataRequired("Please choose a property type.")],
    )
    location = StringField(
        "Location (village / town)",
        filters=[clean_text],
        validators=[DataRequired("Please tell us where the property is."), Length(2, 120, "Location should be 2–120 characters.")],
    )
    monthly_bill = IntegerField(
        "Monthly electricity bill in ₹ (optional)",
        validators=[Optional(), NumberRange(0, 10000000, "Please enter a realistic monthly bill amount.")],
    )
    message = TextAreaField(
        "Your requirements",
        filters=[lambda v: clean_text(v, multiline=True)],
        validators=[Optional(), Length(max=1500, message="Please keep your message under 1500 characters.")],
    )
    source = HiddenField(filters=[clean_text])
    # Honeypot: humans never see or fill this field.
    website = StringField("Leave this field empty", filters=[clean_text])

    @staticmethod
    def aria(field):
        """Accessibility attributes linking a field to its error message."""
        if field.errors:
            return {"aria-invalid": "true", "aria-describedby": f"{field.id}-error"}
        return {}

    def validate_phone(self, field):
        normalized = normalize_indian_phone(field.data)
        if not normalized:
            raise ValidationError("Please enter a valid 10-digit Indian mobile number, e.g. 98765 43210.")
        field.data = normalized

    def validate_email(self, field):
        if field.data:
            if not EMAIL_RE.match(field.data):
                raise ValidationError("Please enter a valid email address or leave it blank.")
            field.data = field.data.lower()

    def validate_property_type(self, field):
        if field.data not in PROPERTY_LABELS:
            raise ValidationError("Please choose a property type.")
