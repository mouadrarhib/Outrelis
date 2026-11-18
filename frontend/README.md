# Outrelis frontend

React + TypeScript + Vite authentication interface using the Outrelis
sage/paper/tomato palette, local Instrument Serif / DM Sans fonts, wordmark,
and discovery diagram.

## Run locally

Start the FastAPI backend first (see `../backend/README.md`), then:

```bash
npm install
npm run dev
```

Open http://localhost:5173. The default API base URL is
`http://127.0.0.1:8000/api/v1`. Copy `.env.example` to `.env.local` to override
`VITE_API_BASE_URL`; only public configuration belongs in Vite environment files.

## Routes

- `/login`: email/password sign-in.
- `/register`: full name, email and password; success returns to login.
- `/forgot-password`: honest availability notice, not a simulated reset request.
- `/getting-started`: authenticated choice between a guided first-lead path and pipeline growth.
- `/account`: authenticated account confirmation with server-backed sign-out.

There is no product dashboard yet. Registration requires a 1–100 character trimmed
name and an 8–128 character password. Simulated authentication outcomes have
been replaced by the actual FastAPI contract.

## Structure

- `src/components/layout/`: shared split layout and reference SVG diagram.
- `src/components/ui/`: shared SVG icons and beUI feedback components.
- `src/features/auth/components/`: auth forms and account confirmation.
- `src/features/auth/api/`: typed backend requests.
- `src/features/auth/AuthProvider.tsx`: user identity, expiry and session lifecycle.
- `src/features/onboarding/`: starting-path API, types and authenticated choice page.
- `src/lib/http.ts`: Axios instance and in-memory bearer token handling.
- `src/lib/api-error.ts`: shared backend-code, network, timeout and retry parser.
- `public/fonts/`: self-hosted fonts and their original licenses.

Axios calls FastAPI directly. Tokens and passwords are never written to
localStorage/sessionStorage. Refreshing the page signs the browser out locally;
the server session still expires normally. A persistent login requires a separate
cookie/CSRF design. Sign-out revokes the current session through the backend.

SPA hosting must serve `index.html` for application routes. Backend CORS origins
must match the frontend origin. Password recovery, mailbox OAuth, and persistent
browser login are not implemented.

## Checks

```bash
npm run build
npm run lint
npm run test:e2e
```

Playwright uses system Google Chrome on this machine. On another machine, install
Chromium with `npx playwright install chromium`, or set
`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` to your Chrome executable.

Default tests mock API responses and cover form contracts, accessibility behavior,
network errors, throttling, session handling, and responsive layouts at nine widths.
Screenshots are saved under ignored `test-results/screenshots/`.

The beUI Alert source is adapted locally under its MIT license. Tailwind CSS 4
supplies its semantic utility classes; Outrelis-specific styling remains in
`src/App.css` so feedback matches the established authentication design.

For an opt-in real backend test, start local FastAPI on port 8000 and run:

```bash
LIVE_API=1 npm run test:e2e
```

This creates a randomly named local test account, exercises registration/login/me/
logout, verifies revocation, and deletes only that account afterward using the
backend's local environment. Do not run the live test against production.
