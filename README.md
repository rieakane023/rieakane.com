# rieakane.com

Personal website of **Rie Akane**. Monorepo containing the frontend and backend.

```
rieakane.com/
├── frontend/            # Angular single-page app (runs locally)
├── backend/             # Django + DRF API (runs in Docker)
└── docker-compose.yml   # Postgres + Django backend
```

## Prerequisites

- **Docker** + Docker Compose — for the backend and database
- **Node** 24.15+ (managed via `nvm`) — for the frontend: `nvm use 24`

## Backend (Docker)

The backend (Django) and PostgreSQL run in Docker:

```bash
docker compose up --build           # starts Postgres + Django on :8000
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser   # optional
```

- API base: `http://localhost:8000/api/`
- Health check: `GET http://localhost:8000/api/health/` → `{"status": "ok"}`
- Source is volume-mounted, so Django auto-reloads on edits.

Stop with `docker compose down` (add `-v` to also wipe the database volume).

## Frontend (local)

The Angular app runs on your machine and proxies `/api/*` to the backend
container on port 8000 (see `frontend/proxy.conf.json`):

```bash
cd frontend
nvm use 24
npm install                         # first time only
npm start                           # http://localhost:4200
```

Production build: `npm run build` → outputs to `frontend/dist/`.

## Environment variables

For Docker, backend config lives in `docker-compose.yml`. For running the
backend outside Docker, copy `backend/.env.example` to `backend/.env`. The app
uses PostgreSQL when `POSTGRES_DB` is set, otherwise falls back to SQLite.
