<div align="center">

# 🤖 Telegram-Ecom-Bot-v2

**Automated e-commerce sales bot for Telegram — built for speed, scale, and seamless checkout.**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)](https://github.com/) [![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com) [![License: MIT](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)](LICENSE) [![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)](Dockerfile) [![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://www.mongodb.com) [![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?style=flat-square&logo=stripe&logoColor=white)](https://stripe.com)

<br/>

<img src="docs/assets/demo-screenshot.png" alt="Bot Demo" width="680"/>

<br/>

*A production-grade Telegram bot that turns any channel into a fully automated storefront — complete with product catalog, persistent cart, Stripe checkout, and real-time order tracking.*

</div>

---

## Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Architecture

```
┌──────────────┐       ┌──────────────────┐       ┌─────────────┐
│   Telegram   │◄─────►│   FastAPI Core    │◄─────►│   MongoDB   │
│   Bot API    │       │  (async/await)    │       │   Atlas     │
└──────────────┘       └────────┬─────────┘       └─────────────┘
                                │
                     ┌──────────┴──────────┐
                     │                     │
              ┌──────▼──────┐       ┌──────▼──────┐
              │   Stripe    │       │    Redis    │
              │  Payments   │       │   Cache     │
              └─────────────┘       └─────────────┘
```

The bot operates on a **webhook-driven event loop**. Incoming Telegram updates hit the FastAPI server, get routed through the conversation handler middleware, and dispatch to the appropriate service layer. Cart state is persisted in MongoDB with TTL-indexed sessions, while Redis handles rate limiting and catalog caching.

---

## Features

### Core Commerce
- **Dynamic Product Catalog** — CRUD operations via admin commands; supports categories, variants, and image galleries
- **Persistent Shopping Cart** — per-user cart with quantity management, auto-expiration (configurable TTL), and inline keyboard UI
- **Stripe Checkout Integration** — PCI-compliant payment flow with Payment Intents API, automatic webhook reconciliation, and refund handling
- **Order Lifecycle Management** — status tracking from `pending` → `paid` → `shipped` → `delivered` with push notifications at each stage

### Bot Intelligence
- **Conversational Flow Engine** — finite-state machine for guided purchase flows, with graceful fallback on unexpected input
- **Multi-Language Support** — i18n via `gettext` with 6 pre-configured locales (EN, IT, ES, DE, FR, PT)
- **Smart Search** — fuzzy product matching powered by MongoDB Atlas Search with typo tolerance and synonym expansion
- **Rate Limiting** — per-user throttling via Redis sliding window to prevent abuse

### Operations & Observability
- **Admin Dashboard Commands** — `/stats`, `/orders`, `/inventory`, `/broadcast` accessible to authorized Telegram user IDs
- **Structured Logging** — JSON logs with correlation IDs, shipped to stdout for easy ingestion by ELK/Datadog/Grafana Loki
- **Health Checks** — `/health` and `/ready` endpoints for orchestrator probes
- **Graceful Shutdown** — SIGTERM handler drains in-flight requests before exit

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Runtime | Python 3.11+ | Core language |
| Framework | FastAPI 0.104 | Async HTTP server + webhook receiver |
| Bot SDK | python-telegram-bot 20.x | Telegram Bot API abstraction |
| Database | MongoDB 7.0 | Persistent storage (carts, orders, products, users) |
| Cache | Redis 7.x | Session cache, rate limiter, pub/sub |
| Payments | Stripe Python SDK | Payment Intents, webhooks, refunds |
| Validation | Pydantic v2 | Request/response schemas |
| Containerization | Docker + Compose | Reproducible local & production environments |
| CI/CD | GitHub Actions | Lint, test, build, deploy pipeline |

---

## Project Structure

```
Telegram-Ecom-Bot-v2/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Lint + test on PR
│       └── deploy.yml              # Build & push to registry
├── src/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app factory + lifespan
│   ├── config.py                   # Pydantic Settings (env parsing)
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers/
│   │   │   ├── start.py            # /start, /help commands
│   │   │   ├── catalog.py          # Browse, search, product detail
│   │   │   ├── cart.py             # Add, remove, view cart
│   │   │   ├── checkout.py         # Payment flow orchestration
│   │   │   ├── orders.py           # Order status, history
│   │   │   └── admin.py            # Admin-only commands
│   │   ├── keyboards/
│   │   │   ├── inline.py           # InlineKeyboardMarkup builders
│   │   │   └── reply.py            # ReplyKeyboardMarkup builders
│   │   ├── middlewares/
│   │   │   ├── auth.py             # Admin role verification
│   │   │   ├── rate_limit.py       # Redis-backed throttle
│   │   │   └── i18n.py             # Locale detection + translation
│   │   └── fsm/
│   │       ├── states.py           # Conversation state definitions
│   │       └── engine.py           # State machine dispatcher
│   ├── services/
│   │   ├── product_service.py      # Catalog business logic
│   │   ├── cart_service.py         # Cart operations + TTL mgmt
│   │   ├── order_service.py        # Order creation + status updates
│   │   ├── payment_service.py      # Stripe integration layer
│   │   └── notification_service.py # Push notifications to users
│   ├── models/
│   │   ├── product.py              # Product document schema
│   │   ├── cart.py                 # Cart document schema
│   │   ├── order.py                # Order document schema
│   │   └── user.py                 # User profile schema
│   ├── db/
│   │   ├── mongo.py                # Motor async client + indexes
│   │   └── redis.py                # aioredis connection pool
│   ├── api/
│   │   ├── routes/
│   │   │   ├── webhooks.py         # Telegram + Stripe webhook endpoints
│   │   │   └── health.py           # Liveness + readiness probes
│   │   └── deps.py                 # FastAPI dependency injection
│   └── utils/
│       ├── logging.py              # Structured JSON logger
│       ├── security.py             # Webhook signature verification
│       └── helpers.py              # Formatting, currency, pagination
├── tests/
│   ├── conftest.py                 # Fixtures (mock DB, bot, Stripe)
│   ├── unit/
│   │   ├── test_cart_service.py
│   │   ├── test_payment_service.py
│   │   └── test_fsm_engine.py
│   └── integration/
│       ├── test_checkout_flow.py
│       └── test_webhook_handling.py
├── locales/
│   ├── en/LC_MESSAGES/messages.po
│   ├── it/LC_MESSAGES/messages.po
│   └── ...
├── scripts/
│   ├── seed_products.py            # Populate DB with sample catalog
│   └── generate_locales.sh         # Compile .po → .mo files
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- Python ≥ 3.11
- Docker & Docker Compose v2
- A [Telegram Bot Token](https://core.telegram.org/bots#botfather) from BotFather
- A [Stripe API Key](https://dashboard.stripe.com/apikeys) (test mode for development)
- MongoDB Atlas cluster (or local instance via Docker)

### 1. Clone & Install

```bash
git clone https://github.com/MarcoS-Dev0/Telegram-Ecom-Bot-v2.git
cd Telegram-Ecom-Bot-v2

# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials (see Environment Variables below)
```

### 3. Start Infrastructure

```bash
# Spin up MongoDB + Redis via Docker
docker compose up -d mongo redis

# Seed the product catalog
python scripts/seed_products.py
```

### 4. Run the Bot

```bash
# Development (with hot-reload)
uvicorn src.main:app --reload --port 8000

# Or via Docker (full stack)
docker compose up --build
```

### 5. Set Webhook

```bash
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourdomain.com/api/v1/webhooks/telegram"}'
```

---

## Environment Variables

| Variable | Description | Default |
|----------|------------|---------|
| `BOT_TOKEN` | Telegram Bot API token | *required* |
| `STRIPE_SECRET_KEY` | Stripe secret key | *required* |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | *required* |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGO_DB_NAME` | Database name | `ecom_bot` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `WEBHOOK_BASE_URL` | Public HTTPS URL for webhooks | *required* |
| `ADMIN_USER_IDS` | Comma-separated Telegram user IDs | `""` |
| `CART_TTL_HOURS` | Cart expiration in hours | `72` |
| `DEFAULT_LOCALE` | Fallback language code | `en` |
| `LOG_LEVEL` | Logging level | `INFO` |

---

## API Documentation

Once the server is running, interactive API docs are available at:

- **Swagger UI** → `http://localhost:8000/docs`
- **ReDoc** → `http://localhost:8000/redoc`

### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/webhooks/telegram` | Telegram update receiver |
| `POST` | `/api/v1/webhooks/stripe` | Stripe event handler |
| `GET` | `/health` | Liveness probe |
| `GET` | `/ready` | Readiness probe (DB + Redis connectivity) |

---

## Deployment

### Docker (Recommended)

```bash
# Production build
docker compose -f docker-compose.prod.yml up -d --build

# Scale workers
docker compose -f docker-compose.prod.yml up -d --scale bot=3
```

### Manual

```bash
# Install production deps only
pip install .

# Run with Gunicorn + Uvicorn workers
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 --timeout 120
```

---

## Testing

```bash
# Run full suite
pytest --cov=src --cov-report=term-missing

# Unit tests only
pytest tests/unit -v

# Integration tests (requires running Docker services)
pytest tests/integration -v --runslow
```

---

## Roadmap

- [x] Core cart + checkout flow
- [x] Stripe Payment Intents integration
- [x] Multi-language support
- [x] Docker Compose production config
- [ ] Crypto payments (TON blockchain via TON Connect)
- [ ] AI product recommendations (collaborative filtering)
- [ ] Subscription / recurring orders
- [ ] Analytics export to CSV / webhook

---

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change, then submit a PR against `develop`.

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/amazing-feature`)
3. Commit with conventional commits (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

---

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

<div align="center">
  <sub>Built with ☕ and asyncio — star the repo if you find it useful.</sub>
</div>
