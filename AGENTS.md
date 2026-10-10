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

## Phase 0 foundation (apps/foundation)
- LGPD model: UserProfile (role/account_type/status/locale), ProfessionalProfile (stub), ConsentRecord, AccountDeletionRequest, AuditLog (append-only — save() blocks edits), LegalDocument (5 pt-BR docs seeded by migration 0002; platform content, not user data).
- Row-level security is enforced at the app layer: models expose `for_user(user)`; views guard with `login_required` + role checks (client hitting professional onboarding gets 403). Postgres-level RLS not in place.
- Signup: `foundation.views.SignUpView` mounted at `/accounts/register/` (accounts/urls was repointed). Intent values MUST be `customer`/`provider` (matches `CustomUser.user_type`). Consent captured with IP+UA at signup; Google signups go through a consent screen.
- Google OAuth: minimal stdlib module `foundation/google_oauth.py`; requires GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET secrets (button hidden until configured). Uses Google tokeninfo endpoint for validation.
- Account deletion: `/settings/conta/excluir/` — password confirm → AccountDeletionRequest + AuditLog → anonymize (is_active=False, email rewritten) → logout.
- Routing map: /, /categories, /legal/*, /app/*, /settings/*, /admin (staff only); handlers 403/404/500 in config/urls.py. Legacy marketplace modules (providers, reviews, bcubed, accounts) stay mounted but unlinked — rebuilt in later phases.
- Design tokens in tailwind.config.js + `fp-*` component classes in static/src/input.css; dark mode via `class` + localStorage key `findapro-theme` ('light'|'dark'|'system'), applied before first paint in base.html.
- base.html must keep blocks: title, extra_head, extra_css, content, extra_js (56 legacy templates extend it).
- Verify flows: `DJANGO_SETTINGS_MODULE=config.settings python -` with a Django test Client (signup, deletion, 403). Zero user records required — delete any test accounts created during verification.

## Quirks
- `apps/core/views.py` imports `from django.db import models` at module bottom, after HomeView — works because it runs at module import, but don't "clean it up" blindly.
- `STATICFILES_STORAGE` is whitenoise `CompressedManifestStaticFilesStorage` — static URLs resolve via manifest, so Tailwind must build `output.css` before `collectstatic`. CSS changes require re-running `collectstatic` (restart `web`).
- `makemigrations` is NOT run on startup (only `migrate`) — existing migrations are current; avoid auto-generating files into the repo.
- Verify: `curl http://localhost:3000/` → 200 and contains `<title>`.
