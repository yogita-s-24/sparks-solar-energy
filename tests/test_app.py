import re
import sqlite3

import pytest

from app import create_app
from config import TestConfig
from forms import clean_text, normalize_indian_phone

VALID = {
    "name": "Asha Patil",
    "phone": "98765 43210",
    "email": "asha@example.com",
    "property_type": "residential",
    "location": "Rahuri",
    "monthly_bill": "2500",
    "message": "RCC roof, about 600 sq ft.",
    "source": "home",
}


@pytest.fixture
def app(tmp_path):
    class Cfg(TestConfig):
        DATABASE = str(tmp_path / "test.sqlite3")

    return create_app(Cfg)


@pytest.fixture
def client(app):
    # Most tests check English text; Marathi is the site default (see mr_client).
    c = app.test_client()
    c.set_cookie("lang", "en")
    return c


def rows(app):
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM enquiries ORDER BY id").fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
@pytest.mark.parametrize("path", ["/", "/about", "/solutions", "/contact", "/privacy", "/contact/thank-you"])
def test_pages_render(client, path):
    res = client.get(path)
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "<title>" in html and 'name="description"' in html
    assert 'rel="canonical"' in html


def test_home_has_key_sections_and_contact_links(client):
    html = client.get("/").get_data(as_text=True)
    for anchor in ('id="solutions"', 'id="benefits"', 'id="how-it-works"', 'id="estimator"', 'id="gallery"', 'id="faq"', 'id="enquiry"'):
        assert anchor in html
    assert 'href="tel:+919356806280"' in html
    assert "https://wa.me/919356806280?text=" in html
    assert "images/projects/" in html
    assert "data-calculator=" in html


def test_structured_data_uses_business_details(client):
    html = client.get("/").get_data(as_text=True)
    assert '"@type": "LocalBusiness"' in html
    assert '"telephone": "+919356806280"' in html
    assert '"addressLocality": "Deolali Pravara"' in html


def test_404(client):
    res = client.get("/does-not-exist")
    assert res.status_code == 404
    assert "This page is in the shade" in res.get_data(as_text=True)


def test_robots_and_sitemap(client):
    robots = client.get("/robots.txt")
    assert robots.status_code == 200 and "Sitemap:" in robots.get_data(as_text=True)
    sitemap = client.get("/sitemap.xml")
    assert sitemap.status_code == 200
    body = sitemap.get_data(as_text=True)
    assert "<urlset" in body and "/solutions" in body and "thank-you" not in body


def test_security_headers(client):
    res = client.get("/")
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in res.headers["Content-Security-Policy"]


def test_contact_preselects_property_type(client):
    html = client.get("/contact?type=agricultural").get_data(as_text=True)
    assert re.search(r'<option selected value="agricultural">|<option value="agricultural" selected>', html)


def test_static_assets_exist(client):
    for path in ("/static/css/output.css", "/static/js/main.js", "/static/js/animations.js",
                 "/static/js/calculator.js", "/static/images/icons/sprite.svg", "/static/favicon/favicon.ico"):
        assert client.get(path).status_code == 200, path


# --------------------------------------------------------------------------
# Validation helpers
# --------------------------------------------------------------------------
@pytest.mark.parametrize("raw,expected", [
    ("9876543210", "+919876543210"),
    ("+91 98765-43210", "+919876543210"),
    ("919876543210", "+919876543210"),
    ("09876543210", "+919876543210"),
    ("(98765) 43210", "+919876543210"),
    ("12345", None),
    ("5876543210", None),
    ("98765432101", None),
    ("98765abcde", None),
    ("", None),
])
def test_normalize_indian_phone(raw, expected):
    assert normalize_indian_phone(raw) == expected


def test_clean_text_strips_control_chars_and_whitespace():
    assert clean_text("  Asha\x00   Patil \t") == "Asha Patil"
    assert clean_text("line one\r\n\n\n\nline   two", multiline=True) == "line one\n\nline two"


# --------------------------------------------------------------------------
# Enquiry submission
# --------------------------------------------------------------------------
def test_valid_enquiry_is_saved_and_redirects(client, app):
    res = client.post("/contact", data=VALID)
    assert res.status_code == 302
    assert "/contact/thank-you" in res.headers["Location"]
    saved = rows(app)
    assert len(saved) == 1
    assert saved[0]["phone"] == "+919876543210"
    assert saved[0]["monthly_bill"] == 2500
    assert saved[0]["source"] == "home"


@pytest.mark.parametrize("field,value,message", [
    ("name", "", "Please tell us your name."),
    ("phone", "12345", "valid 10-digit Indian mobile number"),
    ("email", "not-an-email", "valid email address"),
    ("property_type", "castle", "Please choose a property type."),
    ("location", "", "Please tell us where the property is."),
    ("monthly_bill", "-5", "realistic monthly bill"),
])
def test_invalid_enquiry_shows_errors(client, app, field, value, message):
    data = dict(VALID, **{field: value})
    res = client.post("/contact", data=data)
    assert res.status_code == 422
    assert message in res.get_data(as_text=True)
    assert rows(app) == []


def test_optional_fields_can_be_blank(client, app):
    data = dict(VALID, email="", monthly_bill="", message="")
    assert client.post("/contact", data=data).status_code == 302
    saved = rows(app)[0]
    assert saved["email"] is None and saved["monthly_bill"] is None and saved["message"] is None


def test_user_content_is_escaped_on_error_page(client):
    data = dict(VALID, name="<script>alert(1)</script>", phone="bad")
    html = client.post("/contact", data=data).get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_duplicate_submission_is_not_stored_twice(client, app):
    client.post("/contact", data=VALID)
    res = client.post("/contact", data=VALID)
    assert res.status_code == 302
    assert len(rows(app)) == 1


def test_honeypot_submission_is_ignored(client, app):
    res = client.post("/contact", data=dict(VALID, website="http://spam.example"))
    assert res.status_code == 302
    assert rows(app) == []


def test_unknown_source_is_normalised(client, app):
    client.post("/contact", data=dict(VALID, source="evil"))
    assert rows(app)[0]["source"] == "contact"


def test_storage_failure_shows_honest_error(client, app, monkeypatch):
    import db

    def broken(_data):
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr(db, "save_enquiry", broken)
    res = client.post("/contact", data=VALID)
    html = res.get_data(as_text=True)
    assert res.status_code == 503
    assert "could not save your enquiry" in html
    assert "tel:+919356806280" in html


def test_thank_you_greets_by_first_name(client):
    client.post("/contact", data=VALID)
    assert "Thank you, Asha!" in client.get("/contact/thank-you").get_data(as_text=True)


def test_csrf_is_enforced_when_enabled(tmp_path):
    class Cfg(TestConfig):
        WTF_CSRF_ENABLED = True
        DATABASE = str(tmp_path / "csrf.sqlite3")

    client = create_app(Cfg).test_client()
    client.set_cookie("lang", "en")
    res = client.post("/contact", data=VALID)
    assert res.status_code == 400
    assert "session expired" in res.get_data(as_text=True)


# --------------------------------------------------------------------------
# Email notifications
# --------------------------------------------------------------------------
class FakeSMTP:
    sent = []
    fail = False

    def __init__(self, *args, **kwargs):
        if FakeSMTP.fail:
            raise OSError("connection refused")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self, **kwargs):
        pass

    def login(self, user, password):
        pass

    def send_message(self, msg):
        FakeSMTP.sent.append(msg)


@pytest.fixture
def mail_app(tmp_path, monkeypatch):
    import notifications

    FakeSMTP.sent, FakeSMTP.fail = [], False
    monkeypatch.setattr(notifications.smtplib, "SMTP", FakeSMTP)

    class Cfg(TestConfig):
        DATABASE = str(tmp_path / "mail.sqlite3")
        MAIL_SERVER = "smtp.example.com"
        MAIL_USERNAME = "site@example.com"
        MAIL_PASSWORD = "secret"
        MAIL_TO = "owner@example.com"

    return create_app(Cfg)


def test_email_sent_when_configured(mail_app):
    res = mail_app.test_client().post("/contact", data=VALID)
    assert res.status_code == 302
    assert len(FakeSMTP.sent) == 1
    msg = FakeSMTP.sent[0]
    assert msg["To"] == "owner@example.com" and "Asha Patil" in msg["Subject"]
    assert msg["Reply-To"] == "asha@example.com"


def test_email_not_resent_for_duplicate(mail_app):
    client = mail_app.test_client()
    client.post("/contact", data=VALID)
    client.post("/contact", data=VALID)
    assert len(FakeSMTP.sent) == 1


def test_db_and_email_failure_reports_error(mail_app, monkeypatch):
    import db

    def broken(_data):
        raise sqlite3.OperationalError("locked")

    monkeypatch.setattr(db, "save_enquiry", broken)
    FakeSMTP.fail = True
    res = mail_app.test_client().post("/contact", data=VALID)
    assert res.status_code == 503


def test_email_alone_is_enough_when_db_fails(mail_app, monkeypatch):
    import db

    def broken(_data):
        raise sqlite3.OperationalError("locked")

    monkeypatch.setattr(db, "save_enquiry", broken)
    res = mail_app.test_client().post("/contact", data=VALID)
    assert res.status_code == 302 and len(FakeSMTP.sent) == 1


# --------------------------------------------------------------------------
# Pricing
# --------------------------------------------------------------------------
def test_solutions_page_shows_prices_and_components(client):
    html = client.get("/solutions").get_data(as_text=True)
    assert 'id="pricing"' in html
    text = re.sub(r"<[^>]+>", "", html)  # prices are wrapped in count-up spans
    for price in ("₹1,02,000", "₹1,12,000", "₹2,30,000", "₹2,50,000", "₹50,000", "₹55,000"):
        assert price in text, price
    assert 'data-count="102000"' in html
    assert "+ ₹78,000 subsidy" in html and "All prices include GST and installation." in html
    assert "pay ₹1,80,000 at installation" in html
    assert "Subsidy available until 31 March 2027" in html
    for amount in ("₹30,000 per kW", "₹60,000", "₹18,000 per kW"):
        assert amount in html, amount
    assert "additional 10% subsidy per kW" in html and "National Portal for Rooftop Solar" in html
    for brand in ("Waaree / Adani", "Polycab string inverter", "Apollo GI pipe structure", "Type II surge protection"):
        assert brand in html, brand


def test_home_pricing_preview_shows_starting_prices(client):
    html = client.get("/").get_data(as_text=True)
    assert "Know the price before you begin." in html
    assert "₹1,02,000" in html and "₹2,30,000" in html and "₹50,000" in html
    assert "/solutions#pricing" in html


def test_subsidy_deadline_notice_hides_after_end_date(client, monkeypatch):
    from datetime import date
    import content

    monkeypatch.setitem(content.SUBSIDY, "end_date", date(2000, 1, 1))
    html = client.get("/solutions").get_data(as_text=True)
    assert "Subsidy available until" not in html
    assert "is still accepting applications" in html



def test_diwali_offer_shows_until_end_date(client, monkeypatch):
    from datetime import date
    import content

    monkeypatch.setitem(content.OFFER, "end_date", date(2999, 1, 1))
    html = client.get("/").get_data(as_text=True)
    assert 'id="diwali-offer"' in html and "Diwali Dhamaka Offer" in html and "15,000" in html
    assert "offer-strip" in html and "data-offer-popup" in html
    # the announcement strip shows on every page; the popup stays off the enquiry page
    contact = client.get("/contact").get_data(as_text=True)
    assert "offer-strip" in contact and "data-offer-popup" not in contact

    monkeypatch.setitem(content.OFFER, "end_date", date(2000, 1, 1))
    html = client.get("/").get_data(as_text=True)
    assert "diwali-offer" not in html and "Diwali Dhamaka Offer" not in html
    assert "offer-strip" not in html and "data-offer-popup" not in html

# --------------------------------------------------------------------------
# English / Marathi
# --------------------------------------------------------------------------
MARATHI_PAGES = ["/", "/about", "/solutions", "/contact", "/privacy", "/contact/thank-you", "/missing-page"]


@pytest.fixture
def mr_client(client):
    client.set_cookie("lang", "mr")
    return client


def test_language_switch_sets_cookie_and_returns_to_page(client):
    res = client.get("/lang/mr?next=/solutions?type=commercial")
    assert res.status_code == 302 and res.headers["Location"] == "/solutions?type=commercial"
    assert "lang=mr" in res.headers["Set-Cookie"]
    html = client.get("/solutions").get_data(as_text=True)
    assert '<html lang="mr">' in html and "सोलर सोल्युशन्स" in html

    client.get("/lang/en?next=/solutions")
    html = client.get("/solutions").get_data(as_text=True)
    assert '<html lang="en-IN">' in html and "On-grid, off-grid or hybrid?" in html


@pytest.mark.parametrize("target", ["https://evil.example", "//evil.example", "/\\evil.example", "javascript:alert(1)", ""])
def test_language_switch_never_redirects_off_site(client, target):
    res = client.get("/lang/mr", query_string={"next": target})
    assert res.headers["Location"] == "/"


def test_marathi_is_the_default_for_new_visitors(app):
    html = app.test_client().get("/").get_data(as_text=True)
    assert '<html lang="mr">' in html and "सूर्यप्रकाशाला" in html


def test_unknown_language_is_ignored(client):
    res = client.get("/lang/xx?next=/about")
    assert res.headers["Location"] == "/about" and "Set-Cookie" not in res.headers
    client.set_cookie("lang", "xx")
    assert '<html lang="mr">' in client.get("/").get_data(as_text=True)


def test_navbar_offers_both_languages(client):
    html = client.get("/about").get_data(as_text=True)
    assert 'href="/lang/en?next=/about"' in html and 'href="/lang/mr?next=/about"' in html
    assert "ENG" in html and "मराठी" in html


@pytest.mark.parametrize("path", MARATHI_PAGES)
def test_marathi_pages_have_no_missing_translations(mr_client, path):
    import i18n

    i18n.MISSING.clear()
    res = mr_client.get(path)
    assert res.status_code in (200, 404)
    html = res.get_data(as_text=True)
    assert '<html lang="mr">' in html and "मुख्यपृष्ठ" in html
    assert not i18n.MISSING, sorted(i18n.MISSING)


def test_marathi_content_and_estimator_text(mr_client):
    html = mr_client.get("/").get_data(as_text=True)
    assert "सूर्यप्रकाशाला" in html and "नेहमीचे प्रश्न" in html
    assert "रूफटॉप सोलर प्रणाली कशी काम करते?" in html
    assert "निवासी वीजबिलाचा साधारण 40–80%" in html
    assert "Turn Sunlight" not in html and "Questions, answered." not in html
    html = mr_client.get("/solutions").get_data(as_text=True)
    assert "अनुदान 31 मार्च 2027 पर्यंत उपलब्ध" in html and "+ ₹78,000 अनुदान" in html


def test_marathi_form_errors_and_choices(mr_client, app):
    html = mr_client.post("/contact", data={**VALID, "phone": "12345", "name": ""}).get_data(as_text=True)
    assert "कृपया तुमचे नाव सांगा." in html
    assert "कृपया योग्य 10 अंकी भारतीय मोबाइल नंबर टाका" in html
    assert "कृपया ठळक केलेली माहिती तपासा" in html
    assert "निवासी (घर)" in html
    assert rows(app) == []


def test_every_template_string_has_a_marathi_translation():
    from pathlib import Path

    from translations_mr import MR

    root = Path(__file__).resolve().parent.parent
    call = re.compile(r"""\b_\(\s*(?:"([^"]*)"|'([^']*)')""")
    keys = set()
    for path in (root / "templates").rglob("*.html"):
        for m in call.finditer(path.read_text(encoding="utf-8")):
            keys.add(m.group(1) if m.group(1) is not None else m.group(2))
    keys.update(re.findall(r'alert = "([^"]+)"', (root / "app.py").read_text(encoding="utf-8")))
    missing = sorted(k for k in keys if k not in MR)
    assert not missing, missing


def test_marathi_translations_keep_placeholders():
    from translations_mr import MR

    field = re.compile(r"\{(\w*)\}")
    wrong = [en for en, mr in MR.items() if sorted(field.findall(en)) != sorted(field.findall(mr))]
    assert not wrong, wrong
