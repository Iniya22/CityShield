# CityShield 🏛️

**Zero-trust security architecture for smart urban infrastructure**

CityShield provides a modular, centralized protection layer for critical city APIs. Every request is verified, monitored, and logged before reaching infrastructure data.

## Current Use Case

**Urban Water Supply Department** — Manages pipelines, water tanks, and maintenance activities through secure RESTful APIs.

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Frontend   │───▶│  Security Layer  │───▶│   Data Services  │
│  (React UI)  │    │  JWT · RBAC ·    │    │  FastAPI + SQLite │
│              │    │  Audit Logging   │    │                  │
└─────────────┘    └──────────────────┘    └──────────────────┘
```

## Quick Start

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python -m app.seed_data        # seed demo data
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Login
Open `http://localhost:5173` and use one of:

| Username   | Password  | Role     |
|-----------|-----------|----------|
| admin      | admin123  | Admin    |
| operator1  | oper123   | Operator |
| viewer1    | view123   | Viewer   |

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Security:** JWT (python-jose), bcrypt, RBAC middleware, audit logging
- **Frontend:** React (Vite), vanilla CSS

## Team Roles

| Module | Owner |
|--------|-------|
| Data Services (`backend/app/`) | Member 2 |
| Security Layer (`backend/security/`) | Member 1 |
| Frontend UI (`frontend/`) | Member 3 |

## License

MIT
