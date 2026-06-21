# CLAUDE.md

This repository follows a standard set of development, design, testing, and
security conventions maintained at the workspace level, outside this repository.

**Before working in this repo, read and apply the workspace guidelines in
`../CLAUDE.md`.** They are the source of truth for architecture, coding patterns,
UI/UX, testing, and security practices.

## Project

Monorepo for a personal website:

- `frontend/` — Angular public single-page app (runs locally)
- `backend/` — Django + DRF API, Dockerized with PostgreSQL
- `admin/` — Angular admin panel (internal only; never publicly reachable)
- `shared/` — shared design tokens (single source of truth for colors/theming)

See `README.md` and the per-package READMEs for setup and commands.
