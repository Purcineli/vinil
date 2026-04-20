# Vinil

A full-stack event ticketing platform built with Django. Organizers create events and ticket types; buyers place orders and receive individual tickets with QR codes; staff validate tickets at the door via camera.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.0.3-green?logo=django)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Features

- **Email-based authentication** — login with email instead of username
- **Event management** — organizers create and manage events with start/end dates and location
- **Ticket types** — multiple categories per event (e.g. General, VIP) with quantity control
- **Order flow** — buyers select ticket types and quantities; race conditions prevented with `select_for_update()`
- **MercadoPago payments** — supports both Checkout Pro and Transparent Checkout
- **QR code tickets** — each confirmed ticket gets a unique `VNL-XXXXX` code and server-generated QR code
- **Door validation** — real-time camera QR code scanning via `jsQR` with instant server validation
- **Audit history** — all model changes tracked with `django-simple-history`
- **Responsive UI** — TailwindCSS (via CDN), no build step required

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12+ / Django 6.0.3 |
| Frontend | Django Templates + TailwindCSS CDN |
| Database | SQLite (dev) / PostgreSQL (production) |
| Payments | MercadoPago SDK |
| QR Code generation | `qrcode[pil]` (server-side, base64) |
| QR Code reading | `jsQR` (JavaScript, browser camera) |
| History tracking | `django-simple-history` |

---

## Architecture

Five Django apps with clear responsibilities:

```
vinil/
├── core/        # Project settings, root URLs
├── accounts/    # Email-based auth, user registration, profile
├── events/      # Event CRUD, organizer management
├── tickets/     # TicketType (categories) + Ticket (individual issued tickets)
├── orders/      # Order + OrderItem, quantity management
├── payments/    # Payment model, MercadoPago integration, ticket emission signal
└── templates/   # HTML templates (base, dashboard, per-app)
```

### Data model

```
USER ─── organizes ──── EVENT
  │                       │
  └── places ── ORDER     └── has many ── TICKET_TYPE
                  │                            │
                  ├── ORDER_ITEM ─ references ─┘
                  │       └── emits N ── TICKET (VNL-XXXXX, QR code)
                  └── paid via ── PAYMENT
```

Tickets are emitted automatically via a `post_save` signal when a `Payment` is confirmed.

---

## Getting Started

### Prerequisites

- Python 3.12+
- pip
- A MercadoPago account (for payment features — test credentials work fine)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-username/vinil.git
cd vinil

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your values (see Environment Variables section)

# 5. Apply migrations
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key — generate one with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `True` for development, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts (e.g. `localhost,127.0.0.1`) |
| `MERCADOPAGO_ACCESS_TOKEN` | MercadoPago Access Token (use `TEST-...` for sandbox) |
| `MERCADOPAGO_PUBLIC_KEY` | MercadoPago Public Key |
| `MERCADOPAGO_WEBHOOK_SECRET` | MercadoPago webhook secret for signature validation |

> Get your MercadoPago test credentials at [developers.mercadopago.com](https://developers.mercadopago.com).

---

## Project Structure

```
vinil/
├── accounts/           # Auth app (email login, registration, profile)
├── core/               # Django project config (settings.py, urls.py)
├── events/             # Events app
├── orders/             # Orders app
├── payments/           # Payments + MercadoPago integration
├── tickets/            # Ticket types and individual tickets
├── templates/          # All HTML templates
│   ├── base.html
│   ├── base_dashboard.html
│   └── components/     # Reusable navbar, sidebar, footer, messages
├── docs/               # Architecture, conventions, design system docs
├── .env.example        # Environment variable template
├── manage.py
└── requirements.txt
```

---

## Screenshots

> Coming soon.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Open a pull request
