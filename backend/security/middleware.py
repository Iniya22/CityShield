"""
CityShield – Security Middleware
Logs every request to the audit trail and performs basic anomaly detection
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import SessionLocal
from security.audit_logger import log_event


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that intercepts every request, measures latency, detects
    basic anomalies, and writes an audit log entry.
    """

    # Paths that should not be logged (health checks, static assets)
    SKIP_PATHS = {"/docs", "/openapi.json", "/redoc", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next):
        # Skip non-API paths
        if request.url.path in self.SKIP_PATHS or request.url.path.startswith("/static"):
            return await call_next(request)

        start = time.time()
        response = await call_next(request)
        duration = time.time() - start

        # Determine user from state (set by auth) or fall back to "anonymous"
        user = getattr(request.state, "user", None)
        username = user.username if user else "anonymous"

        # Basic anomaly scoring
        risk = self._compute_risk(request, response, duration)

        # Log to DB (fire-and-forget style in a new session)
        try:
            db = SessionLocal()
            log_event(
                db=db,
                user=username,
                action=request.method,
                resource=request.url.path,
                detail=f"status={response.status_code} latency={duration:.3f}s",
                ip_address=request.client.host if request.client else None,
                risk_score=risk
            )
            db.close()
        except Exception:
            pass    # audit logging should never break the request

        return response

    @staticmethod
    def _compute_risk(request: Request, response, duration: float) -> float:
        """
        Simple heuristic anomaly scoring:
        - 401/403 responses raise the score
        - Very slow requests raise the score
        - DELETE operations get a baseline bump
        """
        score = 0.0
        if response.status_code in (401, 403):
            score += 0.5
        if response.status_code >= 500:
            score += 0.3
        if duration > 5.0:
            score += 0.2
        if request.method == "DELETE":
            score += 0.1
        return min(score, 1.0)
