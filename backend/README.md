# Outrelis backend

FastAPI backend with PostgreSQL and email/password account authentication.
Gmail mailbox authorization is a separate, unimplemented feature.

Run these commands from `backend/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
alembic upgrade head
fastapi dev app/main.py
```

`requirements.txt` pins the installed dependencies for repeatable setup.
Direct project dependencies are declared in `pyproject.toml`.

- Interactive documentation: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Authentication API

| Method | Path | Behavior |
|---|---|---|
| POST | `/api/v1/auth/register` | Create an account; returns public user fields (201) |
| POST | `/api/v1/auth/login` | Verify credentials; return session token and user |
| GET | `/api/v1/auth/me` | Return the authenticated user |
| POST | `/api/v1/auth/logout` | Revoke the current session (204) |

Registration accepts JSON:

```json
{
  "full_name": "Mouad Example",
  "email": "owner@example.com",
  "password": "a long private passphrase"
}
```

Login accepts only `email` and `password`. Registration requires `full_name`
(1–100 characters after trimming surrounding whitespace). Single-word names and
international characters are supported. Registration, login, and `/me` user
responses include `full_name`. Accounts created before the name migration keep
`null` until a future profile update; existing accounts and sessions are preserved.

Emails are trimmed and lowercased; passwords are preserved exactly. New passwords
must contain 15–128 characters. Passwords use Argon2id hashes, and validation
responses omit submitted values. Registration does not automatically log in.
Duplicate registration returns 409; incorrect login and unknown email return the
same 401 response.

Login returns `access_token`, `token_type`, `expires_in`, and `user`. This is an
opaque random session token, not a JWT. Send it on protected requests:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

In Swagger `/docs`, log in, copy `access_token`, click **Authorize**, and paste
the token. Then try `/me` and `/logout`. No real accounts are seeded automatically.

Only a SHA-256 digest of the token is stored in PostgreSQL. Sessions expire after
24 hours by default and logout revokes the current session immediately. Other
sessions remain valid. Inactive users cannot log in or use existing sessions.
There is no refresh-token endpoint; users log in again after expiry. When wiring
React, keep the bearer token in memory; persistent browser sessions need a deliberate
cookie/CSRF design rather than storing tokens in localStorage.

The API permits the two configured local Vite origins. `CORS_ORIGINS` is a JSON
array. It does not grant database access or replace authentication.

PostgreSQL-backed fixed-minute limits apply across API processes: 10 registration
attempts per IP, 30 login attempts per IP, and 10 login attempts per email.
They count successful and unsuccessful requests with valid input. Exceeding a
limit returns 429 with `Retry-After`. Proxy deployment must configure trusted
forwarding correctly; never blindly trust a client-supplied IP header. Additional
edge-level limits are needed before public exposure.

This is the local account-authentication foundation. Email verification, password
reset/change, session-management UI, and workspace authorization are not implemented.
These are separate next steps before a public product launch. Use HTTPS outside
local development, protect `.env`, and never log passwords or authorization headers.

## Local database

The existing `postgres-dev` Docker container hosts `outrelis_db` on
`127.0.0.1:5432`, owned by the dedicated `outrelis_app` login.

The connection URL is stored in the ignored `backend/.env`. For another machine,
copy `.env.example` to `.env` and supply the password after provisioning PostgreSQL.
Do not commit `.env`.

`app/config.py` loads backend configuration independently of the working directory.
`app/db.py` provides a SQLAlchemy engine and a request-scoped session dependency.
Database writes must explicitly commit; closing a session does not commit changes.
No tables are created automatically at application startup. Run `alembic upgrade
head` to create `users`, `auth_sessions`, `auth_rate_limits`, and Alembic's version
table. This migration history applies to `outrelis_db`, not the archived
`leadmap_db` schema. Never apply the new history to the legacy database.

## Tests

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

Tests require the configured PostgreSQL connection and permission to create a
schema. They migrate a randomly named temporary schema, roll back each test's
data, verify migration downgrade, then drop that schema. They do not reset or
populate the public schema or the legacy database. Test dependencies are declared
in the `dev` extra; `requirements.txt` pins the current development environment.
