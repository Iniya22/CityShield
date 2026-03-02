# app/database.py
# ───────────────────────────────────────────────────────────
# In-memory "database" for the CityShield demo.
#
# Pre-seeded with three demo users — one per role — so the
# demo works immediately without having to register first.
#
# Passwords are hashed with pbkdf2_sha256 (same scheme used
# by auth.py) so login works exactly like a real user would.
# ───────────────────────────────────────────────────────────

from passlib.context import CryptContext

# Use the same hashing algorithm as auth.py
_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# ── Demo users ────────────────────────────────────────────
# These are created once when the module is imported.
# The database is reset every time the server restarts
# (no persistence – this is a demo prototype).
#
# Credentials for quick testing:
#   admin     / Admin@123      → role: admin
#   engineer1 / Engineer@123   → role: engineer
#   viewer1   / Viewer@123     → role: viewer
fake_users_db = {
    "admin": {
        "username": "admin",
        "email":    "admin@cityshield.com",
        "hashed_password": _pwd.hash("Admin@123"),
        "role": "admin",
    },
    "engineer1": {
        "username": "engineer1",
        "email":    "engineer@cityshield.com",
        "hashed_password": _pwd.hash("Engineer@123"),
        "role": "engineer",
    },
    "viewer1": {
        "username": "viewer1",
        "email":    "viewer@cityshield.com",
        "hashed_password": _pwd.hash("Viewer@123"),
        "role": "viewer",
    },
}