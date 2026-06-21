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
- Admin-only API: `http://localhost:8000/api/v1/admin/` (consumed by the `admin/` app)
- Django admin: at `DJANGO_ADMIN_URL` (default `control-panel/`, not `/admin/`)
- Source is volume-mounted, so Django auto-reloads on edits. The dev container
  runs migrations automatically on startup.

Stop with `docker compose down` (add `-v` to also drop the database volume).

## API endpoints

| Method | Path                                  | Auth        | Description                          |
| ------ | ------------------------------------- | ----------- | ------------------------------------ |
| GET    | `/api/health/`                        | public      | Liveness check → `{"status": "ok"}`  |
| POST   | `/api/v1/admin/auth/login/`           | public      | Admin login (password + MFA) → token |
| POST   | `/api/v1/admin/auth/logout/`          | admin token | Invalidate the caller's token        |
| GET    | `/api/v1/admin/auth/me/`              | admin token | Current admin profile + role         |
| —      | `/api/v1/admin/users/`                | superadmin  | Admin user management (CRUD)         |
| —      | `/api/v1/admin/error-logs/`           | admin       | Error logs (list / resolve)          |
| —      | `/api/v1/admin/audit-logs/`           | admin       | Audit trail (list, `/models/`)       |

All admin endpoints are **default-deny**, throttled, and paginated. Roles are
enforced server-side; the admin UI only reflects them.

## Project layout

```
backend/
├── config/              # Django project (settings, settings_test, urls, wsgi/asgi)
├── api/                 # Public API app (health)
├── accounts/            # Custom user model with roles
├── audit/               # ErrorLog + AuditLog, middleware, signals, exception handler
├── adminpanel/          # Admin-only DRF API (users, error/audit logs, MFA login)
├── manage.py
├── requirements.txt     # single file — dev mirrors prod (incl. test/lint tools)
├── conftest.py          # shared pytest fixtures
├── pytest.ini
├── Dockerfile
├── docker-compose.yml   # Postgres + Django
└── .env.example         # template for backend/.env
```

## Admin support (error logs, audit trail, roles)

- **`accounts.User`** — custom user model with a `role` (superadmin / admin /
  editor / support / readonly), enforced server-side.
- **`audit.ErrorLog`** — every unhandled error is persisted (DRF exception
  handler + middleware) so it shows in the admin's Error logs tab.
- **`audit.AuditLog`** — every create/update/delete on tracked models
  (`DJANGO_AUDIT_TRACKED_APPS`) is recorded with a per-field diff and the acting
  user. Sensitive fields are scrubbed.
- **MFA** — admin login verifies a TOTP code when the user has a confirmed
  device; set `DJANGO_REQUIRE_MFA=True` (default in production) to require
  enrolment. Wire up device enrolment (django-otp) before going live.

## Environment variables

When running via Docker, these are supplied by `docker-compose.yml`. To run
outside Docker, copy `.env.example` to `.env` and adjust:

| Variable                       | Purpose                                              |
| ------------------------------ | ---------------------------------------------------- |
| `DJANGO_SECRET_KEY`            | Django secret key (required in production)           |
| `DJANGO_DEBUG`                 | `True`/`False`                                       |
| `DJANGO_ALLOWED_HOSTS`         | Comma-separated hostnames                            |
| `DJANGO_CORS_ALLOWED_ORIGINS`  | Origins allowed to call the API (frontend :4200, admin :4300) |
| `DJANGO_CSRF_TRUSTED_ORIGINS`  | Trusted origins for HTTPS form/admin posts (prod)    |
| `DJANGO_ADMIN_URL`             | Django admin path (non-default; e.g. `control-panel/`) |
| `DJANGO_REQUIRE_MFA`           | Require MFA at admin login (defaults ON when `DEBUG=False`) |
| `DJANGO_AUDIT_TRACKED_APPS`    | Comma-separated apps whose models are audited        |
| `POSTGRES_DB` / `_USER` / `_PASSWORD` / `_HOST` / `_PORT` | Postgres connection. The app uses Postgres when `POSTGRES_DB` is set, else SQLite. |

`backend/.env` is gitignored — never commit real secrets.

## Running tests

The suite uses **pytest + pytest-django** with in-memory SQLite. The test tools
ship in the same image (dev = prod parity), so no extra install is needed:

```bash
docker compose exec backend pytest
```

Run `python manage.py check --deploy` and `pip-audit` before any release.
