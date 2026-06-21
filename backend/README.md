# Backend — rieakane.com

The API for [rieakane.com](https://rieakane.com), built with **Django 5.2** +
**Django REST Framework**, running in Docker against **PostgreSQL**.

## Stack

- Django 5.2 + Django REST Framework
- PostgreSQL 17 (via Docker; falls back to SQLite when no `POSTGRES_DB` is set)
- WhiteNoise (static files), django-cors-headers (CORS for the Angular app)
- Gunicorn (production WSGI server)
- Configuration via environment variables / `python-dotenv`

## Prerequisites

- **Docker** + Docker Compose

That's all you need — Python and Postgres run inside containers.

## Running

All commands run from this `backend/` directory (where `docker-compose.yml` lives):

```bash
docker compose up --build           # starts Postgres + Django on :8000
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser   # optional
```

- API base: `http://localhost:8000/api/`
- Django admin: `http://localhost:8000/admin/`
- Source is volume-mounted, so Django auto-reloads on edits.

Stop with `docker compose down` (add `-v` to also drop the database volume).

## API endpoints

| Method | Path           | Description                |
| ------ | -------------- | -------------------------- |
| GET    | `/api/health/` | Liveness check → `{"status": "ok"}` |

## Project layout

```
backend/
├── config/              # Django project (settings, urls, wsgi/asgi)
├── api/                 # API app (views, urls)
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml   # Postgres + Django
└── .env.example         # template for backend/.env
```

## Environment variables

When running via Docker, these are supplied by `docker-compose.yml`. To run
outside Docker, copy `.env.example` to `.env` and adjust:

| Variable                       | Purpose                                              |
| ------------------------------ | ---------------------------------------------------- |
| `DJANGO_SECRET_KEY`            | Django secret key (required in production)           |
| `DJANGO_DEBUG`                 | `True`/`False`                                       |
| `DJANGO_ALLOWED_HOSTS`         | Comma-separated hostnames                            |
| `DJANGO_CORS_ALLOWED_ORIGINS`  | Origins allowed to call the API (the Angular app)    |
| `DJANGO_CSRF_TRUSTED_ORIGINS`  | Trusted origins for HTTPS form/admin posts (prod)    |
| `POSTGRES_DB` / `_USER` / `_PASSWORD` / `_HOST` / `_PORT` | Postgres connection. The app uses Postgres when `POSTGRES_DB` is set, else SQLite. |

`backend/.env` is gitignored — never commit real secrets.

## Running tests

```bash
docker compose exec backend python manage.py test
```
