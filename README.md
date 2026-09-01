# 🔔 Notifi

> Connect with every parent, instantly.

Notifi is a white-label bulk SMS platform built for schools in East Africa. School administrators can send instant SMS to parents and staff, manage contact groups, track delivery reports, and purchase SMS credits — all from a clean, mobile-friendly dashboard.

## Features

- 📨 **Bulk SMS** — Send to individual groups or all contacts at once
- 👥 **Contact Management** — Add manually or import via CSV/Excel
- 📊 **Delivery Reports** — Track which messages were delivered
- 📝 **Message Templates** — Pre-built Swahili templates for common school communications
- 💳 **Credit System** — Admin tops up school credits, schools spend as they send
- 📱 **Mobile First** — Fully responsive, works perfectly on any phone
- 🔐 **Multi-tenant** — Each school only sees their own data
- 🌍 **East Africa Ready** — Built for Tanzania, Kenya, Uganda, Rwanda

## Tech Stack

- **Backend:** Python 3.10+ / Django 4.2
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Database:** PostgreSQL
- **SMS Provider:** Beem Africa API
- **Server:** Gunicorn + Nginx

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- PostgreSQL
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/Ian-BM/notifi.git
cd notifi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your values

# Setup database
createdb notifi_db  # or use psql
python manage.py migrate

# Seed demo data
python manage.py seed_notifi

# Run development server
python manage.py runserver
```

Open http://127.0.0.1:8000

### Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Platform Admin | admin | notifi2026 |
| School Demo | stagnes | demo2026 |

⚠️ Change these immediately in production.

## Deployment

See `deploy/README.md` for full production deployment guide on Ubuntu VPS.

Quick overview:
```bash
# On server — first time only
bash deploy/setup_server.sh

# Upload code
bash deploy/upload_to_server.sh

# Install app
bash deploy/install_app.sh

# SSL
bash deploy/ssl_setup.sh
```

## Environment Variables

See `.env.example` for all required variables.

Key variables:
- `SECRET_KEY` — Django secret key
- `BEEM_API_KEY` — Beem Africa API key
- `BEEM_SECRET_KEY` — Beem Africa secret key
- `DB_PASSWORD` — PostgreSQL password

## SMS Integration

Notifi uses the [Beem Africa API](https://beem.africa) for SMS delivery across 150+ networks in Africa.

Supported networks (Tanzania):
- Vodacom Tanzania
- Airtel Tanzania
- Tigo/Yas Tanzania
- Halotel Tanzania
- TTCL

## Project Structure

```
notifi/
├── core/                 # Django project settings
├── apps/
│   ├── accounts/         # Authentication, user management
│   ├── schools/          # School profiles, sender IDs
│   ├── contacts/         # Parent/staff contacts & groups
│   ├── messaging/        # SMS sending, templates, reports
│   └── dashboard/        # Dashboard views
├── templates/            # HTML templates
├── static/               # CSS, JavaScript
├── deploy/               # Server deployment scripts
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
└── manage.py
```

## License

Private — All rights reserved © 2026 Notifi

---

Built with ❤️ for schools in East Africa.
