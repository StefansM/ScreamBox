from model import WebhookEvent

events_map = {}


def handle_event(event: WebhookEvent):
    _save_event(event)


def _save_event(event: WebhookEvent):
    events_map[event.event.id] = event.event


def get_open_incidents():
    open_incidents = []
    for event in events_map.values():
        if event.event_type in ['incident.reopened', 'incident.triggered']:
            open_incidents.append(event)
    return open_incidents
