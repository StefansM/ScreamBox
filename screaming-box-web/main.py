from __future__ import annotations

import datetime
from typing import Any, Optional, Dict

import fastapi
import pydantic
import uvicorn


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


app = fastapi.FastAPI()


@app.get("/poll", response_model=PollResult)
def poll():
    return PollResult(
        is_open=False,
    )


@app.post("/trigger", response_model=WebhookResult)
def trigger(event: WebhookEvent):
    print(event)
    return WebhookResult(accepted=True)


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
