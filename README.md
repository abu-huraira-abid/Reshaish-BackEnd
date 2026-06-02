# Rehaish Backend

Django REST Framework backend for the Rehaish Phase-1 smart renting ecosystem.

## Setup

```powershell
cd "C:\Users\HS TRADER\OneDrive\Documents\Rehaish-Backend"
poetry install
Copy-Item .env.example .env
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

If Poetry is not installed:

```powershell
python -m pip install poetry
```

## PostgreSQL

Create a PostgreSQL database matching `.env`:

```sql
CREATE DATABASE rehaish;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE rehaish TO postgres;
```

Use a stronger user/password outside local development.

Or run the included local PostgreSQL container:

```powershell
docker compose up -d postgres
```

If you already have PostgreSQL installed locally, update `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_HOST`, and `POSTGRES_PORT` in `.env` to match your
real server before running migrations.

## Apps

- `accounts`: custom user, roles, auth profile
- `properties`: listings, ownership proof, agent verification reports
- `visits`: visit requests, QR tokens, check-in/check-out
- `agreements`: rental agreements and key handover
- `payments`: payment transactions and commission ledger
- `services_marketplace`: third-party service orders
- `flatmates`: flatmate profiles and matches
- `audit`: audit log model

## App Structure

Each domain app follows this structure:

```text
app/
  models/          # one model or related model group per file
  serializers/     # DRF serializers split by resource
  views/           # viewsets split by API resource
  services/        # business logic and state transitions
  permissions.py   # role and resource permissions for the app
  admin.py
  apps.py
  migrations/
```

Keep workflow decisions in `services/`, request/response shaping in
`serializers/`, and HTTP/API behavior in `views/`.
