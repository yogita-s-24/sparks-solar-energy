"""SPARKS SOLAR ENERGY — Flask application."""
import logging
import os
import sqlite3
from datetime import datetime
from urllib.parse import quote, urlsplit

from flask import Flask, Response, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CSRFError, CSRFProtect

import content
import db
import i18n
from config import Config
from forms import PROPERTY_LABELS, EnquiryForm
from i18n import gettext as _
from notifications import mail_configured, send_enquiry_email

csrf = CSRFProtect()

# Public pages listed in sitemap.xml: (endpoint, change frequency, priority)
SITEMAP_PAGES = [
    ("index", "monthly", "1.0"),
    ("solutions", "monthly", "0.9"),
    ("about", "yearly", "0.7"),
    ("contact", "yearly", "0.8"),
    ("privacy", "yearly", "0.3"),
]

CSP = (
    "default-src 'self'; "
    "img-src 'self' data:; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
)

ENQUIRY_SOURCES = {"home", "contact", "solutions"}


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    os.makedirs(app.instance_path, exist_ok=True)
    if not app.config.get("DATABASE"):
        app.config["DATABASE"] = os.path.join(app.instance_path, "enquiries.sqlite3")

    if not app.testing and app.config["SECRET_KEY"] == "dev-only-change-me":
        app.logger.warning("SECRET_KEY is not set. Set it in .env before deploying.")

    csrf.init_app(app)
    db.init_app(app)
    register_template_helpers(app)
    register_routes(app)
    register_error_handlers(app)

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Content-Security-Policy", CSP)
        # Pages are rendered in the language stored in the "lang" cookie.
        response.vary.add("Cookie")
        return response

    return app


def register_template_helpers(app):
    business = app.config["BUSINESS"]

    @app.url_defaults
    def static_cache_buster(endpoint, values):
        """Add ?v=<modified time> to static URLs so browsers fetch updated files."""
        if endpoint == "static" and "filename" in values and "v" not in values:
            path = os.path.join(app.static_folder, values["filename"])
            try:
                values["v"] = int(os.path.getmtime(path))
            except OSError:
                pass

    app.jinja_env.globals["_"] = _
    app.jinja_env.filters["date_long"] = i18n.format_date
    app.jinja_env.filters["date_short"] = lambda value: i18n.format_date(value, short=True)

    @app.context_processor
    def inject_globals():
        whatsapp_url = f"https://wa.me/{business['whatsapp_number']}?text={quote(_(business['whatsapp_message']))}"
        addr = business["address"]
        address_parts = [addr["street"], _(addr["locality"]), _(addr["taluka"]), _(addr["district"]),
                         f"{_(addr['region'])} {addr['postal_code']}".strip(), _(addr["country"])]
        return {
            "lang": i18n.get_lang(),
            "languages": i18n.LANGUAGES,
            "business": business,
            "whatsapp_url": whatsapp_url,
            "full_address": ", ".join(p for p in address_parts if p),
            "current_year": datetime.now().year,
            "site_url": app.config["SITE_URL"],
            "solutions_nav": content.SOLUTIONS,
            "subsidy": content.SUBSIDY,
            # Deadline notices disappear automatically once the scheme's end date passes.
            "subsidy_open": datetime.now().date() <= content.SUBSIDY["end_date"],
        }

    app.jinja_env.filters["inr"] = inr


def inr(value):
    """Format a number with Indian digit grouping, e.g. 1,23,456."""
    s = str(int(value))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups) + "," + tail


def calculator_settings(calc):
    """Estimator assumptions plus its messages in the current language, for calculator.js."""
    def pct(n):
        return round(n * 100)

    assumption = ("Assumption used: a suitably sized system might offset roughly {low}–{high}% of a typical "
                  "{type} bill. This is an illustrative assumption, not a promise.")
    return {
        **calc,
        "text": {
            "assumptions": {
                key: _(assumption, low=pct(pt["offset_low"]), high=pct(pt["offset_high"]), type=_(pt["label"]).lower())
                for key, pt in calc["property_types"].items()
            },
            "invalid_bill": _("Please enter a monthly bill between ₹{min} and ₹{max}.",
                              min=inr(calc["min_bill"]), max=inr(calc["max_bill"])),
            # {rate} and {units} are filled in by calculator.js
            "rate": _("From your figures, you currently pay about ₹{rate} per unit and use roughly {units} units a year. "
                      "Useful information for planning a system size."),
        },
    }


def enquiry_form_for(source):
    form = EnquiryForm()
    form.source.data = source
    preset = request.args.get("type")
    if preset in PROPERTY_LABELS and not form.property_type.data:
        form.property_type.data = preset
    return form


def register_routes(app):
    @app.route("/")
    def index():
        return render_template(
            "index.html",
            form=enquiry_form_for("home"),
            value_points=content.VALUE_POINTS,
            solutions=content.SOLUTIONS,
            benefits=content.BENEFITS,
            steps=content.STEPS,
            faqs=content.FAQS,
            gallery=content.GALLERY,
            gallery_filters=content.GALLERY_FILTERS,
            gallery_is_demo=any(item["demo"] for item in content.GALLERY),
            pricing=content.PRICING,
            calculator=app.config["CALCULATOR"],
            calculator_js=calculator_settings(app.config["CALCULATOR"]),
        )

    @app.route("/about")
    def about():
        return render_template(
            "about.html",
            commitments=content.COMMITMENTS,
            team=content.TEAM,
            value_points=content.VALUE_POINTS,
        )

    @app.route("/solutions")
    def solutions():
        return render_template(
            "solutions.html",
            form=enquiry_form_for("solutions"),
            solutions=content.SOLUTIONS,
            system_types=content.SYSTEM_TYPES,
            services=content.SERVICES,
            steps=content.STEPS,
            pricing=content.PRICING,
            subsidy_steps=content.SUBSIDY_STEPS,
            components=content.COMPONENTS,
        )

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        form = enquiry_form_for("contact") if request.method == "GET" else EnquiryForm()
        status, alert = 200, None
        if request.method == "POST":
            if form.validate_on_submit():
                if form.website.data:  # honeypot filled: quietly ignore bots
                    return redirect(url_for("thank_you", _anchor="main"))
                result = handle_enquiry(app, form)
                if result:
                    session["enquiry_name"] = form.name.data.split(" ")[0]
                    # Explicit anchor so the form's "#enquiry" is not carried over.
                    return redirect(url_for("thank_you", _anchor="main"))
                status = 503
                alert = "We could not save your enquiry right now. Please call or WhatsApp us instead. We would be glad to help."
            else:
                status = 422
                alert = "Please check the highlighted fields and try again."
        return render_template("contact.html", form=form, alert=alert), status

    @app.route("/contact/thank-you")
    def thank_you():
        name = session.pop("enquiry_name", None)
        return render_template("thank_you.html", name=name)

    @app.route("/privacy")
    def privacy():
        return render_template("privacy.html")

    @app.route("/lang/<code>")
    def set_language(code):
        """Remember the chosen language and return to the page the visitor was on."""
        target = request.args.get("next", "")
        parts = urlsplit(target)
        # Only same-site paths, never an external redirect.
        if parts.scheme or parts.netloc or not target.startswith("/") or target.startswith("//") or "\\" in target:
            target = url_for("index")
        response = redirect(target)
        if code in i18n.LANGUAGES:
            response.set_cookie(i18n.COOKIE_NAME, code, max_age=i18n.COOKIE_MAX_AGE, samesite="Lax",
                                secure=app.config["SESSION_COOKIE_SECURE"])
        return response

    @app.route("/robots.txt")
    def robots():
        body = f"User-agent: *\nAllow: /\nDisallow: /contact/thank-you\n\nSitemap: {app.config['SITE_URL']}{url_for('sitemap')}\n"
        return Response(body, mimetype="text/plain")

    @app.route("/sitemap.xml")
    def sitemap():
        xml = render_template("sitemap.xml", pages=SITEMAP_PAGES, lastmod=datetime.now().date().isoformat())
        return Response(xml, mimetype="application/xml")

    @app.route("/site.webmanifest")
    def manifest():
        b = app.config["BUSINESS"]
        return {
            "name": b["name"],
            "short_name": b["short_name"],
            "icons": [
                {"src": url_for("static", filename="favicon/icon-192.png"), "sizes": "192x192", "type": "image/png"},
                {"src": url_for("static", filename="favicon/icon-512.png"), "sizes": "512x512", "type": "image/png"},
            ],
            "theme_color": "#103D2B",
            "background_color": "#F7F8F2",
            "display": "browser",
        }


def handle_enquiry(app, form):
    """Save and/or email an enquiry. Returns True if at least one succeeded."""
    data = {
        "name": form.name.data,
        "phone": form.phone.data,
        "email": form.email.data or None,
        "property_type": form.property_type.data,
        "location": form.location.data,
        "monthly_bill": form.monthly_bill.data,
        "message": form.message.data or None,
        "source": form.source.data if form.source.data in ENQUIRY_SOURCES else "contact",
    }
    saved = duplicate = False
    try:
        _, duplicate = db.save_enquiry(data)
        saved = True
    except sqlite3.Error as exc:
        app.logger.error("Could not save enquiry: %s", exc)

    emailed = False
    if not duplicate and mail_configured(app.config):
        emailed = send_enquiry_email(app.config, data, app.logger)
    return saved or emailed


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("500.html"), 500

    @app.errorhandler(CSRFError)
    def csrf_error(_e):
        # Keep what the visitor typed so they only need to press submit again.
        form = EnquiryForm(meta={"csrf": True})
        alert = "Your session expired before the form was sent. Please check your details and submit again."
        return render_template("contact.html", form=form, alert=alert), 400


app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Local development only; production uses wsgi.py.
    app.run(debug=os.environ.get("FLASK_DEBUG", "1") == "1")
