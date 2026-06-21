# rieakane.com

Personal website of **Rie Akane** — a monorepo containing the web frontend and
the API backend.

```
rieakane.com/
├── frontend/   # Angular single-page app          → see frontend/README.md
└── backend/    # Django + DRF API (Dockerized)     → see backend/README.md
```

## Tech stack

- **Frontend:** Angular (standalone components, SCSS, routing) — runs locally
- **Backend:** Django 5.2 + Django REST Framework, in Docker with PostgreSQL
- **Domain:** [rieakane.com](https://rieakane.com)

## Quick start

The two halves run independently. Start the backend first, then the frontend.

**Backend** (Docker — Postgres + Django on `:8000`):

```bash
cd backend
docker compose up --build
```

**Frontend** (Angular dev server on `:4200`, proxies `/api` → backend):

```bash
cd frontend
nvm use 24
npm install      # first time only
npm start
```

Then open <http://localhost:4200>.

## Documentation

- [`frontend/README.md`](frontend/README.md) — frontend setup, build, and dev server
- [`backend/README.md`](backend/README.md) — backend setup, API, environment, and tests

## Prerequisites

- **Docker** + Docker Compose (backend)
- **Node** 24.15+ via [nvm](https://github.com/nvm-sh/nvm) (frontend)
