# AGENTS.md — FindAPro (Django + Postgres + Tailwind)

## How to run / verify
- Everything runs from `docker-compose.base44.yml` (the ONLY compose to use in the sandbox — the repo's own `docker-compose.yml` is a production-style setup that needs a repo `.env` and fails without it).
- Web entry: host port **3000 → container 8000** (Django dev server, StatReloader = live reload for Python/templates). Tailwind runs as a background `--watch` process inside the web container, so CSS changes recompile automatically.
- Health: `docker compose -f docker-compose.base44.yml ps` (both services healthy) plus `curl http://localhost:3000/` should return 200.
- Migrations run automatically at container start (`makemigrations` for all 5 local apps, then `migrate`). The `apps/core` app has models-less migrations only.
- After changing `requirements.txt`, rebuild: `docker compose -f docker-compose.base44.yml up -d --build`.

## Non-obvious findings
- Django reads config via `python-decouple`: `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `POSTGRES_*`, `OPENAI_API_KEY`. There is no repo `.env`; in the sandbox these come from compose `environment:` + `/run/base44/app.env`.
- `ALLOWED_HOSTS` must include the wildcard `.${BASE44_SANDBOX_HOST_DOMAIN}` (sandbox host rotates) and `CSRF_TRUSTED_ORIGINS` must include `https://3000-${BASE44_PUBLIC_HOST_SUFFIX}` or login/form POSTs from the preview iframe fail CSRF. Both are set in the Base44 compose only — shared defaults in `config/settings.py` are untouched.
- `whitenoise` uses `CompressedManifestStaticFilesStorage`; `collectstatic` must run before serving with `DEBUG=0`. The Base44 entrypoint runs it always.
- Tailwind source is `static/src/input.css`, compiled to `static/css/output.css` (gitignored). Templates in `/templates`, apps under `apps/` (accounts, providers, reviews, core, bcubed).
- `apps/accounts` and `apps/providers` contain `fixtures/` dirs and Faker-based seed management commands — **do not run any seed/fixture loading**; the project requires zero demo records.
- The HEAD commit (64166ea, "B³ results") boots and serves cleanly; earlier "failed to start" reports were environmental (missing `.env` for the production compose / host allowlist), not code defects.

## Verification commands
- `docker compose -f docker-compose.base44.yml logs web | grep -E "500|Traceback"` — should be empty.
- `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/` — expect 200 (home), as well as `/providers/`, `/bcubed/`, `/admin/` (admin login).
