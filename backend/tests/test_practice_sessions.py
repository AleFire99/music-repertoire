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


def test_stats_empty(client: TestClient) -> None:
    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    assert response.json() == {
        "total_minutes": 0,
        "pieces": [],
        "recently_practiced": [],
        "neglected": [],
    }


def test_stats_empty_with_pieces_but_no_sessions(client: TestClient) -> None:
    _create_piece(client, "Never Practiced")

    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    body = response.json()

    assert body["pieces"] == []
    assert body["recently_practiced"] == []
    assert len(body["neglected"]) == 1
    assert body["neglected"][0]["last_practiced_at"] is None


def test_stats_aggregates_across_pieces(client: TestClient) -> None:
    piece_a = _create_piece(client, "Clair de Lune")
    piece_b = _create_piece(client, "Sonata")

    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 20},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-03T10:00:00Z", "duration_minutes": 15},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_b, "practiced_at": "2026-08-02T10:00:00Z", "duration_minutes": 30},
    )

    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    body = response.json()

    assert body["total_minutes"] == 65

    by_id = {p["piece_id"]: p for p in body["pieces"]}
    assert by_id[piece_a]["total_minutes"] == 35
    assert by_id[piece_a]["session_count"] == 2
    assert by_id[piece_a]["last_practiced_at"] == "2026-08-03T10:00:00Z"
    assert by_id[piece_b]["total_minutes"] == 30
    assert by_id[piece_b]["session_count"] == 1

    # ordered by last_practiced_at desc: piece_a (Aug 3) before piece_b (Aug 2)
    assert [p["piece_id"] for p in body["pieces"]] == [piece_a, piece_b]


def test_stats_recently_practiced_ordered_most_recent_first(client: TestClient) -> None:
    piece_a = _create_piece(client, "Clair de Lune")
    piece_b = _create_piece(client, "Sonata")
    piece_c = _create_piece(client, "Etude")

    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_b, "practiced_at": "2026-08-05T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_c, "practiced_at": "2026-08-03T10:00:00Z", "duration_minutes": 10},
    )
    # A second, more recent session on piece_a should make it the most recent overall.
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-10T10:00:00Z", "duration_minutes": 10},
    )

    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    recently_practiced = response.json()["recently_practiced"]

    assert [p["piece_id"] for p in recently_practiced] == [piece_a, piece_b, piece_c]
    assert recently_practiced[0]["last_practiced_at"] == "2026-08-10T10:00:00Z"


def test_stats_recently_practiced_capped_at_five(client: TestClient) -> None:
    piece_ids = [_create_piece(client, f"Piece {i}") for i in range(6)]
    for i, piece_id in enumerate(piece_ids):
        client.post(
            "/api/practice-sessions",
            json={
                "piece_id": piece_id,
                "practiced_at": f"2026-08-{i + 1:02d}T10:00:00Z",
                "duration_minutes": 10,
            },
        )

    response = client.get("/api/practice-sessions/stats")
    recently_practiced = response.json()["recently_practiced"]

    assert len(recently_practiced) == 5
    # Most recently created/practiced piece (last one) should be first.
    assert recently_practiced[0]["piece_id"] == piece_ids[-1]


def test_stats_neglected_includes_never_practiced_first(client: TestClient) -> None:
    piece_practiced = _create_piece(client, "Practiced")
    piece_never = _create_piece(client, "Never Practiced")

    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_practiced,
            "practiced_at": "2026-08-01T10:00:00Z",
            "duration_minutes": 10,
        },
    )

    response = client.get("/api/practice-sessions/stats")
    neglected = response.json()["neglected"]

    assert [p["piece_id"] for p in neglected] == [piece_never, piece_practiced]
    assert neglected[0]["last_practiced_at"] is None
    assert neglected[1]["last_practiced_at"] == "2026-08-01T10:00:00Z"


def test_stats_neglected_ordered_oldest_last_practiced_first(client: TestClient) -> None:
    piece_a = _create_piece(client, "A")
    piece_b = _create_piece(client, "B")

    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-05T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_b, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 10},
    )

    response = client.get("/api/practice-sessions/stats")
    neglected = response.json()["neglected"]

    # piece_b was practiced longer ago than piece_a, so it's more neglected.
    assert [p["piece_id"] for p in neglected] == [piece_b, piece_a]


def test_stats_neglected_capped_at_five(client: TestClient) -> None:
    for i in range(6):
        _create_piece(client, f"Untouched {i}")

    response = client.get("/api/practice-sessions/stats")
    neglected = response.json()["neglected"]

    assert len(neglected) == 5
