# Historical Python prototype

Archived on 17 November 2026 while restarting Outrelis with React and FastAPI.

This directory preserves the former Streamlit application for reference:
Google Places discovery, website research, email extraction, scoring,
deduplication, approval-first Gmail sending, tests, and database migrations.
Its README and `.env.example` describe the historical implementation.

The Google Places integration is not part of the active product direction.
No replacement collector or FastAPI backend was created during this cleanup.
Google OAuth dependencies here support the historical Gmail integration.

Source files were moved together to retain their relationships. Historical
absolute imports and relative configuration expect this directory as the working
directory. It is not wired into the React app or an active backend.

Existing database migrations are retained as history. Do not rerun, rewrite, or
delete them against an existing database as part of source cleanup. The local
root `.env`, local Python environment, Docker services, and PostgreSQL data were
left untouched. No secret files were copied into this archive.
