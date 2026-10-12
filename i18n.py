"""English / Marathi language switching.

English text is the translation key: templates call ``_("English text")`` and
get the Marathi version from ``translations_mr.MR`` when Marathi is selected.
Text without a Marathi entry falls back to English (tests list any gaps).
"""
from datetime import date

from flask import has_request_context, request

from translations_mr import MR

LANGUAGES = {"en": "English", "mr": "मराठी"}
DEFAULT_LANG = "mr"
COOKIE_NAME = "lang"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365

# English keys asked for in Marathi that have no translation (checked by tests).
MISSING = set()

_MONTHS_MR = ["जानेवारी", "फेब्रुवारी", "मार्च", "एप्रिल", "मे", "जून",
              "जुलै", "ऑगस्ट", "सप्टेंबर", "ऑक्टोबर", "नोव्हेंबर", "डिसेंबर"]


def get_lang():
    if has_request_context():
        lang = request.cookies.get(COOKIE_NAME)
        if lang in LANGUAGES:
            return lang
    return DEFAULT_LANG


def gettext(text, **values):
    """Translate English ``text`` into the current language, then fill {placeholders}."""
    if not text:
        return text
    if get_lang() == "mr":
        translated = MR.get(text)
        if translated is None:
            MISSING.add(text)
            translated = text
    else:
        translated = text
    return translated.format(**values) if values else translated


def format_date(value: date, short=False):
    """'31 March 2027' (or '31 Mar 2027') in English, '31 मार्च 2027' in Marathi."""
    if get_lang() == "mr":
        return f"{value.day} {_MONTHS_MR[value.month - 1]} {value.year}"
    return f"{value.day} {value.strftime('%b' if short else '%B')} {value.year}"
