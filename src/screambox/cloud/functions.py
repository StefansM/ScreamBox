"""
Implementations of cloud functions that control the cloud portion of the ScreamBox.
"""
import dataclasses
from typing import Any, Dict, Tuple

from screambox.cloud.store import DatastoreFactory, UserstoreFactory
from screambox.model import INTERESTING_EVENTS


class HttpException(Exception):
    pass


class MissingQueryParamException(HttpException):
    def __init__(self, key: str):
        super().__init__(f"Missing query parameter '{key}'.")


class MissingBodyParamException(HttpException):
    def __init__(self, key: str):
        super().__init__(f"Missing parameter '{key}'.")


def _query_param(request, key: str) -> str:
    if not request.args or key not in request.args:
        raise MissingQueryParamException(key)

    return request.args[key]


def _body_param(payload, key: str, key_path: str) -> Any:
    if not payload or key not in payload:
        raise MissingBodyParamException(key_path)

    return payload[key]


def success() -> Tuple[Dict[str, Any], int]:
    return {"error": None}, 200


def error(error_string: str, status_code: int) -> Tuple[Dict[str, Any], int]:
    return {"error": error_string}, status_code


def trigger(request, store_factory: DatastoreFactory):
    try:
        user = _query_param(request, "user")

        request_json = request.get_json()
        event = _body_param(request_json, "event", "event")
        event_type = _body_param(event, "event_type", "event.event_type")

        incident_key = _body_param(event, "incident_key", "event.incident_key")

        store = store_factory(user)

        if event_type not in INTERESTING_EVENTS:
            return success()

        store.set_state(incident_key, event_type)

    except HttpException as e:
        return error(str(e), 400)
    except ValueError:
        return error("User does not exist", 404)

    return success()


def register(request, user_store_factory: UserstoreFactory):
    try:
        request_json = request.get_json()
        webhook_key = _body_param(request_json, "webhook_key", "webhook_key")

        user_store = user_store_factory()

        uid = user_store.register(webhook_key)

        return {"user_id": str(uid)}, 200

    except HttpException as e:
        return error(str(e), 400)


def list_incidents(request, store_factory: DatastoreFactory):
    try:
        user = _query_param(request, "user")

        store = store_factory(user)

        results = [dataclasses.asdict(i) for i in store.open_incidents()]
        return {"open_incidents": results}, 200

    except HttpException as e:
        return error(str(e), 400)
    except ValueError:
        return error("User not found", 404)
