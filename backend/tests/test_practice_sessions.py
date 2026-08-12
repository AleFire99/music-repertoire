from fastapi.testclient import TestClient


def _create_piece(client: TestClient, title: str) -> int:
    return client.post("/api/pieces", json={"title": title}).json()["id"]


def test_create_and_list_practice_session(client: TestClient) -> None:
    piece_id = _create_piece(client, "Clair de Lune")
    payload = {
        "piece_id": piece_id,
        "practiced_at": "2026-08-01T10:00:00Z",
        "duration_minutes": 30,
        "notes": "Worked on the arpeggios",
        "rating": 4,
        "section": "measures 1-16",
    }
    create_response = client.post("/api/practice-sessions", json=payload)
    assert create_response.status_code == 201
    session = create_response.json()
    assert session["piece_id"] == piece_id
    assert session["duration_minutes"] == 30
    assert session["notes"] == "Worked on the arpeggios"
    assert session["rating"] == 4
    assert session["section"] == "measures 1-16"

    list_response = client.get("/api/practice-sessions")
    assert list_response.status_code == 200
    assert [s["id"] for s in list_response.json()] == [session["id"]]


def test_create_session_missing_piece_404(client: TestClient) -> None:
    payload = {
        "piece_id": 999999,
        "practiced_at": "2026-08-01T10:00:00Z",
        "duration_minutes": 15,
    }
    response = client.post("/api/practice-sessions", json=payload)
    assert response.status_code == 404


def test_create_session_invalid_rating_422(client: TestClient) -> None:
    piece_id = _create_piece(client, "Etude")
    payload = {
        "piece_id": piece_id,
        "practiced_at": "2026-08-01T10:00:00Z",
        "duration_minutes": 15,
        "rating": 6,
    }
    response = client.post("/api/practice-sessions", json=payload)
    assert response.status_code == 422


def test_list_sessions_filter_by_piece(client: TestClient) -> None:
    piece_a = _create_piece(client, "A")
    piece_b = _create_piece(client, "B")
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_b, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 20},
    )

    response = client.get("/api/practice-sessions", params={"piece_id": piece_a})
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) == 1
    assert sessions[0]["piece_id"] == piece_a


def test_list_sessions_empty(client: TestClient) -> None:
    response = client.get("/api/practice-sessions")
    assert response.status_code == 200
    assert response.json() == []


def test_list_sessions_ordered_newest_first(client: TestClient) -> None:
    piece_id = _create_piece(client, "Sonata")
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_id, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_id, "practiced_at": "2026-08-03T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_id, "practiced_at": "2026-08-02T10:00:00Z", "duration_minutes": 10},
    )

    response = client.get("/api/practice-sessions")
    dates = [s["practiced_at"] for s in response.json()]
    assert dates == sorted(dates, reverse=True)
