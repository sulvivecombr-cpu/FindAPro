# Find A Pro — Base44 Dev Environment Notes

## Stack
- Django 5.0.1 (server-rendered templates + DRF), PostgreSQL 16, Tailwind CSS 3.
- Frontend is Django templates, not a SPA — the web entry point is Django itself.

## Running (Base44 sandbox)
- `docker compose -f docker-compose.base44.yml up -d` — starts `db` (postgres) and `web`.
- `Dockerfile.base44` provides tooling only (Python + pip deps, Node.js, postgresql-client, curl). Source is bind-mounted; never bake source into an image.
- Web startup command: npm install → build Tailwind CSS → migrate → collectstatic → ensure `admin/adminpassword` superuser → `runserver 0.0.0.0:8000` (auto-reload on .py changes).
- Host port 3000 maps to Django on 8000.
- Restarting `web` re-runs the full startup (npm install is quick once cached, Tailwind rebuilds output.css — it is gitignored).

## Environment / secrets
- Local infra credentials (postgres) are inline in compose — not secrets.
- `SECRET_KEY` generated as dev placeholder (`requiredAtBoot`, `generatedForDevelopment`).
- `OPENAI_API_KEY` — optional user secret; B-Cubed AI tools (`/bcubed/`) need it, app boots without it (defaults to empty string).
- `.env.base44-defaults` holds placeholders; `/run/base44/app.env` is listed last and wins.
- `ALLOWED_HOSTS=*` in compose (dev only); `DEBUG=True`.
- `BASE44_PREVIEW_MODE=1` is passed through; nothing in the app reads it yet.

## Quirks
- `apps/core/views.py` imports `from django.db import models` at module bottom, after HomeView — works because it runs at module import, but don't "clean it up" blindly.
- `STATICFILES_STORAGE` is whitenoise `CompressedManifestStaticFilesStorage` — static URLs resolve via manifest, so Tailwind must build `output.css` before `collectstatic`. CSS changes require re-running `collectstatic` (restart `web`).
- `makemigrations` is NOT run on startup (only `migrate`) — existing migrations are current; avoid auto-generating files into the repo.
- Verify: `curl http://localhost:3000/` → 200 and contains `<title>`.
