# Outrelis

Your first leads. Your next opportunities.

Outrelis is a planned workspace for discovering local-business prospects,
organizing leads, and preparing personalized outreach.

## Current development

The React + TypeScript + Vite starter is in `frontend/`. FastAPI has not been
initialized, and the new Maps collector has not been implemented.

```bash
cd frontend
npm install
npm run dev
```

```bash
npm run build
npm run lint
```

## Direction

- React uses Axios to communicate with FastAPI; this integration is planned.
- FastAPI will access PostgreSQL: Docker locally and Supabase in production.
- Maps discovery is planned around our own collector, without the Google Places
  API or a paid third-party collection API. Reliability and operating costs still
  need to be evaluated.
- The frontend currently contains the default starter, not the planned product.

## Repository

- `frontend/` — active React starter.
- `docs/` — product overview, release plans, stack, and design reference.
- `founder/` — business research and planning.
- `docs/archive/` — original requirements and historical Python prototype.

Start with the [product overview](docs/product-overview.md) and
[technology stack](docs/technology-stack.md).

## Legacy prototype

The old Streamlit app, Google Places integration, Gmail integration, Python
dependencies, and database migrations are preserved in
[`docs/archive/legacy-prototype/`](docs/archive/legacy-prototype/ARCHIVE.md).
They are reference material, not the active backend.

The local root `.env` and Python environment are preserved and ignored by Git.
Existing PostgreSQL data has not been changed. Do not place database credentials
or other server secrets in the React app.
