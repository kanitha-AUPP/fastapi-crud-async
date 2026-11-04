import json

import pytest

from app.api import events_crud

EVENT = {"title": "Angkor Run", "city": "Siem Reap", "price_usd": 25.5, "seats_left": 100}


def test_create_event(test_app, monkeypatch):
    async def mock_post(payload):
        return 1

    monkeypatch.setattr(events_crud, "post", mock_post)
    response = test_app.post("/events/", data=json.dumps(EVENT))
    assert response.status_code == 201
    assert response.json() == {"id": 1, **EVENT}


def test_create_event_invalid_json(test_app):
    response = test_app.post("/events/", data=json.dumps({"title": "ab"}))
    assert response.status_code == 422


def test_read_event(test_app, monkeypatch):
    async def mock_get(id):
        return {"id": 1, **EVENT}

    monkeypatch.setattr(events_crud, "get", mock_get)
    response = test_app.get("/events/1/")
    assert response.status_code == 200
    assert response.json() == {"id": 1, **EVENT}


def test_read_event_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(events_crud, "get", mock_get)
    response = test_app.get("/events/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"

    response = test_app.get("/events/0/")
    assert response.status_code == 422


def test_read_all_events(test_app, monkeypatch):
    async def mock_get_all():
        return [{"id": 1, **EVENT}, {"id": 2, **EVENT}]

    monkeypatch.setattr(events_crud, "get_all", mock_get_all)
    response = test_app.get("/events/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_event(test_app, monkeypatch):
    updated = {"title": "Angkor Run 2", "city": "Phnom Penh", "price_usd": 0, "seats_left": 5}

    async def mock_get(id):
        return {"id": 1, **EVENT}

    async def mock_put(id, payload):
        return 1

    monkeypatch.setattr(events_crud, "get", mock_get)
    monkeypatch.setattr(events_crud, "put", mock_put)
    response = test_app.put("/events/1/", data=json.dumps(updated))
    assert response.status_code == 200
    assert response.json() == {"id": 1, **updated}


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"title": "ab", "city": "Siem Reap", "price_usd": 1, "seats_left": 1}, 422],
        [1, {"title": "Valid title", "city": "X", "price_usd": 1, "seats_left": 1}, 422],
        [1, {"title": "Valid title", "city": "Siem Reap", "price_usd": -1, "seats_left": 1}, 422],
        [1, {"title": "Valid title", "city": "Siem Reap", "price_usd": 1, "seats_left": -1}, 422],
        [0, EVENT, 422],
    ],
)
def test_update_event_invalid(test_app, monkeypatch, id, payload, status_code):
    async def mock_get(id):
        return None

    monkeypatch.setattr(events_crud, "get", mock_get)
    response = test_app.put(f"/events/{id}/", data=json.dumps(payload))
    assert response.status_code == status_code


def test_remove_event(test_app, monkeypatch):
    async def mock_get(id):
        return {"id": 1, **EVENT}

    async def mock_delete(id):
        return id

    monkeypatch.setattr(events_crud, "get", mock_get)
    monkeypatch.setattr(events_crud, "delete", mock_delete)
    response = test_app.delete("/events/1/")
    assert response.status_code == 200
    assert response.json() == {"id": 1, **EVENT}


def test_remove_event_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(events_crud, "get", mock_get)
    assert test_app.delete("/events/999/").status_code == 404
    assert test_app.delete("/events/0/").status_code == 422