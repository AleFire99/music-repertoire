from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from repertoire.config import settings

MINIMAL_PDF = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"


def _create_piece(client: TestClient, title: str) -> int:
    return client.post("/api/pieces", json={"title": title}).json()["id"]


@pytest.fixture(autouse=True)
def _sheet_resource_storage_settings(tmp_path: Path) -> Generator[None, None, None]:
    original_dir = settings.sheet_resource_storage_dir
    original_max_bytes = settings.sheet_resource_max_upload_bytes
    settings.sheet_resource_storage_dir = str(tmp_path)
    try:
        yield
    finally:
        settings.sheet_resource_storage_dir = original_dir
        settings.sheet_resource_max_upload_bytes = original_max_bytes


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


def test_upload_sheet_resource_stores_file_and_metadata(client: TestClient) -> None:
    piece_id = _create_piece(client, "Prelude")

    response = client.post(
        "/api/sheet-resources/upload",
        data={"piece_id": piece_id, "label": "MuseScore export"},
        files={"file": ("prelude.pdf", MINIMAL_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    resource = response.json()
    assert resource["kind"] == "uploaded"
    assert resource["piece_id"] == piece_id
    assert resource["original_filename"] == "prelude.pdf"
    assert resource["content_type"] == "application/pdf"
    assert resource["file_size_bytes"] == len(MINIMAL_PDF)
    assert "storage_key" not in resource

    stored_files = list(Path(settings.sheet_resource_storage_dir).iterdir())
    assert len(stored_files) == 1
    assert stored_files[0].read_bytes() == MINIMAL_PDF


def test_upload_sheet_resource_missing_piece_404(client: TestClient) -> None:
    response = client.post(
        "/api/sheet-resources/upload",
        data={"piece_id": 999999},
        files={"file": ("prelude.pdf", MINIMAL_PDF, "application/pdf")},
    )
    assert response.status_code == 404


def test_upload_sheet_resource_wrong_content_type_415(client: TestClient) -> None:
    piece_id = _create_piece(client, "Prelude")

    response = client.post(
        "/api/sheet-resources/upload",
        data={"piece_id": piece_id},
        files={"file": ("prelude.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 415
    assert list(Path(settings.sheet_resource_storage_dir).iterdir()) == []


def test_upload_sheet_resource_oversized_413(client: TestClient) -> None:
    piece_id = _create_piece(client, "Prelude")
    settings.sheet_resource_max_upload_bytes = 10

    response = client.post(
        "/api/sheet-resources/upload",
        data={"piece_id": piece_id},
        files={"file": ("prelude.pdf", MINIMAL_PDF, "application/pdf")},
    )

    assert response.status_code == 413
    assert list(Path(settings.sheet_resource_storage_dir).iterdir()) == []


def test_download_uploaded_sheet_resource(client: TestClient) -> None:
    piece_id = _create_piece(client, "Prelude")
    uploaded = client.post(
        "/api/sheet-resources/upload",
        data={"piece_id": piece_id},
        files={"file": ("prelude.pdf", MINIMAL_PDF, "application/pdf")},
    ).json()

    response = client.get(f"/api/sheet-resources/{uploaded['id']}/file")

    assert response.status_code == 200
    assert response.content == MINIMAL_PDF
    assert response.headers["content-type"] == "application/pdf"
    assert 'filename="prelude.pdf"' in response.headers["content-disposition"]


def test_download_sheet_resource_missing_404(client: TestClient) -> None:
    response = client.get("/api/sheet-resources/999999/file")
    assert response.status_code == 404


def test_download_non_uploaded_sheet_resource_404(client: TestClient) -> None:
    piece_id = _create_piece(client, "Prelude")
    created = client.post(
        "/api/sheet-resources",
        json={"piece_id": piece_id, "kind": "url", "reference": "https://example.com"},
    ).json()

    response = client.get(f"/api/sheet-resources/{created['id']}/file")
    assert response.status_code == 404


def test_delete_uploaded_sheet_resource_removes_file(client: TestClient) -> None:
    piece_id = _create_piece(client, "Prelude")
    uploaded = client.post(
        "/api/sheet-resources/upload",
        data={"piece_id": piece_id},
        files={"file": ("prelude.pdf", MINIMAL_PDF, "application/pdf")},
    ).json()
    assert len(list(Path(settings.sheet_resource_storage_dir).iterdir())) == 1

    delete_response = client.delete(f"/api/sheet-resources/{uploaded['id']}")
    assert delete_response.status_code == 204

    assert list(Path(settings.sheet_resource_storage_dir).iterdir()) == []
