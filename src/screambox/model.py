import dataclasses

OPEN_STATUSES = ["incident.triggered", "incident.reopened"]
INTERESTING_EVENTS = {"incident.triggered", "incident.acknowledged", "incident.reopened", "incident.resolved"}


@dataclasses.dataclass
class Incident:
    key: str
    state: str
