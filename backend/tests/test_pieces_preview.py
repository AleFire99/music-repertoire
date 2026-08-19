from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from repertoire.api import sheet_resources as sheet_resources_module
from repertoire.config import settings

MINIMAL_PDF = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"


@pytest.fixture(autouse=True)
def _sheet_resource_storage_settings(tmp_path: Path) -> Generator[None, None, None]:
    original_dir = settings.sheet_resource_storage_dir
    settings.sheet_resource_storage_dir = str(tmp_path)
    try:
        yield
    finally:
        settings.sheet_resource_storage_dir = original_dir


def _create_piece(client: TestClient, title: str) -> int:
    return client.post("/api/pieces", json={"title": title}).json()["id"]


def _upload(client: TestClient, piece_id: int, filename: str) -> dict:
    return client.post(
        "/api/sheet-resources/upload",
        data={"piece_id": piece_id},
        files={"file": (filename, MINIMAL_PDF, "application/pdf")},
    ).json()


def _stub_thumbnail(monkeypatch: pytest.MonkeyPatch, key: str = "thumb.png") -> None:
    def _generate(pdf_path: Path) -> str:
        (pdf_path.parent / key).write_bytes(b"fake-png-bytes")
        return key

    monkeypatch.setattr(sheet_resources_module, "generate_pdf_thumbnail", _generate)


def test_piece_without_uploads_has_no_preview(client: TestClient) -> None:
    piece_id = _create_piece(client, "Nocturne")
    response = client.get(f"/api/pieces/{piece_id}")
    assert response.json()["preview_sheet_resource_id"] is None


def test_piece_with_non_thumbnailed_upload_has_no_preview(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sheet_resources_module, "generate_pdf_thumbnail", lambda path: None)
    piece_id = _create_piece(client, "Nocturne")
    _upload(client, piece_id, "a.pdf")

    response = client.get(f"/api/pieces/{piece_id}")
    assert response.json()["preview_sheet_resource_id"] is None


def test_piece_with_thumbnailed_upload_has_preview(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_thumbnail(monkeypatch)
    piece_id = _create_piece(client, "Nocturne")
    uploaded = _upload(client, piece_id, "a.pdf")

    response = client.get(f"/api/pieces/{piece_id}")
    assert response.json()["preview_sheet_resource_id"] == uploaded["id"]


def test_piece_with_multiple_thumbnailed_uploads_picks_most_recent(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_thumbnail(monkeypatch)
    piece_id = _create_piece(client, "Nocturne")
    _upload(client, piece_id, "a.pdf")
    second = _upload(client, piece_id, "b.pdf")

    response = client.get(f"/api/pieces/{piece_id}")
    assert response.json()["preview_sheet_resource_id"] == second["id"]


def test_list_pieces_includes_preview_field(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_thumbnail(monkeypatch)
    piece_id = _create_piece(client, "Nocturne")
    uploaded = _upload(client, piece_id, "a.pdf")

    listed = client.get("/api/pieces").json()
    assert listed[0]["preview_sheet_resource_id"] == uploaded["id"]


def test_piece_with_only_non_uploaded_resources_has_no_preview(client: TestClient) -> None:
    piece_id = _create_piece(client, "Nocturne")
    client.post(
        "/api/sheet-resources",
        json={"piece_id": piece_id, "kind": "url", "reference": "https://example.com"},
    )

    response = client.get(f"/api/pieces/{piece_id}")
    assert response.json()["preview_sheet_resource_id"] is None
