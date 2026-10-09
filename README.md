# AWS Route 53 Clone

<p align="center">
  <strong>A full-stack recreation of the AWS Route 53 management console</strong>
  <br />
  A modern DNS management interface built with Next.js, TypeScript, FastAPI, and SQLite.
  <br /><br />
  <a href="https://scaler-ai-submission-akshat.vercel.app/"><strong>Live Demo</strong></a>
  &nbsp; · &nbsp;
  <a href="https://scaler-ai-submission-akshat.vercel.app/"><strong>Try the Application</strong></a>
</p>

---

## Overview

AWS Route 53 Clone is a full-stack web application that recreates the look, navigation, and core management workflows of the AWS Route 53 console.

The application provides a centralized interface for managing hosted zones and DNS records, with mock authentication, RESTful APIs, relational data persistence, validation, search, filtering, and pagination.

The frontend follows AWS console design conventions, including its navigation hierarchy, sidebar, breadcrumbs, data tables, forms, notifications, and resource-management workflows. The backend separates API endpoints, business logic, database access, and data validation to maintain a clean and extensible architecture.

**Live application:** [https://scaler-ai-submission-akshat.vercel.app/](https://scaler-ai-submission-akshat.vercel.app/)

## Features

### Authentication and sessions
- Mock login and logout workflows.
- HTTP-only session cookies.
- Protected application routes and authentication checks.
- Session persistence while the backend process remains running.
- Configurable credentials and cookie security settings.

### Hosted Zone management
- Create, view, edit, and delete hosted zones.
- Support for public and private hosted zone configurations.
- Hosted zone descriptions and generated Route 53-style identifiers.
- Search hosted zones by relevant attributes.
- Paginated resource listings.
- DNS record counts associated with hosted zones.
- Persistent storage through SQLite and SQLAlchemy.
- Ownership checks for protected resource operations.

### DNS record management
Manage DNS records within individual hosted zones through dedicated resource views and forms.

Supported record types:

| Record type | Purpose |
|---|---|
| A | Maps a hostname to an IPv4 address |
| AAAA | Maps a hostname to an IPv6 address |
| CNAME | Creates a canonical name alias |
| TXT | Stores text-based DNS information |
| MX | Defines mail exchange servers |
| NS | Identifies authoritative name servers |
| PTR | Supports reverse DNS lookups |
| SRV | Specifies service locations and connection details |
| CAA | Defines certificate authority authorization policies |

DNS record operations include:
- Create, view, edit, and delete records.
- Record-specific fields and validation.
- Search by record attributes.
- Filter records by DNS type.
- Paginated record listings.
- Confirmation dialogs for destructive actions.
- Success notifications and error feedback.
- Automatic record-count updates and relational consistency.

### Route 53 console interface
- AWS-inspired global navigation and service header.
- Collapsible sidebar and nested navigation.
- Breadcrumb-based navigation.
- Resource tables with search and pagination controls.
- Hosted zone details and record-management pages.
- Structured forms, loading indicators, empty states, and error states.
- Placeholder sections for Dashboard, Traffic Policies, Health Checks, Resolver, and Profiles.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | Next.js 14, React, TypeScript |
| Styling and UI | React components, CSS, AWS-inspired design system |
| Backend | Python, FastAPI |
| API validation | Pydantic |
| ORM | SQLAlchemy |
| Database | SQLite |
| Authentication | HTTP-only cookies and server-side sessions |
| Testing | Pytest |
| Frontend deployment | Vercel |
| Backend deployment | AWS Lightsail |
| Web server and HTTPS | Nginx, Let's Encrypt |

## Architecture

The application follows a layered architecture that separates the user interface, API endpoints, business rules, and persistence operations.

```text
                  User / Browser
                        |
                        v
              Next.js + TypeScript
                  Frontend UI
                        |
                        v
                REST API Requests
                        |
                        v
                 FastAPI Backend
                        |
             +----------+----------+
             |                     |
             v                     v
      Authentication         API Routers
                                   |
                                   v
                            Service Layer
                         Business Validation
                                   |
                                   v
                           Repository Layer
                          Database Operations
                                   |
                                   v
                         SQLAlchemy Models
                                   |
                                   v
                              SQLite DB
```

### Frontend

The Next.js application handles navigation, page rendering, form interactions, client-side state, authentication checks, and communication with the backend.

A typed API client centralizes HTTP requests and supports cookie-based authentication.

### Backend

FastAPI exposes REST endpoints for authentication, hosted zones, and DNS records. Request and response schemas provide structured validation, while service and repository layers separate business rules from database operations.

### Database

SQLite stores application resources locally on the backend server. SQLAlchemy provides ORM-based database access and relationship management.

For the deployed application, the database is located on the backend server's filesystem and is configured through the `DATABASE_URL` environment variable.

## Project Structure

```text
ScalerAI-submission-Akshat/
│
├── frontend/
│   ├── app/
│   │   ├── login/
│   │   ├── hosted-zones/
│   │   └── ...
│   ├── components/
│   ├── services/
│   ├── public/
│   ├── next.config.mjs
│   ├── package.json
│   └── .env.example
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── main.py
│   ├── tests/
│   ├── data/
│   ├── requirements.txt
│   └── .env.example
│
├── .gitignore
└── README.md
```

## Database Design

The database is organized around two primary entities: `hosted_zones` and `dns_records`.

### 1. Hosted Zones — `hosted_zones`

Stores the metadata associated with each hosted zone.

| Field | Description |
|---|---|
| ID | Primary key |
| Name | Hosted zone name |
| Type | Public or private |
| Description | Optional resource description |
| Zone ID | Generated Route 53-style identifier |
| Owner | Resource ownership information |
| Record count | Number of associated DNS records |
| Created at | Resource creation timestamp |
| Updated at | Most recent update timestamp |

### 2. DNS Records — `dns_records`

Stores the DNS records associated with each hosted zone.

| Field | Description |
|---|---|
| ID | Primary key |
| Hosted zone ID | Foreign key referencing `hosted_zones` |
| Name | DNS record name |
| Type | A, AAAA, CNAME, TXT, MX, NS, PTR, SRV, or CAA |
| TTL | Time to live |
| Value | Record value |
| Structured fields | Type-specific MX, SRV, and CAA attributes |
| Comment | Optional record description |
| Created at | Resource creation timestamp |
| Updated at | Most recent update timestamp |

### Relationships and integrity

- A hosted zone can contain multiple DNS records.
- Each DNS record belongs to a hosted zone through a foreign key.
- SQLAlchemy relationships maintain consistency between parent and child resources.
- Cascade deletion removes associated records when a hosted zone is deleted.
- Validation rules ensure that record fields conform to the selected DNS type.

## REST API Reference

The backend exposes a REST API under the `/api` prefix.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Authenticate a user |
| GET | `/api/auth/me` | Retrieve the current session user |
| POST | `/api/auth/logout` | End the current session |

### Hosted Zones

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/hosted-zones` | List hosted zones |
| GET | `/api/hosted-zones/{id}` | Retrieve a hosted zone |
| POST | `/api/hosted-zones` | Create a hosted zone |
| PUT | `/api/hosted-zones/{id}` | Update a hosted zone |
| DELETE | `/api/hosted-zones/{id}` | Delete a hosted zone |

Supported listing parameters include `search`, `page`, and `page_size`.

### DNS Records

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/hosted-zones/{id}/records` | List records in a hosted zone |
| GET | `/api/hosted-zones/{id}/records/{record_id}` | Retrieve a DNS record |
| POST | `/api/hosted-zones/{id}/records` | Create a DNS record |
| PUT | `/api/hosted-zones/{id}/records/{record_id}` | Update a DNS record |
| DELETE | `/api/hosted-zones/{id}/records/{record_id}` | Delete a DNS record |

The records listing supports `search`, `type`, `page`, and `page_size`.

### API documentation

FastAPI automatically provides interactive API documentation.

- **Swagger UI:** `https://YOUR-BACKEND-HOST/docs`
- **OpenAPI schema:** `https://YOUR-BACKEND-HOST/openapi.json`
- **Health check:** `https://YOUR-BACKEND-HOST/health`

Replace `YOUR-BACKEND-HOST` with the deployed backend hostname.

## Getting Started

### Prerequisites

Install the following tools:

- Python 3.11 or newer
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/AkshatBhatnagar29/ScalerAI-submission-Akshat.git
cd ScalerAI-submission-Akshat
```

### 2. Configure the backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux or macOS:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create the environment file from the example:

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Linux or macOS:**

```bash
cp .env.example .env
```

Configure the required environment variables in `backend/.env`:

```env
MOCK_USERNAME=admin
MOCK_PASSWORD=admin123
FRONTEND_ORIGIN=http://localhost:3000
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
SESSION_SECRET=replace-with-a-long-random-secret
DATABASE_URL=sqlite:///./data/route53.db
```

Use a unique secret for `SESSION_SECRET`. Keep `.env` files out of version control.

Start the backend:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`.

### 3. Configure the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Create the frontend environment file.

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env.local
```

**Linux or macOS:**

```bash
cp .env.example .env.local
```

For local development, leave `NEXT_PUBLIC_API_BASE_URL` empty and configure the server-side proxy target in `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=
BACKEND_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### 4. Sign in

Use the development credentials:

```text
Username: admin
Password: admin123
```

You can then create a hosted zone and manage its DNS records through the interface.

## Configuration Reference

### Backend environment variables

| Variable | Purpose |
|---|---|
| `MOCK_USERNAME` | Mock authentication username |
| `MOCK_PASSWORD` | Mock authentication password |
| `FRONTEND_ORIGIN` | Allowed frontend origin for CORS |
| `COOKIE_SECURE` | Enables the Secure cookie attribute |
| `COOKIE_SAMESITE` | Controls cookie SameSite behavior |
| `SESSION_SECRET` | Secret used by the session/security configuration |
| `DATABASE_URL` | SQLAlchemy database connection URL |

### Frontend environment variables

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Optional browser-facing API base URL |
| `BACKEND_API_URL` | Backend target for the Next.js `/api` rewrite proxy |

When using the Next.js proxy, leave `NEXT_PUBLIC_API_BASE_URL` empty and set `BACKEND_API_URL` to the reachable backend URL.

For production, configure environment variables in the relevant hosting provider's settings instead of committing local environment files.

## Testing

### Backend tests

From the backend directory, activate the Python environment and run:

```bash
pytest
```

The test suite covers the implemented API workflows, including authentication, hosted zone CRUD, search and pagination, DNS record operations, record-type validation, ownership checks, filtering, and cascade deletion.

### Frontend production build

From the frontend directory:

```bash
npm run build
```

To run the production build locally:

```bash
npm run start
```

### Manual verification checklist

- [ ] Sign in and sign out.
- [ ] Refresh the application and verify authentication behavior.
- [ ] Create, edit, search, and delete hosted zones.
- [ ] Open a hosted zone and manage its DNS records.
- [ ] Test the supported DNS record types.
- [ ] Verify record search, type filters, and pagination.
- [ ] Confirm that deleting a hosted zone removes its associated records.
- [ ] Restart the backend and verify that previously stored data remains available.
- [ ] Verify the frontend production build and deployed API connectivity.

## Deployment

The application uses a separately hosted frontend and backend.

### Frontend — Vercel

Production demo:

[https://scaler-ai-submission-akshat.vercel.app/](https://scaler-ai-submission-akshat.vercel.app/)

The frontend can be deployed through the Vercel Git integration by importing the repository and setting the project root directory to `frontend`.

Configure the frontend environment variables for the production deployment. When using the Next.js rewrite proxy, set `BACKEND_API_URL` to the public HTTPS backend URL and leave `NEXT_PUBLIC_API_BASE_URL` empty.

### Backend — AWS Lightsail

The FastAPI backend runs on an Ubuntu instance with Uvicorn managed by systemd and Nginx handling incoming web traffic and HTTPS.

For deployment:

1. Install Python and the backend dependencies.
2. Configure the backend `.env` file.
3. Configure Nginx to forward requests to the FastAPI application.
4. Configure HTTPS and the frontend origin.
5. Start and enable the backend systemd service.
6. Configure a persistent location for the SQLite database.
7. Verify the health endpoint, authentication, and resource APIs.

The SQLite database path is controlled by `DATABASE_URL`. Keep the database on persistent storage and back it up before deployments or database migrations.

### Production verification

After deployment, verify:

- The live frontend loads successfully.
- The backend health endpoint returns a successful response.
- Authentication works across page refreshes.
- Hosted zones and DNS records can be created and retrieved.
- Existing resources remain available after a backend restart.
- HTTPS, cookies, CORS, and frontend-to-backend routing are configured correctly.

## Design Principles

The project emphasizes the following engineering principles:

- **Separation of concerns:** API routes, business logic, data access, and frontend rendering are organized into distinct layers.
- **Typed interfaces:** TypeScript and Pydantic provide structured contracts for application data.
- **Data integrity:** Relational constraints and ORM relationships keep hosted zones and DNS records consistent.
- **Reusable UI:** Shared components maintain consistent navigation, forms, tables, and notifications.
- **Configuration-driven deployment:** Environment variables allow the application to run in local and hosted environments.
- **Maintainability:** A modular project structure makes future functionality easier to extend.

## Future Enhancements

The architecture can be extended with additional Route 53-inspired capabilities, including:

- BIND zone file import and export.
- JSON resource export.
- Bulk DNS record operations.
- Keyboard shortcuts.
- Theme preferences.
- Additional DNS validation and resource-management workflows.

## License

This project was developed as a Route 53-inspired full-stack application. Add a `LICENSE` file if you intend to distribute the repository under a specific open-source license.

---

<p align="center">
  <strong>AWS Route 53 Clone</strong>
  <br />
  Built with Next.js, TypeScript, FastAPI, and SQLite.
  <br /><br />
  <a href="https://scaler-ai-submission-akshat.vercel.app/">View Live Demo</a>
</p>
