from fastapi.testclient import TestClient


def test_create_and_get_piece(client: TestClient) -> None:
    payload = {"title": "Clair de Lune", "composer": "Debussy"}
    create_response = client.post("/api/pieces", json=payload)
    assert create_response.status_code == 201
    piece = create_response.json()
    assert piece["title"] == "Clair de Lune"

    get_response = client.get(f"/api/pieces/{piece['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["composer"] == "Debussy"


def test_list_pieces_empty(client: TestClient) -> None:
    response = client.get("/api/pieces")
    assert response.status_code == 200
    assert response.json() == []


def test_update_piece(client: TestClient) -> None:
    created = client.post("/api/pieces", json={"title": "Prelude"}).json()
    response = client.patch(f"/api/pieces/{created['id']}", json={"composer": "Chopin"})
    assert response.status_code == 200
    assert response.json()["composer"] == "Chopin"


def test_delete_piece(client: TestClient) -> None:
    created = client.post("/api/pieces", json={"title": "Etude"}).json()
    delete_response = client.delete(f"/api/pieces/{created['id']}")
    assert delete_response.status_code == 204
    assert client.get(f"/api/pieces/{created['id']}").status_code == 404


def test_delete_piece_with_practice_sessions_cascades(client: TestClient) -> None:
    piece = client.post("/api/pieces", json={"title": "Etude"}).json()
    session = client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece["id"],
            "practiced_at": "2026-08-01T10:00:00Z",
            "duration_minutes": 20,
        },
    ).json()

    delete_response = client.delete(f"/api/pieces/{piece['id']}")
    assert delete_response.status_code == 204

    remaining_sessions = client.get(
        "/api/practice-sessions", params={"piece_id": piece["id"]}
    ).json()
    assert session["id"] not in [s["id"] for s in remaining_sessions]


def test_get_missing_piece_404(client: TestClient) -> None:
    response = client.get("/api/pieces/999999")
    assert response.status_code == 404


def test_create_piece_defaults_status_and_tags(client: TestClient) -> None:
    created = client.post("/api/pieces", json={"title": "Nocturne"}).json()
    assert created["status"] == "backlog"
    assert created["tags"] == []


def test_create_piece_with_status_and_tags(client: TestClient) -> None:
    payload = {"title": "Ballade", "status": "learning", "tags": ["romantic", "chopin"]}
    created = client.post("/api/pieces", json=payload).json()
    assert created["status"] == "learning"
    assert created["tags"] == ["romantic", "chopin"]


def test_create_piece_invalid_status_422(client: TestClient) -> None:
    response = client.post("/api/pieces", json={"title": "Etude", "status": "unknown"})
    assert response.status_code == 422


def test_update_piece_status_and_tags(client: TestClient) -> None:
    created = client.post("/api/pieces", json={"title": "Sonata"}).json()
    response = client.patch(
        f"/api/pieces/{created['id']}",
        json={"status": "memorized", "tags": ["classical"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "memorized"
    assert body["tags"] == ["classical"]


def test_list_pieces_filter_by_status(client: TestClient) -> None:
    client.post("/api/pieces", json={"title": "A", "status": "learning"})
    client.post("/api/pieces", json={"title": "B", "status": "archived"})

    response = client.get("/api/pieces", params={"status": "learning"})
    assert response.status_code == 200
    titles = [piece["title"] for piece in response.json()]
    assert titles == ["A"]


def test_list_pieces_filter_by_status_invalid_422(client: TestClient) -> None:
    response = client.get("/api/pieces", params={"status": "unknown"})
    assert response.status_code == 422


def test_list_pieces_filter_by_tag(client: TestClient) -> None:
    client.post("/api/pieces", json={"title": "A", "tags": ["baroque", "fugue"]})
    client.post("/api/pieces", json={"title": "B", "tags": ["romantic"]})

    response = client.get("/api/pieces", params={"tag": "fugue"})
    assert response.status_code == 200
    titles = [piece["title"] for piece in response.json()]
    assert titles == ["A"]


def test_create_piece_defaults_favorite(client: TestClient) -> None:
    created = client.post("/api/pieces", json={"title": "Impromptu"}).json()
    assert created["is_favorite"] is False


def test_update_piece_favorite(client: TestClient) -> None:
    created = client.post("/api/pieces", json={"title": "Waltz"}).json()
    response = client.patch(f"/api/pieces/{created['id']}", json={"is_favorite": True})
    assert response.status_code == 200
    assert response.json()["is_favorite"] is True


def test_list_pieces_filter_by_favorite(client: TestClient) -> None:
    client.post("/api/pieces", json={"title": "A", "is_favorite": True})
    client.post("/api/pieces", json={"title": "B", "is_favorite": False})

    response = client.get("/api/pieces", params={"favorite": "true"})
    assert response.status_code == 200
    titles = [piece["title"] for piece in response.json()]
    assert titles == ["A"]


def test_create_piece_defaults_key_tempo_difficulty_instrument(client: TestClient) -> None:
    created = client.post("/api/pieces", json={"title": "Arabesque"}).json()
    assert created["key"] is None
    assert created["tempo_bpm"] is None
    assert created["difficulty"] is None
    assert created["instrument"] is None


def test_create_piece_with_key_tempo_difficulty_instrument(client: TestClient) -> None:
    payload = {
        "title": "Gymnopedie",
        "key": "D major",
        "tempo_bpm": 66,
        "difficulty": "intermediate",
        "instrument": "Piano",
    }
    created = client.post("/api/pieces", json=payload).json()
    assert created["key"] == "D major"
    assert created["tempo_bpm"] == 66
    assert created["difficulty"] == "intermediate"
    assert created["instrument"] == "Piano"


def test_create_piece_invalid_difficulty_422(client: TestClient) -> None:
    response = client.post("/api/pieces", json={"title": "Etude", "difficulty": "unknown"})
    assert response.status_code == 422


def test_update_piece_key_tempo_difficulty_instrument(client: TestClient) -> None:
    created = client.post("/api/pieces", json={"title": "Reverie"}).json()
    response = client.patch(
        f"/api/pieces/{created['id']}",
        json={
            "key": "B flat minor",
            "tempo_bpm": 120,
            "difficulty": "advanced",
            "instrument": "Classical guitar",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["key"] == "B flat minor"
    assert body["tempo_bpm"] == 120
    assert body["difficulty"] == "advanced"
    assert body["instrument"] == "Classical guitar"


def test_list_pieces_filter_by_difficulty(client: TestClient) -> None:
    client.post("/api/pieces", json={"title": "A", "difficulty": "beginner"})
    client.post("/api/pieces", json={"title": "B", "difficulty": "expert"})

    response = client.get("/api/pieces", params={"difficulty": "beginner"})
    assert response.status_code == 200
    titles = [piece["title"] for piece in response.json()]
    assert titles == ["A"]


def test_list_pieces_filter_by_difficulty_invalid_422(client: TestClient) -> None:
    response = client.get("/api/pieces", params={"difficulty": "unknown"})
    assert response.status_code == 422


def test_list_pieces_filter_by_instrument(client: TestClient) -> None:
    client.post("/api/pieces", json={"title": "A", "instrument": "Violin"})
    client.post("/api/pieces", json={"title": "B", "instrument": "Cello"})

    response = client.get("/api/pieces", params={"instrument": "Violin"})
    assert response.status_code == 200
    titles = [piece["title"] for piece in response.json()]
    assert titles == ["A"]
