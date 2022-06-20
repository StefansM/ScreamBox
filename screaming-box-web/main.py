from __future__ import annotations

import fastapi
import uvicorn
import webhook_event_handler
from model import PollResult, WebhookResult, WebhookEvent

app = fastapi.FastAPI()


@app.get("/poll", response_model=PollResult)
def poll():
    open_incidents = webhook_event_handler.get_open_incidents()
    return PollResult(
        is_open=len(open_incidents) > 0,
    )


@app.post("/trigger", response_model=WebhookResult)
def trigger(event: WebhookEvent):
    print(event)
    webhook_event_handler.handle_event(event)
    return WebhookResult(accepted=True)


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
