# rieakane.com

Personal website of **Rie Akane** — a monorepo with a public frontend, an API
backend, and an internal admin panel.

```
rieakane.com/
├── frontend/   # Angular public site (SPA)            → see frontend/README.md
├── backend/    # Django + DRF API (Dockerized)        → see backend/README.md
├── admin/      # Angular admin panel (internal only)  → see admin/README.md
└── shared/     # shared design tokens (single source of truth for colors)
```

## Tech stack

- **Frontend:** Angular 22 (standalone components, signals, SCSS) — runs locally
- **Backend:** Django 5.2 + Django REST Framework, in Docker with PostgreSQL
- **Admin:** Angular 22, separate app on its own port; talks to admin-only API
- **Theming:** one global token file (`shared/styles/`), light + dark + color-
  vision-deficiency modes; primary/secondary brand colors constant across modes
- **Domain:** [rieakane.com](https://rieakane.com)

## Quick start

Start the backend first, then either Angular app.

**Backend** (Docker — Postgres + Django on `:8000`, migrates on startup):

```bash
cd backend
docker compose up --build
```

**Frontend** (dev server on `:4200`, proxies `/api` → backend):

```bash
cd frontend
nvm use 24
npm install      # first time only
npm start        # → http://localhost:4200
```

**Admin** (dev server on `:4300`, internal only):

```bash
cd admin
nvm use 24
npm install      # first time only
npm start        # → http://localhost:4300
```

## Documentation

- [`frontend/README.md`](frontend/README.md) — public site setup, build, dev server
- [`backend/README.md`](backend/README.md) — API, endpoints, environment, tests
- [`admin/README.md`](admin/README.md) — admin panel, features, security notes

## Prerequisites

- **Docker** + Docker Compose (backend)
- **Node** 24.15+ via [nvm](https://github.com/nvm-sh/nvm) (frontend & admin)

## Security

The **server is the only authority** for auth, authorization, and validation.
The admin panel is for the owner/team only — it must be network-restricted, use
MFA, and is never publicly reachable. See the workspace conventions referenced in
`CLAUDE.md`.
