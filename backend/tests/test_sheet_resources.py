from fastapi.testclient import TestClient


def _create_piece(client: TestClient, title: str) -> int:
    return client.post("/api/pieces", json={"title": title}).json()["id"]


def test_create_and_list_sheet_resource(client: TestClient) -> None:
    piece_id = _create_piece(client, "Clair de Lune")
    payload = {
        "piece_id": piece_id,
        "kind": "url",
        "reference": "https://example.com/clair-de-lune.pdf",
        "label": "IMSLP edition",
        "notes": "Public domain scan",
    }
    create_response = client.post("/api/sheet-resources", json=payload)
    assert create_response.status_code == 201
    resource = create_response.json()
    assert resource["piece_id"] == piece_id
    assert resource["kind"] == "url"
    assert resource["reference"] == "https://example.com/clair-de-lune.pdf"
    assert resource["label"] == "IMSLP edition"
    assert resource["notes"] == "Public domain scan"

    list_response = client.get("/api/sheet-resources")
    assert list_response.status_code == 200
    assert [r["id"] for r in list_response.json()] == [resource["id"]]


def test_create_sheet_resource_physical_and_local_doc_kinds(client: TestClient) -> None:
    piece_id = _create_piece(client, "Etude")

    physical = client.post(
        "/api/sheet-resources",
        json={"piece_id": piece_id, "kind": "physical", "reference": "Chopin Etudes, p. 12"},
    )
    assert physical.status_code == 201
    assert physical.json()["kind"] == "physical"

    local_doc = client.post(
        "/api/sheet-resources",
        json={"piece_id": piece_id, "kind": "local-doc", "reference": "/scores/etude.pdf"},
    )
    assert local_doc.status_code == 201
    assert local_doc.json()["kind"] == "local-doc"


def test_create_sheet_resource_missing_piece_404(client: TestClient) -> None:
    payload = {"piece_id": 999999, "kind": "url", "reference": "https://example.com"}
    response = client.post("/api/sheet-resources", json=payload)
    assert response.status_code == 404


def test_create_sheet_resource_invalid_kind_422(client: TestClient) -> None:
    piece_id = _create_piece(client, "Sonata")
    payload = {"piece_id": piece_id, "kind": "pdf", "reference": "https://example.com"}
    response = client.post("/api/sheet-resources", json=payload)
    assert response.status_code == 422


def test_list_sheet_resources_filter_by_piece(client: TestClient) -> None:
    piece_a = _create_piece(client, "A")
    piece_b = _create_piece(client, "B")
    client.post(
        "/api/sheet-resources",
        json={"piece_id": piece_a, "kind": "url", "reference": "https://example.com/a"},
    )
    client.post(
        "/api/sheet-resources",
        json={"piece_id": piece_b, "kind": "url", "reference": "https://example.com/b"},
    )

    response = client.get("/api/sheet-resources", params={"piece_id": piece_a})
    assert response.status_code == 200
    resources = response.json()
    assert len(resources) == 1
    assert resources[0]["piece_id"] == piece_a


def test_list_sheet_resources_empty(client: TestClient) -> None:
    response = client.get("/api/sheet-resources")
    assert response.status_code == 200
    assert response.json() == []


def test_delete_sheet_resource(client: TestClient) -> None:
    piece_id = _create_piece(client, "Nocturne")
    created = client.post(
        "/api/sheet-resources",
        json={"piece_id": piece_id, "kind": "url", "reference": "https://example.com"},
    ).json()

    delete_response = client.delete(f"/api/sheet-resources/{created['id']}")
    assert delete_response.status_code == 204

    list_response = client.get("/api/sheet-resources")
    assert list_response.json() == []


def test_delete_sheet_resource_missing_404(client: TestClient) -> None:
    response = client.delete("/api/sheet-resources/999999")
    assert response.status_code == 404


def test_deleting_piece_cascades_to_sheet_resources(client: TestClient) -> None:
    piece_id = _create_piece(client, "Ballade")
    client.post(
        "/api/sheet-resources",
        json={"piece_id": piece_id, "kind": "url", "reference": "https://example.com"},
    )

    delete_response = client.delete(f"/api/pieces/{piece_id}")
    assert delete_response.status_code == 204

    list_response = client.get("/api/sheet-resources", params={"piece_id": piece_id})
    assert list_response.status_code == 200
    assert list_response.json() == []
