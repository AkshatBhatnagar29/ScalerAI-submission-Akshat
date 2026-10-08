# AWS Route53 Clone

This project is a functional Route53 UX clone with mocked authentication, persistent SQLite storage, and a FastAPI backend. It is designed for local development and does not connect to AWS.

## Features

- Mock login, logout, HTTP-only session cookie, protected routes, and session persistence while the backend is running
- Hosted Zone view, search, create, edit, delete, pagination, record counts, and SQLite persistence
- DNS Record view, search, type filters, pagination, create, edit, delete, confirmation dialogs, and notifications
- Supported record types: A, AAAA, CNAME, TXT, MX, NS, PTR, SRV, and CAA
- AWS-style Route53 navigation, header, sidebar, breadcrumbs, tables, forms, loading, empty, and error states
- Placeholder pages for Dashboard, Traffic Policies, Health Checks, Resolver, and Profiles

Optional bonus features such as BIND import, export, dark mode, keyboard shortcuts, and bulk operations are not implemented.

## Tech stack

- Frontend: Next.js 14, React, TypeScript
- Backend: FastAPI, Python
- Database: SQLite and SQLAlchemy

## Architecture

```text
Next.js frontend
        ↓
FastAPI HTTP API
        ↓
Service and repository layers
        ↓
SQLAlchemy models and sessions
        ↓
SQLite database
```

## Project structure

```text
frontend/
  app/              Next.js routes and page components
  components/       Auth, shell, notices, and shared UI
  services/         Typed frontend API client
  public/           AWS and Route53 assets
backend/
  app/api/          Authentication, hosted zone, and DNS record routes
  app/core/         Configuration, security, and dependencies
  app/database/     SQLAlchemy base, models, and sessions
  app/repositories/ Database queries and persistence operations
  app/services/     Business rules and ownership checks
  app/schemas/      Pydantic request and response schemas
  tests/            Backend API and validation tests
```

## Database schema

`hosted_zones` stores the zone name, public/private type, description, generated Route53-style zone ID, owner, timestamps, and denormalized record count.

`dns_records` stores the record name, type, TTL, value, structured MX/SRV/CAA fields, comments, timestamps, and its `hosted_zone_id` foreign key. A HostedZone has many DNSRecords. The relationship uses a foreign key with cascade delete and SQLAlchemy `delete-orphan` behavior, so deleting a zone does not leave orphaned records.

## API overview

Authentication:

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`

Hosted Zones:

- `GET /api/hosted-zones`
- `GET /api/hosted-zones/{id}`
- `POST /api/hosted-zones`
- `PUT /api/hosted-zones/{id}`
- `DELETE /api/hosted-zones/{id}`

DNS Records:

- `GET /api/hosted-zones/{id}/records`
- `GET /api/hosted-zones/{id}/records/{record_id}`
- `POST /api/hosted-zones/{id}/records`
- `PUT /api/hosted-zones/{id}/records/{record_id}`
- `DELETE /api/hosted-zones/{id}/records/{record_id}`

The records list accepts `search`, `type`, `page`, and `page_size`. Hosted Zone lists accept `search`, `page`, and `page_size`. Interactive OpenAPI documentation is available at `/docs`.

## Setup and running

Prerequisites: Python 3.11+ and Node.js/npm.

Backend:

```powershell
cd backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

Frontend, in a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open <http://localhost:3000>. The backend health endpoint is <http://localhost:8000/health> and API docs are at <http://localhost:8000/docs>.

The backend creates the configured SQLite database directory automatically. SQLite is embedded; no SQLite server, AWS CLI, AWS SDK, Redis, PostgreSQL, Docker, or other service is required.

### Environment variables

Backend variables are documented in [backend/.env.example](backend/.env.example): `MOCK_USERNAME`, `MOCK_PASSWORD`, `FRONTEND_ORIGIN`, `COOKIE_SECURE`, `COOKIE_SAMESITE`, `SESSION_SECRET`, and `DATABASE_URL`.

Frontend variables are documented in [frontend/.env.example](frontend/.env.example): `NEXT_PUBLIC_API_BASE_URL` and the server-side `BACKEND_API_URL` proxy target. Do not put secrets in `NEXT_PUBLIC_*` variables. Local `.env` files are intentionally ignored by Git.

### Mock credentials

Development-only mock credentials:

```text
Username: admin
Password: admin123
```

## Running Backend

```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Running Frontend

```powershell
cd frontend
npm run build
npm run start
```

Set `NEXT_PUBLIC_API_BASE_URL` to the deployed backend URL when the frontend and backend are hosted independently. For local development, leave it empty and set `BACKEND_API_URL` for the Next.js rewrite proxy.

## Testing

Backend tests:

```powershell
cd backend
pytest
```

Frontend production build:

```powershell
cd frontend
npm run build
```

The test suite covers authentication, protected routes, Hosted Zone CRUD/search/pagination, all required record types, type-specific validation, ownership isolation, filters, combined search and filter behavior, and cascade deletion.

## Screenshots

No screenshots are included in the repository, so none are documented here.

## Limitations

- DNS behavior and Route53 data are mocked; no real AWS Route53 API is used.
- AWS IAM, accounts, regions, and permissions are mocked for the local experience.
- Dashboard, Traffic Policies, Health Checks, Resolver, and Profiles are placeholder sections.
- Sessions are held in the backend process memory and therefore are not intended for multi-process or production deployment.

## Deployment Instructions

These instructions are provider-neutral because no hosting provider is configured in this repository:

1. Deploy the FastAPI backend with the production-like Uvicorn command above.
2. Configure persistent storage for the SQLite database.
3. Set backend environment variables, including `DATABASE_URL`, `FRONTEND_ORIGIN`, `COOKIE_SECURE`, and `COOKIE_SAMESITE`.
4. Deploy the Next.js frontend with `npm run build` and `npm run start` or the provider’s equivalent.
5. Set frontend `NEXT_PUBLIC_API_BASE_URL` to the backend URL.
6. Set backend `FRONTEND_ORIGIN` to the exact frontend origin.
7. Verify login, refresh, `/api/auth/me`, and logout.
8. Verify Hosted Zone creation, editing, searching, pagination, and deletion.
9. Verify DNS Record CRUD, search, filters, pagination, and ownership isolation.
10. Restart the backend and verify that Hosted Zones and DNS Records still exist.

IMPORTANT: SQLite must be stored on a persistent disk or volume in production. An ephemeral filesystem will not satisfy the persistence requirement.

Deployment placeholders:

```text
Frontend URL: TODO — add deployed frontend URL
Backend URL: TODO — add deployed backend URL
Swagger URL: TODO — add deployed backend Swagger URL
```

## Deployment readiness

The frontend has a production build, the backend starts with configurable CORS and SQLite settings, and environment variables are documented. No hosted URL or automatic deployment is configured. Deployment is not complete until the manual hosting, persistent-volume, environment-variable, and hosted-demo verification steps above are performed.
