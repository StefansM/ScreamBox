from typing import Any, Optional, Dict

import pydantic
import datetime

class PollResult(pydantic.BaseModel):
    is_open: bool


class WebhookResult(pydantic.BaseModel):
    accepted: bool


class EventPayload(pydantic.BaseModel):
    id: str
    event_type: str
    resource_type: str
    occurred_at: datetime.datetime
    agent: Optional[str]
    client: Optional[str]
    data: Dict[str, Any]


class WebhookEvent(pydantic.BaseModel):
    event: EventPayload

