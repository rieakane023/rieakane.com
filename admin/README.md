# Admin — rieakane.com

The **internal admin panel** for rieakane.com. A separate Angular app (not part
of the public site) that talks to the backend's admin-only API.

> **Internal tool — never expose this publicly.** It must sit behind network
> restriction (VPN / IP allowlist / access proxy), every account uses MFA, and
> roles are enforced server-side. See the workspace security conventions.

## Stack

- Angular 22 (standalone components, signals, lazy-loaded routes)
- Token auth against `/api/v1/admin/`, attached via a functional interceptor
- Shared design tokens from `../shared/styles` (same palette as the public site,
  light/dark + color-vision-deficiency modes)

## Running

Runs on **:4300** (the public frontend uses :4200) and proxies `/api` → backend
on :8000. Start the backend first.

```bash
nvm use 24
npm install        # first time only
npm start          # ng serve on http://localhost:4300
```

Build / test:

```bash
npm run build      # production build
npm test           # unit tests (vitest)
```

## Features

| Route          | Purpose                                                            |
| -------------- | ----------------------------------------------------------------- |
| `/login`       | Credential + MFA sign-in; issues an admin API token               |
| `/dashboard`   | At-a-glance metrics (users, unresolved errors, audit entries)     |
| `/users`       | **User management** — create/role/deactivate admins (superadmin)  |
| `/error-logs`  | **Error logs** — searchable, filterable, expandable, resolvable   |
| `/audit`       | **Audit trail** — per-model field diffs (old/new/by/when)         |

The last three are the mandatory admin tabs. All tables follow the workspace
table standard: sticky headers, type-aligned columns, search/filter, server-side
pagination ("X–Y of N"), and loading / empty / error states.

## Structure

```
admin/src/app/
├── core/        # auth service, interceptor, guard, api service, theme, models
├── shared/      # shell (sidebar nav, role display, theme/CVD switch)
└── features/    # login, dashboard, users, error-logs, audit
```

## Security notes

- Route guards are **UX only** — the backend enforces every permission.
- The auth token is scoped to same-origin `/api/` calls and never leaked
  cross-origin.
- `noindex, nofollow` is set; deploy on a restricted host, not the public domain.
