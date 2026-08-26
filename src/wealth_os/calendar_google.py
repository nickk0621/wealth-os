from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[2]
SECRETS_DIR = ROOT / "secrets"
CLIENT_SECRET_PATH = SECRETS_DIR / "google_calendar_client_secret.json"
TOKEN_PATH = SECRETS_DIR / "google_calendar_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
]


@dataclass
class CalendarEvent:
    summary: str
    start: str
    end: str
    calendar: str
    attendees: int = 0
    event_type: str = "default"

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "start": self.start,
            "end": self.end,
            "calendar": self.calendar,
            "attendees": self.attendees,
            "event_type": self.event_type,
        }


def _load_credentials(interactive: bool = False) -> Credentials | None:
    creds: Credentials | None = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

    if creds and creds.valid:
        return creds

    if not interactive:
        return None

    if not CLIENT_SECRET_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CLIENT_SECRET_PATH}. Create a Google OAuth Desktop client, download the JSON, "
            "and save it at that path."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds


def authorize_calendar() -> None:
    _load_credentials(interactive=True)


def calendar_is_connected() -> bool:
    try:
        return _load_credentials(interactive=False) is not None
    except Exception:
        return False


def _service():
    creds = _load_credentials(interactive=False)
    if not creds:
        raise RuntimeError("Google Calendar is not connected. Run `wealth-os calendar-auth` first.")
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def list_events(days_back: int = 7, days_forward: int = 7, max_results: int = 250) -> list[CalendarEvent]:
    service = _service()
    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=days_back)).isoformat()
    time_max = (now + timedelta(days=days_forward)).isoformat()

    calendars = service.calendarList().list(maxResults=250).execute().get("items", [])
    events: list[CalendarEvent] = []

    for cal in calendars:
        cal_id = cal["id"]
        cal_name = cal.get("summaryOverride") or cal.get("summary") or cal_id
        page_token = None
        while True:
            response = (
                service.events()
                .list(
                    calendarId=cal_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                    maxResults=max_results,
                    pageToken=page_token,
                )
                .execute()
            )
            for item in response.get("items", []):
                if item.get("status") == "cancelled":
                    continue
                start = item.get("start", {}).get("dateTime") or item.get("start", {}).get("date", "")
                end = item.get("end", {}).get("dateTime") or item.get("end", {}).get("date", "")
                events.append(
                    CalendarEvent(
                        summary=item.get("summary", "(busy)"),
                        start=start,
                        end=end,
                        calendar=cal_name,
                        attendees=len(item.get("attendees", [])),
                        event_type=item.get("eventType", "default"),
                    )
                )
            page_token = response.get("nextPageToken")
            if not page_token:
                break

    events.sort(key=lambda e: e.start)
    return events


def calendar_digest(days_back: int = 7, days_forward: int = 2) -> str:
    if not calendar_is_connected():
        return "GOOGLE CALENDAR: not connected."
    try:
        events = list_events(days_back=days_back, days_forward=days_forward)
    except Exception as exc:
        return f"GOOGLE CALENDAR: connected but unavailable: {exc}"

    lines = [f"GOOGLE CALENDAR EVENTS ({days_back} days back, {days_forward} days forward):"]
    for event in events[:120]:
        lines.append(
            f"- {event.start} -> {event.end} | {event.summary} | calendar={event.calendar} | attendees={event.attendees} | type={event.event_type}"
        )
    if len(events) > 120:
        lines.append(f"- ... {len(events) - 120} more events omitted")
    return "\n".join(lines)
