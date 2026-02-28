"""
CityShield – Audit Logger
Writes every security-relevant event to the audit_logs table
"""

from sqlalchemy.orm import Session
from app.models import AuditLog
from datetime import datetime


def log_event(db: Session, user: str, action: str, resource: str,
              detail: str = None, ip_address: str = None,
              risk_score: float = 0.0):
    """
    Record a security event in the audit trail.

    Parameters
    ----------
    user       : username or "anonymous"
    action     : HTTP method (GET, POST, PUT, DELETE) or custom action
    resource   : endpoint path or resource identifier
    detail     : human-readable description of the event
    ip_address : client IP
    risk_score : 0.0 (benign) – 1.0 (highly suspicious)
    """
    entry = AuditLog(
        user=user,
        action=action,
        resource=resource,
        detail=detail,
        ip_address=ip_address,
        risk_score=risk_score,
        timestamp=datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    return entry
