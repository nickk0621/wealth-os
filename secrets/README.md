# Local secrets

This directory is intentionally gitignored except for this README.

For Google Calendar read-only access:

1. In Google Cloud, enable the Google Calendar API.
2. Configure the OAuth consent screen for your account.
3. Create an OAuth 2.0 **Desktop app** client.
4. Download its JSON credentials.
5. Save the file locally as:

   `secrets/google_calendar_client_secret.json`

6. Run:

   `wealth-os calendar-auth`

Your browser will open for Google authorization. Wealth OS asks only for `calendar.readonly`. The resulting refresh/access token is stored locally at `secrets/google_calendar_token.json` and must never be committed.
