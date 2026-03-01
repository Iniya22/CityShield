# CityShield API Specification

Base URL: `http://localhost:8000`

## Authentication

### POST `/api/auth/login`
Login and receive a JWT.

**Request:**
```json
{ "username": "admin", "password": "admin123" }
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "admin",
  "username": "admin"
}
```

### POST `/api/auth/register`
Register a new user.

### GET `/api/auth/me`
Get the authenticated user's profile. Requires Bearer token.

---

## Pipelines

All endpoints require Bearer token.

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/api/pipelines` | admin, operator, viewer | List all pipelines |
| GET | `/api/pipelines/{id}` | admin, operator, viewer | Get one pipeline |
| POST | `/api/pipelines` | admin, operator | Create a pipeline |
| PUT | `/api/pipelines/{id}` | admin, operator | Update a pipeline |
| DELETE | `/api/pipelines/{id}` | admin | Delete a pipeline |

---

## Water Tanks

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/api/tanks` | admin, operator, viewer | List all tanks |
| GET | `/api/tanks/{id}` | admin, operator, viewer | Get one tank |
| POST | `/api/tanks` | admin, operator | Create a tank |
| PUT | `/api/tanks/{id}` | admin, operator | Update a tank |
| DELETE | `/api/tanks/{id}` | admin | Delete a tank |

---

## Maintenance Logs

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/api/maintenance` | admin, operator, viewer | List logs |
| GET | `/api/maintenance/{id}` | admin, operator, viewer | Get one log |
| POST | `/api/maintenance` | admin, operator | Create log |
| PUT | `/api/maintenance/{id}` | admin, operator | Update log |
| DELETE | `/api/maintenance/{id}` | admin | Delete log |

---

## Dashboard

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/api/dashboard` | admin, operator, viewer | Aggregated stats |

---

## Audit Log

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/api/audit` | admin | Security event trail |

---

## Health Check

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/health` | None | Service status |
