# SPARKS SOLAR ENERGY website

The website for **SPARKS SOLAR ENERGY**, Deolali Pravara, Tal. Rahuri, Dist. Ahilya Nagar, Maharashtra.
It is built with Python Flask, Jinja2 templates, Tailwind CSS (compiled, no CDN) and plain JavaScript.

Pages: Home, About Us, Solutions, Contact, Thank-you, Privacy, plus a custom 404 page, `robots.txt` and `sitemap.xml`.

---

## 1. Project structure

```text
sparks-solar-energy/
├── app.py                  # Flask app: routes, error pages, security headers, sitemap/robots
├── config.py               # Settings, business details, estimator assumptions
├── content.py              # Editable page content: solutions, FAQs, steps, team, gallery
├── forms.py                # Enquiry form + server-side validation and clean-up
├── db.py                   # SQLite storage + CLI commands (init-db, list/export enquiries)
├── notifications.py        # Optional SMTP email for new enquiries
├── wsgi.py                 # Production entry point (refuses to start without SECRET_KEY)
├── requirements.txt        # Pinned Python dependencies
├── package.json            # Tailwind CSS + Lucide icons (build tools only)
├── tailwind.config.js      # Design tokens: colours, fonts, shadows
├── .env.example            # Copy to .env and fill in
├── instance/               # Holds enquiries.sqlite3 at runtime (git-ignored)
├── scripts/build-icons.js  # Builds the icon sprite from Lucide
├── templates/
│   ├── base.html           # <head>, SEO/Open Graph, JSON-LD, WhatsApp button
│   ├── index.html  about.html  solutions.html  contact.html
│   ├── thank_you.html  privacy.html  404.html  500.html  sitemap.xml
│   └── components/         # navbar, footer, enquiry form/section, page hero, macros
├── static/
│   ├── src/input.css       # Tailwind source + custom animation CSS
│   ├── css/output.css      # Compiled, minified CSS (commit this)
│   ├── js/                 # main.js, animations.js, calculator.js
│   ├── images/brand/       # Logo variants + Open Graph image
│   ├── images/stock/       # Demonstration photos (see CREDITS.md)
│   ├── images/icons/       # sprite.svg (Lucide icons)
│   └── favicon/
├── images/                 # Original logo and flyers supplied by the business (untouched)
└── tests/test_app.py       # 43 tests: pages, validation, submissions, CSRF, email
```

## 2. Run it on Windows (VS Code + PowerShell)

Open the folder in VS Code, then open a terminal (**Terminal → New Terminal**, PowerShell):

```powershell
# 1. Create and activate a virtual environment (skip creation if .venv already exists)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
#    If PowerShell blocks the script, run this once, then activate again:
#    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# 2. Install Python packages
pip install -r requirements.txt

# 3. Create your settings file
Copy-Item .env.example .env
#    Then open .env and set SECRET_KEY. Generate one with:
python -c "import secrets; print(secrets.token_hex(32))"

# 4. Start the site
flask --app app run --debug
```

Open <http://127.0.0.1:5000>. Press `Ctrl+C` to stop.

Run the tests:

```powershell
python -m pytest -q
```

## 3. Compiling Tailwind CSS

The compiled `static/css/output.css` is already included, so **you only need Node.js if you change styles or templates**.

```powershell
npm install            # once
npm run build:css      # one-off minified build for production
npm run watch:css      # rebuilds automatically while you edit templates
```

Tailwind scans `templates/**/*.html` and `static/js/**/*.js` for class names, so rebuild after adding new classes.
Custom animations and components live in `static/src/input.css`; colours and fonts are in `tailwind.config.js`.

To add a new icon, add its [Lucide](https://lucide.dev/icons) name to the list in `scripts/build-icons.js`, run `npm run build:icons`, and use it in a template with `{{ icon("name", "h-5 w-5") }}`.

No Node.js? Use the [Tailwind standalone CLI](https://github.com/tailwindlabs/tailwindcss/releases/tag/v3.4.17) (`tailwindcss-windows-x64.exe`) with the same arguments as `build:css`.

## 4. Contact form, email and WhatsApp

**How enquiries work.** Forms on the Home, Solutions and Contact pages post to `/contact`. The server validates and cleans every field, checks the CSRF token, ignores honeypot spam and stores the enquiry in SQLite (`instance/enquiries.sqlite3`). It then redirects to a thank-you page, so refreshing cannot resubmit. An identical enquiry sent again within 10 minutes is not stored twice (`DUPLICATE_WINDOW_MINUTES`).
If saving fails and no email could be sent, the visitor sees an honest error with phone and WhatsApp alternatives.

**Reading enquiries** (on the server; there is deliberately no public admin page):

```powershell
flask --app app list-enquiries --limit 20
flask --app app export-enquiries enquiries.csv   # keep this file private
```

**Database schema** (`enquiries` table): `id`, `created_at` (UTC ISO), `name`, `phone` (normalised `+91XXXXXXXXXX`), `email`, `property_type`, `location`, `monthly_bill`, `message`, `source`, `fingerprint` (duplicate check). Details are in `db.py`.

**Email notifications (optional).** Fill the `MAIL_*` values in `.env`. With Gmail, turn on 2-step verification and create an **App password**:

```ini
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=yourname@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_TO=where-enquiries-should-go@example.com
```

An enquiry counts as emailed only when the SMTP server accepts it. Failures are logged, and the enquiry is still saved in the database.

**WhatsApp.** The number and pre-filled message are in `config.py` → `BUSINESS["whatsapp_number"]` (digits only, with country code: `919356806280`) and `BUSINESS["whatsapp_message"]`. Every WhatsApp link uses `https://wa.me/919356806280?text=…`. The call buttons use `tel:+919356806280` (`phone_tel`).

## 5. Editing content

| What | Where |
| --- | --- |
| Phone, address, Instagram, tagline | `config.py` → `BUSINESS` (or `.env` for email/street/PIN) |
| Estimator assumptions (illustrative offset ranges) | `config.py` → `CALCULATOR` |
| Solutions, benefits, steps, FAQs, services, team | `content.py` |
| Package prices, subsidy steps, component brands | `content.py` → `PRICING`, `SUBSIDY_STEPS`, `COMPONENTS` (also update the cost FAQ) |
| "To confirm" placeholder boxes | `SHOW_PLACEHOLDERS=false` in `.env` hides them |

**Replacing demonstration photos.** Put real project photos (WebP or JPG, about 1200px wide) in `static/images/projects/`. In `content.py` → `GALLERY`, point `src` at them, write accurate `alt` text and set `"demo": False`. When no item is marked demo, the section title changes to "Our Installations" and the demonstration notice disappears. Other stock images are listed in `static/images/stock/CREDITS.md`.

## 6. Deployment

Before going live:

1. Set a strong `SECRET_KEY`, `SITE_URL=https://your-domain`, `SESSION_COOKIE_SECURE=true`, `SHOW_PLACEHOLDERS=false`, and remove `FLASK_DEBUG`.
2. Run `npm run build:css` if you changed any templates or styles.
3. Serve over HTTPS. Make sure the `instance/` folder is writable and persistent (it holds the enquiry database).

**Option A: Linux VPS (recommended).** Use Ubuntu with Nginx and gunicorn:

```bash
git clone <your-repo> sparks-solar-energy && cd sparks-solar-energy
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env          # fill in production values
gunicorn -w 2 -b 127.0.0.1:8000 wsgi:app   # run under systemd in practice
```

Point Nginx at `127.0.0.1:8000`, optionally serve `/static/` directly, and add a free certificate with Certbot.

**Option B: PythonAnywhere.** Upload the project and create a virtualenv with `pip install -r requirements.txt`. Then add a Flask web app whose WSGI file imports `from wsgi import app as application`, set environment variables in `.env`, and map `/static/` to the `static` folder.

**Option C: Render / Railway.** Use a web service with the build command `pip install -r requirements.txt` and the start command `gunicorn wsgi:app`. Set env vars in the dashboard and **attach a persistent disk** for `instance/`, with `DATABASE_PATH` pointing to it. Without a disk, enquiries are lost on redeploy, so configure email as well.

**Option D: Windows server.** Run:

```powershell
waitress-serve --listen=0.0.0.0:8000 wsgi:app
```

After deploying, submit `https://your-domain/sitemap.xml` in Google Search Console and create or verify the Google Business Profile.

## 7. Accuracy rules for this site

- Do not add statistics, savings percentages, testimonials, certifications, awards, project counts or partnerships unless they are verified.
- Estimator output is labelled illustrative. Keep it that way.
- Subsidy information points to official portals. Re-check scheme names and status periodically.
