from typing import Any, Dict, Optional

from screambox.cloud.store import Datastore, Userstore
from screambox.model import Incident, OPEN_STATUSES


class FakeRequest:
    def __init__(self, query_params: Optional[Dict[str, Any]], body: Optional[Dict[str, Any]]):
        self.args = query_params
        self.json = body

    def get_json(self):
        return self.json


class FakeDatastore(Datastore):
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}

    def open_incidents(self) -> list[Incident]:
        return [i for i in self.incidents.values() if i.state in OPEN_STATUSES]

    def closed_incidents(self):
        return [i for i in self.incidents.values() if i.state not in OPEN_STATUSES]

    def set_state(self, incident_key: str, state: str):
        self.incidents[incident_key] = Incident(incident_key, state)

    def delete_incident(self, incident_key: str):
        if incident_key in self.incidents:
            del self.incidents[incident_key]


class FakeUserstore(Userstore):
    def __init__(self):
        self.users: Dict[str, str] = {}
        self.current_id: int = 0

    def register(self, secret_key: str) -> str:
        if secret_key not in self.users:
            new_id = f"user_{self.current_id}"
            self.current_id += 1
            self.users[secret_key] = new_id

        return self.users[secret_key]
