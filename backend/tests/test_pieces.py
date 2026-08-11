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


def test_get_missing_piece_404(client: TestClient) -> None:
    response = client.get("/api/pieces/999999")
    assert response.status_code == 404
