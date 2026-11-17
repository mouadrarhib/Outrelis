# Technology Stack and Backend Architecture

Updated: 14 November 2026.

**Status: planning only. This document does not authorize implementation, installation or deployment.**

The active frontend is a React + TypeScript + Vite starter. The old Python/Streamlit
prototype is archived in `archive/legacy-prototype/`. FastAPI, the job queue and
the credit system below remain planned components, not delivered functionality.
The chosen Maps discovery direction is our own collector without the Google
Places API or a paid third-party collection API; the collector is not implemented.

Related plans: [V1](product-v1.md), [V2](product-v2.md), and
[feature comparison](product-feature-roadmap.md).

## Decisions and proposals

| Area | Decision / proposal | Status |
|---|---|---|
| Frontend | React + TypeScript + Vite | Planned frontend direction |
| Components | beUI | User-selected |
| Styling | Tailwind CSS, following beUI requirements | Planned supporting technology |
| Custom animations | GSAP + `@gsap/react` | User-selected GSAP; React integration recommended |
| Component animations | Motion where required by beUI | Supporting dependency |
| Local database | PostgreSQL running in Docker | User-selected; existing local setup |
| Production database | Supabase PostgreSQL | User-selected |
| MVP backend | Python + FastAPI | Planned backend direction |
| Database access/migrations | SQLAlchemy + Alembic | Retain existing tools |
| Authentication | FastAPI email/password accounts with PostgreSQL-backed bearer sessions | Local foundation implemented; Gmail OAuth is separate |
| Background processing | RQ + Redis | Recommended initial queue; not installed |
| Frontend hosting | Cloudflare Pages | Recommended for the waitlist and static React build |
| Python hosting | Provider to be selected before hosted beta | Open decision |
| Backend structure | Feature-based modular monolith with explicit layers | Recommended architecture |

Exact runtime and package versions will be pinned after a compatibility check at
implementation time. beUI currently documents React 19, Tailwind CSS 4 and Motion
as its foundation; check the dependencies of each selected component rather than
installing an entire catalogue.

## Stage 1 — Waitlist

### Stack

| Layer | Choice | Responsibility |
|---|---|---|
| Frontend | React + TypeScript + Vite | Landing page and signup form |
| Components/styling | beUI + Tailwind CSS | Consistent, responsive interface |
| Animation | GSAP + `@gsap/react`; Motion inside beUI components | Selected transitions, sequences and component feedback |
| Signup storage | Supabase PostgreSQL | Registration records and future beta eligibility |
| Data access | Supabase JavaScript client | Submit registrations under restricted database permissions |
| Hosting | Cloudflare Pages | Serve the frontend |
| Administration | Supabase Dashboard | Review registrations without building an admin app |
| Optional server-side form handling | Supabase Edge Function | CAPTCHA verification, rate limiting or confirmation-email integration if needed |

No separate Python server, Redis or research worker is needed for this stage.
Supabase supplies the managed backend; “no custom backend server” does not mean
that browser-side validation is the security boundary.

### Signup handling

- Use only the Supabase publishable key in browser code. Database credentials,
  service-role keys and other secrets must stay server-side.
- Restrict public access to the intended submission operation using grants and
  row-level security. Public visitors must not read, update or delete the list.
- Validate and constrain data in the database; normalize email addresses and
  enforce duplicate handling there as well as in the form.
- Keep administrative fields such as approval status and credit eligibility
  outside visitor-controlled writes.
- Store only the information needed for the waitlist: email, optional role/target
  market, acquisition source, signup time and the relevant consent record.
- If using CAPTCHA, verify its token server-side; a frontend widget alone is not
  sufficient. An Edge Function can provide this boundary without hosting FastAPI.
- Record eligibility for the promised future beta bonus. Do not create a live
  spendable wallet merely because someone joins the waitlist.

## Stage 2 — Customer-Facing MVP / V1

| Layer | Choice | Responsibility |
|---|---|---|
| Frontend | Same React stack as the waitlist | Search, leads, evidence, credits, jobs and settings |
| API | Python + FastAPI | Authorization, validation and business operations |
| Request/response schemas | Pydantic | Explicit API contracts |
| Configuration | Pydantic Settings | Environment-specific settings and secrets |
| Database | Docker PostgreSQL locally; Supabase PostgreSQL hosted | Durable application records |
| ORM | SQLAlchemy | Models, queries and explicit transactions |
| Migrations | Alembic | Versioned schema changes |
| Identity | FastAPI email/password accounts | Argon2id passwords and revocable sessions; workspace authorization is a later step |
| Job queue | RQ + Redis, proposed | Dispatch and retry long-running work |
| Worker | Separate Python process from the same codebase | Searches, crawling, enrichment and audits |
| Public website research | Existing httpx + BeautifulSoup services | Fetch and extract from public pages |
| Selective browser rendering | Evaluate later if measured failures justify it | Handle websites requiring JavaScript |
| Local orchestration | Docker Compose | PostgreSQL, Redis, API, worker and frontend development services |

### Application flow

```text
React frontend
    → FastAPI API
        → Business services
            → SQLAlchemy → PostgreSQL / Supabase
            → Queue → Python worker → External providers
```

The worker calls the same business services as the API. It is a separate process,
not a separate microservice or a second copy of the business logic.

### Responsibility boundaries

- PostgreSQL is authoritative for accounts, workspace membership, credit grants,
  reservations, transactions and durable job state. Redis is queue infrastructure,
  not the authority for spendable credits.
- The backend validates its own account sessions. Workspace authorization must
  be added before workspace-scoped features; a client-supplied workspace ID is
  not proof of access. Supabase is the planned production PostgreSQL host.
- All credit grants, reservations, charges and privileged data operations go
  through controlled server-side operations. React never decides its own balance.
- Keep provider credentials and privileged database access out of browser bundles.
- Persist results and their related charges atomically. Provider calls should not
  hold long database locks. Coordinate job dispatch and durable records with
  explicit failure/recovery behavior.

## Backend Architecture

### Recommended style

**A modular monolith organized by feature, with clear layers inside each module.**

FastAPI supports routers and dependency injection but does not mandate this
particular folder structure. This is our recommendation for a maintainable first
Python API, especially for a developer familiar with Spring Boot.

### Spring Boot mapping

| Spring Boot concept | FastAPI/Python equivalent |
|---|---|
| `@RestController` | `APIRouter` and endpoint functions |
| Request/response DTO | Pydantic schema |
| `@Service` | Explicit service class or function |
| Spring Data repository | Repository/query functions using SQLAlchemy |
| JPA entity | SQLAlchemy model |
| Dependency injection | `Depends()` at the API boundary and explicit service arguments |
| `@Transactional` | Explicit SQLAlchemy transaction boundary |
| `@ControllerAdvice` | Registered exception handlers |
| Flyway/Liquibase | Alembic |
| Configuration properties | Pydantic Settings |

FastAPI does not automatically reproduce Spring's service container or transaction
behavior. Those responsibilities must be designed explicitly.

### Proposed structure

```text
backend/
├── pyproject.toml
├── migrations/
├── src/
│   └── leadmap/
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   ├── security.py
│       │   ├── logging.py
│       │   └── exception_handlers.py
│       ├── db/
│       │   ├── base.py
│       │   └── session.py
│       ├── modules/
│       │   ├── leads/
│       │   │   ├── router.py
│       │   │   ├── schemas.py
│       │   │   ├── models.py
│       │   │   ├── service.py
│       │   │   └── repository.py
│       │   ├── searches/
│       │   ├── contacts/
│       │   ├── credits/
│       │   └── workspaces/
│       ├── integrations/
│       │   ├── google_places.py
│       │   ├── website_crawler.py
│       │   └── supabase_auth.py
│       └── workers/
│           ├── queue.py
│           └── tasks.py
└── tests/
    ├── unit/
    ├── integration/
    └── api/
```

Create files as the corresponding features need them. This tree is not a request
to generate empty modules or rewrite the working prototype immediately.

### Layer rules

| Layer | Owns | Keep outside it |
|---|---|---|
| Router | HTTP schemas, dependencies, response/status mapping | Crawling, balance arithmetic and complex queries |
| Service | Business rules and operation/transaction boundaries | FastAPI-specific request objects and HTTP exceptions |
| Repository | Database queries and persistence operations | Independent commits that break a larger operation |
| Integration adapter | Provider calls, response translation, provider errors | Deciding permissions or directly changing credit balances |
| Worker task | Dispatch context, execution and retry coordination | Duplicated business rules or shared global database sessions |

Keep request/response schemas separate from ORM models. Map business exceptions to
consistent API errors centrally. Scope queries to authorized workspaces and pass
dependencies explicitly. Reuse concrete services before introducing generic base
classes, interfaces, factories or additional architecture layers.

### Sync and async

Start with synchronous SQLAlchemy and ordinary `def` endpoints for blocking work.
Run long research jobs in workers. Introduce async selectively where libraries and
the measured workload justify it; `async def` does not make a blocking call
non-blocking. Use a separate database session per request/task and do not share it
across concurrent threads or tasks.

## Database Environments

| Environment | Database | Configuration |
|---|---|---|
| Local development | PostgreSQL in Docker | Local `DATABASE_URL` |
| Hosted MVP | Supabase PostgreSQL | Server-side hosted `DATABASE_URL` |
| Automated integration tests | Isolated disposable PostgreSQL database/schema | Dedicated test credentials/configuration |

Use the same application migrations in development and production. Test migration
upgrades before applying them to production; do not run schema creation on every
API request or let multiple workers race to migrate the database.

Plain PostgreSQL does not reproduce Supabase Auth, Storage or every platform
policy. Use the Supabase local stack or a separate test project for those
integration tests. Production data and credentials must not be used by tests.

Use Supabase's appropriate direct/pooler connection settings for each workload;
confirm SQLAlchemy pooling and migration connection requirements when deployment
is selected. Direct server connections and browser Data API access have different
security contexts: never assume browser RLS alone protects privileged backend
queries.

## Animation and Interface Rules

- beUI supplies selected components; Tailwind CSS supplies styling and tokens.
- Motion handles animations already authored inside beUI components.
- GSAP handles deliberate custom sequences and scroll effects, using
  `@gsap/react` for scoped lifecycle cleanup.
- Do not let GSAP and Motion control the same animated properties on the same
  element concurrently.
- Respect reduced-motion preferences, keyboard interaction and loading/error
  states. Dashboard motion should explain state rather than delay tasks.
- Check the license of each chosen asset/component; beUI's public library and Pro
  catalogue have separate terms.

## Documentation, Tests and Clean Code

| Need | Recommended tool / practice | Artifact |
|---|---|---|
| API documentation | FastAPI OpenAPI, typed schemas, descriptions and examples | Swagger UI, OpenAPI schema and response/error contracts |
| Written documentation | Markdown under `docs/` | Setup, architecture, credit rules, provider behavior and deployment notes |
| Backend tests | pytest + TestClient/httpx | Unit, API and integration results |
| Coverage | coverage.py | HTML/XML coverage reports; not a substitute for behavioral tests |
| Test evidence | pytest JUnit XML and CI artifacts | Pass/fail history, failure details and relevant logs |
| Formatting/linting | Ruff | Consistent formatting/imports and common error checks |
| Type checking | mypy | Checked application/service boundaries |
| CI | GitHub Actions | Checks on pull requests |
| Frontend workflow tests | Browser-based end-to-end tests; runner to select | User-flow checks and failure screenshots/videos |

### Critical test areas

- Extraction, normalization, scoring and business-rule edge cases.
- API input validation, authorization, pagination and consistent errors.
- Workspace isolation, including reads, writes, exports and job access.
- PostgreSQL transactions, uniqueness, concurrent spending and rollback.
- Job retry, cancellation, partial completion and idempotency.
- Migration upgrades and any Supabase-specific auth/RLS behavior.

Mock external providers in normal automated tests. Keep optional live-provider
smoke tests explicit, capped and separate. Test database locks and constraints on
PostgreSQL rather than assuming SQLite reproduces them.

Keep requirements and acceptance criteria alongside each planned feature. Build
one feature at a time once implementation is explicitly authorized, and require
the relevant lint/type/test checks before considering it complete.

## Hosting Plan

| Stage/component | Proposed host | Limits / decision |
|---|---|---|
| Waitlist frontend | Cloudflare Pages | Static React hosting; stay within current free-tier quotas |
| Waitlist data | Supabase Free | Monitor database/egress quotas and inactivity pausing |
| MVP frontend | Cloudflare Pages | Same static build approach |
| MVP database | Supabase | Start within free quotas; upgrade based on actual usage/reliability needs |
| Demonstration Python service | Render Free is one evaluated option | Sleeps when idle; not the reliability target for a paid service |
| Production API, worker and Redis | Not selected | Must support the required job duration, availability, outbound access and budget |

Free frontend/database hosting does not imply free provider calls or free
always-on workers. Render/Koyeb free compute is suitable for testing with the
published restrictions, not an availability promise. Cloud Run and Railway were
also evaluated as usage-limited alternatives, not selected providers.

Hosting prices and limits change. Recheck official terms before choosing plans.
Vercel Hobby's personal/non-commercial restriction makes it unsuitable as the
default recommendation for this commercial waitlist.

## V2 Evolution

Retain the same core stack. Add only what the validated workflow requires:

- Payment integration and commercial credit/subscription administration.
- Team permissions and shared-workspace workflows.
- CRM connectors, webhooks and controlled public API access.
- Additional worker capacity, scheduling and monitoring.
- Broader website analysis or selective browser rendering.

RQ is the initial queue recommendation. Celery is an alternative to evaluate if
specific workflow/distribution needs justify it, not a mandatory V2 migration.
No microservice split is planned.

## Open Decisions

- Final public product name and first customer geography.
- Add email verification, password recovery and workspace authorization to the
  implemented email/password authentication foundation before public launch.
- Frontend form/query/table/testing utilities, chosen only as needed.
- Waitlist anti-abuse and confirmation-email requirements.
- Production API/worker/Redis host, region and budget.
- Package/runtime versions, deployment limits and monitoring/error-reporting tools.
- Source-permitted collection, display, retention and exports before research
  delivery. Technology choices do not settle those permissions.

## Primary References

- [beUI](https://beui.dev/)
- [Vite](https://vite.dev/guide/)
- [GSAP with React](https://gsap.com/resources/React/)
- [FastAPI multi-file applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI concurrency](https://fastapi.tiangolo.com/async/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy sessions](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [RQ](https://python-rq.org/)
- [Supabase API keys](https://supabase.com/docs/guides/api/api-keys)
- [Supabase row-level security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase plans](https://supabase.com/pricing)
- [Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits/)
- [Render free-service restrictions](https://render.com/docs/free)
- [Vercel terms](https://vercel.com/legal/terms)
- [Ruff](https://docs.astral.sh/ruff/)
- [mypy](https://mypy.readthedocs.io/en/stable/)
- [pytest report output](https://docs.pytest.org/en/stable/how-to/output.html)
- [coverage.py](https://coverage.readthedocs.io/en/latest/)
