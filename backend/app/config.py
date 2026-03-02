# ─────────────────────────────────────────────
# app/config.py  –  Application configuration
# ─────────────────────────────────────────────
#
# These values control how JWT tokens are created and validated.
# In a real project you would load SECRET_KEY from an environment
# variable (e.g. .env file) so it is never committed to git.

# The secret key is used to SIGN tokens so nobody can tamper with them.
# Change this to a long, random string in production!
SECRET_KEY = "change-me-to-a-very-long-random-secret-key"

# The algorithm used to sign / verify the token.
# HS256 = HMAC with SHA-256 – the most common choice for JWTs.
ALGORITHM = "HS256"

# How many minutes until a login token expires.
# After this time the user must log in again.
ACCESS_TOKEN_EXPIRE_MINUTES = 30
