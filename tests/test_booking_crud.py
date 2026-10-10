import pytest
from jsonschema import validate

from api.schemas import BOOKING_LIST_SCHEMA, BOOKING_SCHEMA, CREATE_BOOKING_RESPONSE_SCHEMA


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.schema
def test_create_booking_returns_id_and_echoes_payload(client, token, booking_payload):
    resp = client.create_booking(booking_payload)

    assert resp.status_code == 200
    body = resp.json()
    validate(instance=body, schema=CREATE_BOOKING_RESPONSE_SCHEMA)
    assert body["booking"] == booking_payload

    client.delete_booking(body["bookingid"], token)  # clean up


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.schema
def test_get_booking_returns_what_was_created(client, created_booking, booking_payload):
    resp = client.get_booking(created_booking)

    assert resp.status_code == 200
    body = resp.json()
    validate(instance=body, schema=BOOKING_SCHEMA)
    assert body == booking_payload


@pytest.mark.regression
@pytest.mark.schema
def test_list_bookings_returns_ids(client):
    resp = client.list_bookings()

    assert resp.status_code == 200
    validate(instance=resp.json(), schema=BOOKING_LIST_SCHEMA)


@pytest.mark.regression
def test_created_booking_appears_in_list(client, created_booking):
    resp = client.list_bookings()

    ids = [item["bookingid"] for item in resp.json()]
    assert created_booking in ids


@pytest.mark.regression
def test_filter_bookings_by_name(client, created_booking, booking_payload):
    resp = client.list_bookings(
        firstname=booking_payload["firstname"], lastname=booking_payload["lastname"]
    )

    assert resp.status_code == 200
    ids = [item["bookingid"] for item in resp.json()]
    assert created_booking in ids


@pytest.mark.regression
def test_full_update_replaces_booking(client, token, created_booking, booking_payload):
    updated = {**booking_payload, "firstname": "Updated", "totalprice": 999, "depositpaid": False}

    resp = client.update_booking(created_booking, updated, token)

    assert resp.status_code == 200
    assert resp.json() == updated
    assert client.get_booking(created_booking).json() == updated


@pytest.mark.regression
def test_partial_update_changes_only_sent_fields(client, token, created_booking, booking_payload):
    resp = client.partial_update_booking(created_booking, {"lastname": "Patched"}, token)

    assert resp.status_code == 200
    body = resp.json()
    assert body["lastname"] == "Patched"
    assert body["firstname"] == booking_payload["firstname"]
    assert body["totalprice"] == booking_payload["totalprice"]


@pytest.mark.regression
def test_delete_removes_booking(client, token, booking_payload):
    booking_id = client.create_booking(booking_payload).json()["bookingid"]

    delete_resp = client.delete_booking(booking_id, token)

    assert delete_resp.status_code == 201  # known quirk: API returns 201 for DELETE
    assert client.get_booking(booking_id).status_code == 404
