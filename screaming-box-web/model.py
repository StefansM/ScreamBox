import datetime
from typing import Any, Dict, Optional

import pydantic


class PollResult(pydantic.BaseModel):
    is_open: bool


class WebhookResult(pydantic.BaseModel):
    accepted: bool


class EventPayload(pydantic.BaseModel):
    id: str
    event_type: str
    resource_type: str
    occurred_at: datetime.datetime
    agent: Optional[Any]
    client: Optional[Any]
    data: Optional[Dict[str, Any]]


class WebhookEvent(pydantic.BaseModel):
    event: EventPayload

