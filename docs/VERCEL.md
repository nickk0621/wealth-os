# Deploy Wealth OS on Vercel

Wealth OS has a separate cloud entrypoint for Vercel. The existing Streamlit/Mac app remains intact.

## Architecture

- `cloud/server.py` — FastAPI backend deployed as a Vercel Function.
- `public/index.html` — lightweight cloud dashboard served as a static asset.
- `src/wealth_os/*` — shared agent and CRE logic used by both local and cloud versions.
- Browser `localStorage` — structured state and recent conversation history in the cheapest cloud configuration.

This design intentionally avoids a hosted database for V1. Your structured operating data remains in the browser that you use. When you ask the Chief of Staff a question, the browser sends the current state and relevant conversation context to the authenticated backend for that request.

## Required Vercel environment variables

Configure these in Vercel Project Settings -> Environment Variables:

- `OPENAI_API_KEY` — your OpenAI API key. Never put it in GitHub or browser JavaScript.
- `WEALTH_OS_PASSWORD` — a strong password you will use to unlock your deployed Wealth OS.
- `WEALTH_OS_SESSION_SECRET` — a long random secret used to sign the authentication cookie. It should be different from the password.

Generate a session secret locally with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Apply the variables to Production, Preview, and Development if you want all deployment types to work.

## Deploy from GitHub

1. In Vercel, choose **Add New -> Project**.
2. Import `nickk0621/wealth-os` from GitHub.
3. Do not set a custom framework preset, build command, or output directory. Vercel's FastAPI detection uses the custom entrypoint declared in `pyproject.toml`.
4. Add the three environment variables above.
5. Deploy.
6. Open the generated `*.vercel.app` URL and enter `WEALTH_OS_PASSWORD`.

Vercel serves `public/index.html` as a static asset and loads the FastAPI `app` from `cloud.server:app`.

## Cheapest-mode data model

The first cloud version deliberately does not use a hosted database:

- scoreboard, priorities, daily check-ins, and recent conversation history are stored in that browser's local storage;
- OpenAI and Vercel secrets remain server-side as environment variables;
- deterministic CRE underwriting is performed by the backend;
- AI analysis is performed only when you explicitly request it.

Use **State -> Download backup** periodically. Because browser-local state is device/browser specific, clearing browser storage will remove it unless you have a backup.

## Security notes

The public URL can show the empty UI shell, but every endpoint that can access OpenAI or underwriting context requires the signed authentication cookie. The OpenAI key never enters browser JavaScript.

This is appropriate for a personal V1, but it is not a multi-user identity system. Before sharing Wealth OS with other people or storing highly sensitive documents in the cloud, replace the shared password with a real identity provider and add encrypted persistent storage.

## Google Calendar

The current Vercel version intentionally does not reuse the local desktop Google OAuth token. The local Mac app retains Calendar Intelligence. A cloud Calendar integration should use a web OAuth callback and persistent encrypted token storage; add that only after a durable cloud data store and proper identity layer are in place.

## Local Vercel development

With Vercel CLI installed:

```bash
vercel dev
```

For your normal private Mac version, continue to use:

```bash
wealth-os dashboard
```
