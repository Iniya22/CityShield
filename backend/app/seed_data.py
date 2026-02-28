"""
CityShield – Seed Data
Populates the database with demo data for development / demonstration
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import User, Pipeline, WaterTank, MaintenanceLog, AuditLog
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Skip if already seeded
    if db.query(User).first():
        print("Database already seeded – skipping.")
        db.close()
        return

    # ── Users ────────────────────────────────────────────────────────────
    users = [
        User(username="admin", email="admin@cityshield.gov",
             hashed_password=pwd.hash("admin123"), full_name="System Admin",
             role="admin"),
        User(username="operator1", email="operator1@cityshield.gov",
             hashed_password=pwd.hash("oper123"), full_name="Ravi Kumar",
             role="operator"),
        User(username="viewer1", email="viewer1@cityshield.gov",
             hashed_password=pwd.hash("view123"), full_name="Priya Sharma",
             role="viewer"),
    ]
    db.add_all(users)
    db.commit()
    print(f"  ✓ {len(users)} users created")

    # ── Pipelines ────────────────────────────────────────────────────────
    zones = ["North", "South", "East", "West", "Central"]
    materials = ["PVC", "HDPE", "Cast Iron", "Ductile Iron", "Steel"]
    statuses = ["active", "active", "active", "maintenance", "critical", "inactive"]

    pipelines = []
    for i in range(1, 9):
        pipelines.append(Pipeline(
            name=f"Pipeline-{zones[(i-1)%5]}-{i:03d}",
            zone=zones[(i-1) % 5],
            material=materials[(i-1) % 5],
            diameter_mm=random.choice([100, 150, 200, 300, 450, 600]),
            length_km=round(random.uniform(0.5, 12.0), 2),
            status=statuses[(i-1) % len(statuses)],
            installed_date=f"20{random.randint(10,22)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            last_inspection=f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        ))
    db.add_all(pipelines)
    db.commit()
    print(f"  ✓ {len(pipelines)} pipelines created")

    # ── Water Tanks ──────────────────────────────────────────────────────
    tank_types = ["overhead", "underground", "ground-level"]
    tanks = []
    for i in range(1, 7):
        tanks.append(WaterTank(
            name=f"Tank-{zones[(i-1)%5]}-{i:02d}",
            zone=zones[(i-1) % 5],
            capacity_liters=random.choice([50000, 100000, 200000, 500000, 1000000]),
            current_level_pct=round(random.uniform(15, 95), 1),
            status=statuses[(i-1) % len(statuses)],
            tank_type=tank_types[(i-1) % 3],
            last_cleaned=f"2025-{random.randint(1,6):02d}-{random.randint(1,28):02d}",
            last_inspection=f"2025-{random.randint(7,12):02d}-{random.randint(1,28):02d}"
        ))
    db.add_all(tanks)
    db.commit()
    print(f"  ✓ {len(tanks)} water tanks created")

    # ── Maintenance Logs ─────────────────────────────────────────────────
    descriptions = [
        "Leak detected at joint section",
        "Routine pressure test completed",
        "Valve replacement scheduled",
        "Corrosion observed on outer surface",
        "Water quality test – chlorine level low",
        "Pump motor overheating",
        "Sediment buildup in tank floor",
        "SCADA sensor malfunction",
        "Emergency pipe burst repair",
        "Scheduled cleaning of filtration unit",
    ]
    priorities = ["low", "medium", "medium", "high", "critical"]
    maint_statuses = ["open", "open", "in_progress", "resolved"]

    logs = []
    for i in range(10):
        asset_type = random.choice(["pipeline", "tank"])
        asset_id = random.randint(1, 8) if asset_type == "pipeline" else random.randint(1, 6)
        s = maint_statuses[i % len(maint_statuses)]
        logs.append(MaintenanceLog(
            asset_type=asset_type,
            asset_id=asset_id,
            asset_name=f"{'Pipeline' if asset_type == 'pipeline' else 'Tank'}-{asset_id}",
            description=descriptions[i],
            priority=priorities[i % len(priorities)],
            status=s,
            assigned_to=random.choice(["Ravi Kumar", "Amit Patel", "Sunita Verma"]),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            resolved_at=(datetime.utcnow() - timedelta(days=random.randint(0, 5))) if s == "resolved" else None
        ))
    db.add_all(logs)
    db.commit()
    print(f"  ✓ {len(logs)} maintenance logs created")

    # ── Audit Logs ───────────────────────────────────────────────────────
    actions = ["GET", "POST", "PUT", "DELETE", "GET", "GET", "POST"]
    resources = [
        "/api/pipelines", "/api/tanks", "/api/maintenance",
        "/api/auth/login", "/api/dashboard", "/api/pipelines/3"
    ]
    audit_entries = []
    for i in range(15):
        audit_entries.append(AuditLog(
            user=random.choice(["admin", "operator1", "viewer1", "anonymous"]),
            action=actions[i % len(actions)],
            resource=resources[i % len(resources)],
            detail=f"status=200 latency={round(random.uniform(0.01, 0.5), 3)}s",
            ip_address=f"192.168.1.{random.randint(10, 250)}",
            risk_score=round(random.uniform(0, 0.6), 2),
            timestamp=datetime.utcnow() - timedelta(hours=random.randint(0, 72))
        ))
    db.add_all(audit_entries)
    db.commit()
    print(f"  ✓ {len(audit_entries)} audit log entries created")

    db.close()
    print("\n✅ Database seeded successfully!")


if __name__ == "__main__":
    seed()
