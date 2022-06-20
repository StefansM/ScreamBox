from typing import Dict

from model import WebhookEvent, EventPayload, PollResult

events_map: Dict[str, EventPayload] = {}


def handle_event(event: WebhookEvent):
    _save_event(event)


def _save_event(event: WebhookEvent):
    if event.event.data and "incident_key" in event.event.data:
        incident_id = event.event.data["incident_key"]
        print(f"Saving incident {incident_id} with status {event.event.event_type}")
        events_map[incident_id] = event.event


def get_open_incidents() -> PollResult:
    open_incidents = []
    titles = []
    for event in events_map.values():
        if event.event_type in ['incident.reopened', 'incident.triggered']:
            open_incidents.append(event)
            if "title" in event.data:
                titles.append(event.data["title"])

    is_open = bool(open_incidents)

    return PollResult(is_open=is_open, titles=titles)
