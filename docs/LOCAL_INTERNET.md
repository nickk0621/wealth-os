# Running Wealth OS locally while connected to the internet

"Local" describes **where the program runs**, not whether it can use the internet.

When you run:

```bash
wealth-os dashboard
```

Streamlit starts a web server on your own computer, normally at a `localhost` address such as `http://localhost:8501`. Your browser talks to that local server. The Python process can still make **outbound HTTPS requests** over your normal internet connection to services you explicitly configure, such as OpenAI or Google Calendar.

A simple mental model:

```text
Your browser
    |
    | local connection
    v
Wealth OS on your laptop  ---- outbound HTTPS ----> OpenAI API
          |
          +---------------- outbound HTTPS ----> Google Calendar API
          |
          +---------------- local files -------> data/, secrets/
```

No public web server is required for this model. Your router/firewall usually allows outbound HTTPS, while unsolicited inbound connections from the public internet remain blocked.

## What stays local

- the Streamlit server
- `data/state.json`
- session memory database
- saved reports/history
- Google OAuth client file and token under `secrets/`

## What leaves the computer

When you ask the Chief of Staff something, the prompt/context needed for that agent run is sent to the configured OpenAI API over encrypted HTTPS. When Calendar is connected, Wealth OS makes encrypted HTTPS requests to Google's Calendar API and includes calendar context in relevant agent runs.

Do not put secrets in prompts or commit them to GitHub.

## Google Calendar connection

Wealth OS uses a read-only Calendar OAuth scope. The local setup is:

1. Create a Google Cloud project.
2. Enable Google Calendar API.
3. Configure the Google Auth consent screen.
4. Create an OAuth client of type **Desktop app**.
5. Download the client JSON to `secrets/google_calendar_client_secret.json`.
6. Run `wealth-os calendar-auth`.
7. Google opens in your browser. After approval, it redirects to a temporary callback server on your own computer.
8. Wealth OS stores the resulting token locally in `secrets/google_calendar_token.json`.

After that, `wealth-os morning`, `wealth-os calendar-audit`, and the dashboard can read your calendar.

## Does localhost mean only I can see it?

By default, yes: `localhost` / `127.0.0.1` is accessible only from the same computer. That is the recommended model for private financial and operating data.

If you intentionally bind Streamlit to `0.0.0.0`, other devices on the same network may be able to connect. Do not expose Wealth OS directly to the public internet without authentication, TLS, firewall rules, and a proper deployment design.

If you want access from your phone while away from home, a safer next step is a private VPN/mesh network or an authenticated deployment rather than raw router port-forwarding.

## API keys

Set your OpenAI key as an environment variable or in a local `.env` file:

```bash
export OPENAI_API_KEY="..."
```

`.env` and `secrets/` are gitignored. Never paste keys into source files.
