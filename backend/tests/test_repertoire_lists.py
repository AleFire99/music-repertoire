from fastapi.testclient import TestClient


def _create_piece(client: TestClient, title: str) -> int:
    return client.post("/api/pieces", json={"title": title}).json()["id"]


def _create_list(client: TestClient, name: str) -> int:
    return client.post("/api/repertoire-lists", json={"name": name}).json()["id"]


def test_create_and_list_repertoire_lists(client: TestClient) -> None:
    response = client.post("/api/repertoire-lists", json={"name": "Recital 2026"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Recital 2026"
    assert body["piece_count"] == 0

    list_response = client.get("/api/repertoire-lists")
    assert list_response.status_code == 200
    assert [lst["id"] for lst in list_response.json()] == [body["id"]]


def test_rename_repertoire_list(client: TestClient) -> None:
    list_id = _create_list(client, "Currently working on")

    response = client.patch(f"/api/repertoire-lists/{list_id}", json={"name": "Audition pieces"})
    assert response.status_code == 200
    assert response.json()["name"] == "Audition pieces"

    get_response = client.get(f"/api/repertoire-lists/{list_id}")
    assert get_response.json()["name"] == "Audition pieces"


def test_rename_missing_repertoire_list_404(client: TestClient) -> None:
    response = client.patch("/api/repertoire-lists/999999", json={"name": "x"})
    assert response.status_code == 404


def test_delete_repertoire_list(client: TestClient) -> None:
    list_id = _create_list(client, "Temp list")

    delete_response = client.delete(f"/api/repertoire-lists/{list_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/repertoire-lists/{list_id}")
    assert get_response.status_code == 404


def test_delete_missing_repertoire_list_404(client: TestClient) -> None:
    response = client.delete("/api/repertoire-lists/999999")
    assert response.status_code == 404


def test_add_and_remove_piece_from_list(client: TestClient) -> None:
    list_id = _create_list(client, "Recital 2026")
    piece_id = _create_piece(client, "Clair de Lune")

    add_response = client.post(
        f"/api/repertoire-lists/{list_id}/pieces", json={"piece_id": piece_id}
    )
    assert add_response.status_code == 201
    detail = add_response.json()
    assert [p["id"] for p in detail["pieces"]] == [piece_id]

    summary = client.get("/api/repertoire-lists").json()[0]
    assert summary["piece_count"] == 1

    remove_response = client.delete(f"/api/repertoire-lists/{list_id}/pieces/{piece_id}")
    assert remove_response.status_code == 204

    get_response = client.get(f"/api/repertoire-lists/{list_id}")
    assert get_response.json()["pieces"] == []


def test_add_piece_missing_piece_404(client: TestClient) -> None:
    list_id = _create_list(client, "Recital 2026")
    response = client.post(f"/api/repertoire-lists/{list_id}/pieces", json={"piece_id": 999999})
    assert response.status_code == 404


def test_add_piece_missing_list_404(client: TestClient) -> None:
    piece_id = _create_piece(client, "Etude")
    response = client.post("/api/repertoire-lists/999999/pieces", json={"piece_id": piece_id})
    assert response.status_code == 404


def test_add_piece_twice_is_idempotent(client: TestClient) -> None:
    list_id = _create_list(client, "Recital 2026")
    piece_id = _create_piece(client, "Ballade")

    first = client.post(f"/api/repertoire-lists/{list_id}/pieces", json={"piece_id": piece_id})
    assert first.status_code == 201
    second = client.post(f"/api/repertoire-lists/{list_id}/pieces", json={"piece_id": piece_id})
    assert second.status_code == 201
    assert [p["id"] for p in second.json()["pieces"]] == [piece_id]


def test_remove_piece_not_on_list_404(client: TestClient) -> None:
    list_id = _create_list(client, "Recital 2026")
    piece_id = _create_piece(client, "Nocturne")
    response = client.delete(f"/api/repertoire-lists/{list_id}/pieces/{piece_id}")
    assert response.status_code == 404


def test_piece_can_be_on_multiple_lists(client: TestClient) -> None:
    list_a = _create_list(client, "Recital 2026")
    list_b = _create_list(client, "Audition pieces")
    piece_id = _create_piece(client, "Sonata")

    client.post(f"/api/repertoire-lists/{list_a}/pieces", json={"piece_id": piece_id})
    client.post(f"/api/repertoire-lists/{list_b}/pieces", json={"piece_id": piece_id})

    assert [p["id"] for p in client.get(f"/api/repertoire-lists/{list_a}").json()["pieces"]] == [
        piece_id
    ]
    assert [p["id"] for p in client.get(f"/api/repertoire-lists/{list_b}").json()["pieces"]] == [
        piece_id
    ]


def test_deleting_piece_removes_it_from_lists_without_deleting_list(client: TestClient) -> None:
    list_id = _create_list(client, "Recital 2026")
    piece_id = _create_piece(client, "Ballade")
    client.post(f"/api/repertoire-lists/{list_id}/pieces", json={"piece_id": piece_id})

    delete_response = client.delete(f"/api/pieces/{piece_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/repertoire-lists/{list_id}")
    assert get_response.status_code == 200
    assert get_response.json()["pieces"] == []


def test_deleting_list_does_not_delete_its_pieces(client: TestClient) -> None:
    list_id = _create_list(client, "Recital 2026")
    piece_id = _create_piece(client, "Ballade")
    client.post(f"/api/repertoire-lists/{list_id}/pieces", json={"piece_id": piece_id})

    delete_response = client.delete(f"/api/repertoire-lists/{list_id}")
    assert delete_response.status_code == 204

    piece_response = client.get(f"/api/pieces/{piece_id}")
    assert piece_response.status_code == 200
