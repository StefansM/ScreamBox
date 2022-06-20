from __future__ import annotations

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import webhook_event_handler
from model import PollResult, WebhookResult, WebhookEvent

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    print(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@app.get("/poll", response_model=PollResult)
def poll():
    return webhook_event_handler.get_open_incidents()


@app.post("/trigger", response_model=WebhookResult)
def trigger(event: WebhookEvent):
    webhook_event_handler.handle_event(event)
    return WebhookResult(accepted=True)


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
