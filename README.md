# CivicPulse — Cloud-Based Smart City Issue Reporting System (Django)

Academic prototype for the Cloud Computing ABA. CivicPulse is **not an official government service**. It supports SDG 11 (Sustainable Cities and Communities) and SDG 9 (Industry, Innovation and Infrastructure).

**Stack:** Django 5.2 LTS · Django ORM (SQLite default, PostgreSQL/RDS optional) · Bootstrap 5 · Leaflet + OpenStreetMap · Chart.js · Gunicorn + WhiteNoise (+ Nginx on AWS)

## Features
- Citizen registration/login (email + hashed password), separate administrator login.
- Submit complaints with unique IDs (`CP-2026-XXXXXX`), optional photo (content-checked, max 5 MB) and map coordinates.
- Citizens see only their own complaints; administrators manage all of them (status, priority, notes, history timeline, delete test records).
- Search/filters, Leaflet map, database-backed Chart.js analytics.
- Private photos (served only to the owner/administrators), CSRF protection, custom 403/404/500 pages, Django admin at `/django-admin/`.
- 27 automated tests.

## Run locally

**Windows (PowerShell)**
```powershell
cd civicpulse_django
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py create_admin
python manage.py runserver
```
**macOS / Linux**
```bash
cd civicpulse_django
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py create_admin
python manage.py runserver
```
Open http://127.0.0.1:8000 (Python 3.10+ required). `.env.example` already has `DEBUG=1` for local use.

## First use
1. Register a citizen account → **Report issue** → note the complaint ID.
2. Log out, open **Administrator login** (`/admin/login/`) with the account from `create_admin`.
3. Open **Manage complaints**, update status/priority, then **Analytics**.
Optional: `python manage.py seed_demo` adds one clearly labelled sample record.

## Tests
```bash
python manage.py test
```
Record your own results in `docs/test_plan.md` (left as *Not run* until you execute it).

## Deploy on AWS EC2
```bash
bash deploy/setup_ec2.sh        # installs Nginx + Gunicorn + systemd service, creates .env, migrates
bash deploy/check_server.sh     # diagnoses "site can't be reached / timed out"
```
Full guide, including the **ERR_CONNECTION_TIMED_OUT checklist**: [`docs/AWS_DEPLOYMENT.md`](docs/AWS_DEPLOYMENT.md).

## Configuration (`.env`)
| Variable | Meaning |
|---|---|
| `SECRET_KEY` | Required when `DEBUG=0`. Signs sessions/CSRF tokens. |
| `DEBUG` | `1` locally, **`0` on AWS**. |
| `ALLOWED_HOSTS` | Comma-separated IPs/domains the site may be opened with (add your EC2 IP). |
| `CSRF_TRUSTED_ORIGINS` | e.g. `http://54.x.x.x` if you see "CSRF verification failed". |
| `USE_HTTPS` | Keep `0` until a TLS certificate is installed. |
| `DATABASE_URL` | Default SQLite. RDS: `postgres://user:pw@host:5432/db` (+ `pip install -r requirements-postgres.txt`). |
| `MAX_CONTENT_LENGTH`, `UPLOAD_FOLDER`, `TIME_ZONE` | Upload limit (bytes), upload path, display time zone. |

## Project layout
```text
civicpulse_django/
├── manage.py, requirements.txt, requirements-postgres.txt, .env.example
├── config/                  # settings.py, urls.py, wsgi.py
├── complaints/              # the app: models, views, forms, urls, admin, migrations
│   ├── management/commands/ # create_admin, seed_demo
│   └── tests/test_app.py
├── templates/               # Django templates (base, citizen/, admin_panel/, auth/, partials/)
├── static/                  # css/, js/
├── deploy/                  # setup_ec2.sh, check_server.sh
├── docs/                    # report, viva, DB design, test plan, AWS guide
├── instance/                # SQLite database (generated)
└── uploads/                 # private complaint photos (generated)
```

## Cloud computing statement
Running locally is not itself a cloud deployment. `docs/AWS_DEPLOYMENT.md` and `docs/cloud_deployment.md` describe the AWS architecture and the steps to host it; S3 photo storage, CloudFront, Route 53 and CloudWatch are proposals only. Provisioning AWS resources may cost money.

## Limitations
Classroom prototype: no email verification, password reset or rate limiting; photos are stored on local disk; not security-certified. Bootstrap, Leaflet, Chart.js and map tiles need internet access (CDN).
"# -CivicPulse1" 
