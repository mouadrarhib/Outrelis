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

## Onboarding API

Both onboarding endpoints require the bearer token returned by login.

| Method | Path | Behavior |
|---|---|---|
| GET | `/api/v1/onboarding` | Read the authenticated user's onboarding state |
| PUT | `/api/v1/onboarding/starting-path` | Save or change the authenticated user's starting path |

The write endpoint accepts one of the two supported paths:

```json
{
  "starting_path": "find_first_leads"
}
```

The other accepted value is `grow_pipeline`. Repeating the request updates the
same user-owned record. The user ID always comes from the authenticated session;
the client cannot select or modify another user's onboarding record.

## Prospecting setup API

Both endpoints require authentication and always operate on the current user.

| Method | Path | Behavior |
|---|---|---|
| GET | `/api/v1/prospecting/setup` | Load the user's current offer and search draft |
| PUT | `/api/v1/prospecting/setup` | Create or replace the current prospecting setup atomically |

The write endpoint accepts 1–10 unique locations. Repeating it updates the same
default offer and current draft instead of creating duplicates.

```json
{
  "service_name": "Website design",
  "outreach_language": "en-US",
  "business_category": "Dental clinics",
  "locations": ["New York, NY", "Austin, TX"],
  "result_limit_per_location": 20
}
```

`result_limit_per_location` may be `null` or an integer from 1 through 100.
Whitespace is normalized before storage, duplicate locations are rejected
case-insensitively, and location order is preserved.

## Lead discovery API

Lead discovery is split between the FastAPI process and a separate PostgreSQL-backed
worker. API requests only queue work; they never wait for Nominatim or Overpass.

| Method | Path | Behavior |
|---|---|---|
| POST | `/api/v1/search-jobs` | Queue a search from an owned search draft |
| GET | `/api/v1/search-jobs/{job_id}` | Read job and per-location progress |
| GET | `/api/v1/search-jobs/{job_id}/leads` | Read paginated, deduplicated results |

Queue a search with:

```json
{
  "search_draft_id": "YOUR_SEARCH_DRAFT_UUID"
}
```

Run one API process and one worker process in separate terminals:

```bash
fastapi dev app/main.py
python -m app.features.discovery.worker
```

The worker checks the location cache, resolves cache misses through Nominatim,
queries Overpass, normalizes businesses, deduplicates by provider identity, domain,
phone, and business similarity, and records source provenance. Configure a real,
contactable `OSM_USER_AGENT` before using the public services. Tests inject fake
providers and never make network requests.

## Error responses

Expected application failures use typed exceptions handled in one global place.
Responses retain the standard `detail` field and also include a stable,
machine-readable `code`, for example:

```json
{
  "detail": "An account with this email already exists",
  "code": "email_already_registered"
}
```

The shared cases cover bad requests, authentication, forbidden access, missing
resources, conflicts, and rate limits. Validation errors use `validation_error`
and omit submitted values. Unexpected application and database failures are
logged server-side and return a generic message without exposing internals.

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
must contain 8–128 characters. Passwords use Argon2id hashes, and validation
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
head` to create the authentication tables, `user_onboarding`, `offer_profiles`,
`search_drafts`, `search_draft_locations`, `search_jobs`, `search_job_locations`,
`geocoded_locations`, `businesses`, `business_sources`, `search_job_leads`, and
Alembic's version table. This
migration history applies to `outrelis_db`, not the archived
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
