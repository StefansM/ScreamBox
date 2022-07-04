from typing import List

import pytest as pytest

import screambox.cloud.functions
from screambox.cloud.store import DatastoreFactory, UserstoreFactory
from screambox.model import Incident
from test_screambox.fake import FakeDatastore, FakeRequest, FakeUserstore

TRIGGER_TEST_CASES = [
    (400, FakeRequest(None, None)),
    (400, FakeRequest({"user": "VALID_USER"}, None)),
    (400, FakeRequest({"user": "VALID_USER"}, {})),
    (400, FakeRequest({"user": "VALID_USER"}, {"event": {}})),
    (400, FakeRequest({"user": "VALID_USER"}, {"event": {"event_type": "incident.acknowledged"}})),
    (200, FakeRequest({"user": "VALID_USER"}, {"event": {"event_type": "incident.acknowledged", "incident_key": "key"}})),
    (200, FakeRequest({"user": "VALID_USER"}, {"event": {"event_type": "incident.triggered", "incident_key": "key"}})),
    (404, FakeRequest({"user": "INVALID_USER"}, {"event": {"event_type": "incident.triggered", "incident_key": "key"}})),
]


@pytest.fixture()
def datastore_factory() -> DatastoreFactory:
    datastore = FakeDatastore()

    def _create(user: str):
        if user != "VALID_USER":
            raise ValueError("Unknown user")

        return datastore

    return _create


@pytest.mark.parametrize("expected_code, req", TRIGGER_TEST_CASES)
def test_trigger_response_codes(expected_code: int, req: FakeRequest, datastore_factory: DatastoreFactory):
    """Response code is as expected."""
    _, code = screambox.cloud.functions.trigger(req, datastore_factory)
    assert code == expected_code


def test_add_and_update_incident(datastore_factory: DatastoreFactory):
    """Incident states can be updated."""
    request1 = FakeRequest({"user": "VALID_USER"}, {"event": {"event_type": "incident.triggered", "incident_key": "foo"}})
    request2 = FakeRequest({"user": "VALID_USER"}, {"event": {"event_type": "incident.acknowledged", "incident_key": "foo"}})

    datastore = datastore_factory("VALID_USER")

    screambox.cloud.functions.trigger(request1, datastore_factory)
    assert datastore.open_incidents()
    assert not datastore.closed_incidents()

    screambox.cloud.functions.trigger(request2, datastore_factory)
    assert not datastore.open_incidents()
    assert datastore.closed_incidents()


REGISTER_TEST_CASES = [
    (400, FakeRequest(None, None)),
    (400, FakeRequest(None, {})),
    (400, FakeRequest(None, {"some_other_key": "foo"})),
    (200, FakeRequest(None, {"webhook_key": "secret_key"})),
]


@pytest.fixture()
def userstore_factory() -> UserstoreFactory:
    user_store = FakeUserstore()
    return lambda: user_store


@pytest.mark.parametrize("expected_code, req", REGISTER_TEST_CASES)
def test_register_response_codes(expected_code: int, req: FakeRequest, userstore_factory: UserstoreFactory):
    """Response code is as expected."""
    _, code = screambox.cloud.functions.register(req, userstore_factory)
    assert code == expected_code


def test_register_repeatedly(userstore_factory: UserstoreFactory):
    """Registering the same webhook ID repeatedly returns the same user ID."""
    request = FakeRequest(None, {"webhook_key": "some_key"})

    response1, code1 = screambox.cloud.functions.register(request, userstore_factory)
    response2, code2 = screambox.cloud.functions.register(request, userstore_factory)
    assert code1 == 200 and code2 == 200
    assert response1["user_id"] == response2["user_id"]


def test_register_different_keys(userstore_factory: UserstoreFactory):
    """Registering different webhook keys returns different user IDs."""
    request1 = FakeRequest(None, {"webhook_key": "some_key"})
    request2 = FakeRequest(None, {"webhook_key": "some_other_key"})

    response1, code1 = screambox.cloud.functions.register(request1, userstore_factory)
    response2, code2 = screambox.cloud.functions.register(request2, userstore_factory)
    assert code1 == 200 and code2 == 200
    assert response1["user_id"] != response2["user_id"]


LIST_INCIDENTS_TEST_CASES = [
    (400, FakeRequest(None, None)),
    (400, FakeRequest({}, None)),
    (404, FakeRequest({"user": "INVALID_USER"}, None)),
    (200, FakeRequest({"user": "VALID_USER"}, None)),
    (200, FakeRequest({"user": "VALID_USER"}, None)),
]


@pytest.mark.parametrize("expected_code, req", LIST_INCIDENTS_TEST_CASES)
def test_trigger_response_codes(expected_code: int, req: FakeRequest, datastore_factory: DatastoreFactory):
    _, code = screambox.cloud.functions.list_incidents(req, datastore_factory)
    assert code == expected_code


def test_list_open_incidents(datastore_factory: DatastoreFactory):
    datastore = datastore_factory("VALID_USER")
    datastore.set_state("foo", "incident.triggered")

    request = FakeRequest({"user": "VALID_USER"}, None)

    response, code = screambox.cloud.functions.list_incidents(request, datastore_factory)

    assert response["open_incidents"] == [{"key": "foo", "state": "incident.triggered"}]


def test_list_closed_incidents(datastore_factory: DatastoreFactory):
    datastore = datastore_factory("VALID_USER")
    datastore.set_state("foo", "incident.acknowledged")

    request = FakeRequest({"user": "VALID_USER"}, None)

    response, code = screambox.cloud.functions.list_incidents(request, datastore_factory)

    assert response["open_incidents"] == []
