from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pdf_fixtures import build_blank_pdf, build_simple_pdf

from repertoire.api import pieces as pieces_module
from repertoire.config import settings

TITLE_ONLY_PDF = build_simple_pdf([("Rhapsody in Blue", 24, 50, 700)])
TITLE_AND_COMPOSER_PDF = build_simple_pdf(
    [
        ("Rhapsody in Blue", 24, 50, 700),
        ("by George Gershwin", 12, 50, 670),
    ]
)
CONTENT_TITLE_AND_COMPOSER_PDF = build_simple_pdf(
    [
        ("Content Title", 24, 50, 700),
        ("by Content Composer", 12, 50, 670),
    ]
)
BLANK_PDF = build_blank_pdf()


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


def test_quick_upload_full_happy_path(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_find_composer = Mock(return_value="George Gershwin")
    monkeypatch.setattr(pieces_module, "find_composer_for_title", mock_find_composer)

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("rhapsody.pdf", TITLE_ONLY_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    piece = response.json()
    assert piece["title"] == "Rhapsody in Blue"
    assert piece["composer"] == "George Gershwin"
    assert piece["sheet_resource_kinds"] == ["uploaded"]
    mock_find_composer.assert_called_once_with("Rhapsody in Blue")

    stored_files = list(Path(settings.sheet_resource_storage_dir).glob("*.pdf"))
    assert len(stored_files) == 1


def test_quick_upload_extracted_composer_takes_precedence(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_find_composer = Mock(return_value="Should not be used")
    monkeypatch.setattr(pieces_module, "find_composer_for_title", mock_find_composer)

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("rhapsody.pdf", TITLE_AND_COMPOSER_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    piece = response.json()
    assert piece["title"] == "Rhapsody in Blue"
    assert piece["composer"] == "George Gershwin"
    mock_find_composer.assert_not_called()


def test_quick_upload_fallback_chain_uses_filename_stem(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pieces_module, "find_composer_for_title", Mock(return_value=None))

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("my_favorite_song.pdf", BLANK_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    piece = response.json()
    assert piece["title"] == "my_favorite_song"
    assert piece["composer"] is None


def test_quick_upload_filename_composer_wins_over_heuristic(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The filename follows the "Composer - Title" convention, so it should win
    # even though the PDF content also has a plausible (but different) guess.
    mock_find_composer = Mock(return_value="Should not be used")
    monkeypatch.setattr(pieces_module, "find_composer_for_title", mock_find_composer)

    response = client.post(
        "/api/pieces/quick-upload",
        files={
            "file": (
                "Filename Composer - Filename Title.pdf",
                CONTENT_TITLE_AND_COMPOSER_PDF,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201
    piece = response.json()
    assert piece["title"] == "Filename Title"
    assert piece["composer"] == "Filename Composer"
    mock_find_composer.assert_not_called()


def test_quick_upload_filename_without_composer_falls_through_to_heuristic(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_find_composer = Mock(return_value="Should not be used")
    monkeypatch.setattr(pieces_module, "find_composer_for_title", mock_find_composer)

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("myfile.pdf", CONTENT_TITLE_AND_COMPOSER_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    piece = response.json()
    assert piece["title"] == "Content Title"
    assert piece["composer"] == "Content Composer"
    mock_find_composer.assert_not_called()


def test_quick_upload_falls_through_to_musicbrainz_when_title_and_composer_signals_absent(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_find_composer = Mock(return_value="MusicBrainz Composer")
    monkeypatch.setattr(pieces_module, "find_composer_for_title", mock_find_composer)
    monkeypatch.setattr(
        pieces_module, "parse_composer_title_from_filename", lambda filename: (None, None)
    )

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("blank.pdf", BLANK_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    piece = response.json()
    assert piece["title"] == "Untitled piece"
    assert piece["composer"] == "MusicBrainz Composer"
    mock_find_composer.assert_called_once_with("Untitled piece")


def test_quick_upload_fallback_chain_untitled_piece_when_title_and_filename_absent(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pieces_module, "find_composer_for_title", Mock(return_value=None))
    monkeypatch.setattr(
        pieces_module, "parse_composer_title_from_filename", lambda filename: (None, None)
    )

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("blank.pdf", BLANK_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    piece = response.json()
    assert piece["title"] == "Untitled piece"
    assert piece["composer"] is None


def test_quick_upload_musicbrainz_degrades_gracefully(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pieces_module, "find_composer_for_title", Mock(return_value=None))

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("rhapsody.pdf", TITLE_ONLY_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    piece = response.json()
    assert piece["title"] == "Rhapsody in Blue"
    assert piece["composer"] is None


def test_quick_upload_wrong_content_type_415_creates_nothing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_find_composer = Mock()
    monkeypatch.setattr(pieces_module, "find_composer_for_title", mock_find_composer)
    before = client.get("/api/pieces").json()

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("notes.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 415
    assert client.get("/api/pieces").json() == before
    assert list(Path(settings.sheet_resource_storage_dir).iterdir()) == []
    mock_find_composer.assert_not_called()


def test_quick_upload_generates_thumbnail(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pieces_module, "find_composer_for_title", Mock(return_value=None))

    def _fake_thumbnail(pdf_path: Path) -> str:
        (pdf_path.parent / "thumb.png").write_bytes(b"fake-png-bytes")
        return "thumb.png"

    monkeypatch.setattr(pieces_module, "generate_pdf_thumbnail", _fake_thumbnail)

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("rhapsody.pdf", TITLE_ONLY_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    piece_id = response.json()["id"]
    resources = client.get("/api/sheet-resources", params={"piece_id": piece_id}).json()
    assert resources[0]["thumbnail_key"] == "thumb.png"


def test_quick_upload_thumbnail_failure_does_not_block_upload(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pieces_module, "find_composer_for_title", Mock(return_value=None))
    monkeypatch.setattr(pieces_module, "generate_pdf_thumbnail", lambda pdf_path: None)

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("rhapsody.pdf", TITLE_ONLY_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    piece_id = response.json()["id"]
    resources = client.get("/api/sheet-resources", params={"piece_id": piece_id}).json()
    assert resources[0]["thumbnail_key"] is None


def test_quick_upload_oversized_413_creates_nothing(client: TestClient) -> None:
    settings.sheet_resource_max_upload_bytes = 10
    before = client.get("/api/pieces").json()

    response = client.post(
        "/api/pieces/quick-upload",
        files={"file": ("rhapsody.pdf", TITLE_ONLY_PDF, "application/pdf")},
    )

    assert response.status_code == 413
    assert client.get("/api/pieces").json() == before
    assert list(Path(settings.sheet_resource_storage_dir).iterdir()) == []
