# CAS Vault (Simple Demo)

A minimal FastAPI app with:
- File upload + deduplication (SHA-256)
- SQLite DB via SQLAlchemy ORM
- JWT auth (demo user)
- Basic web UI
- CI workflow for lint + tests

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export JWT_SECRET=$(python -c 'import secrets; print(secrets.token_hex(16))')
python -m app.scripts.seed_demo_user
uvicorn app.main:create_app --factory --reload
```
Open http://localhost:8000/

## Run with Docker
```bash
docker compose up --build
```
Open http://localhost:8000/


---

## CI (GitHub Actions)
Push to `main` and see tests run under **Actions → CI**.

Add a badge to your README (after first run):

```md
![CI](https://github.com/<your-org>/<your-repo>/actions/workflows/ci.yml/badge.svg)
```

## CD (Optional) — Deploy to Azure App Service (Container)
Set these repository **Secrets** (Settings → Secrets and variables → Actions):
- `AZURE_CREDENTIALS` → Azure OIDC/Service Principal JSON
- `APP_SERVICE_NAME` → Your App Service name
- `APP_SERVICE_RG` → Resource group
- `JWT_SECRET` → Random string

Trigger the **Deploy** workflow on push to `main` or via **Run workflow**.

> Note: This simple demo uses **SQLite + local filesystem** in the container; App Service’s filesystem is ephemeral. For persistent prod usage, wire a managed DB + Blob storage later.
