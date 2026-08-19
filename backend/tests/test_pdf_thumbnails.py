import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from repertoire.pdf_upload import generate_pdf_thumbnail


def _fake_successful_run(cmd: list[str], **kwargs: object) -> Mock:
    output_prefix = Path(cmd[-1])
    (output_prefix.parent / f"{output_prefix.name}.png").write_bytes(b"fake-png-bytes")
    return Mock(returncode=0)


def test_generate_pdf_thumbnail_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pdf_path = tmp_path / "piece.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")
    monkeypatch.setattr("repertoire.pdf_upload.subprocess.run", _fake_successful_run)

    thumbnail_key = generate_pdf_thumbnail(pdf_path)

    assert thumbnail_key is not None
    assert thumbnail_key.endswith(".png")
    assert (tmp_path / thumbnail_key).is_file()


def test_generate_pdf_thumbnail_missing_binary_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf_path = tmp_path / "piece.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    def _raise_missing(cmd: list[str], **kwargs: object) -> None:
        raise FileNotFoundError("pdftoppm not found")

    monkeypatch.setattr("repertoire.pdf_upload.subprocess.run", _raise_missing)

    assert generate_pdf_thumbnail(pdf_path) is None
    assert list(tmp_path.iterdir()) == [pdf_path]


def test_generate_pdf_thumbnail_corrupt_pdf_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf_path = tmp_path / "piece.pdf"
    pdf_path.write_bytes(b"not really a pdf")

    def _raise_called_process_error(cmd: list[str], **kwargs: object) -> None:
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr("repertoire.pdf_upload.subprocess.run", _raise_called_process_error)

    assert generate_pdf_thumbnail(pdf_path) is None


def test_generate_pdf_thumbnail_timeout_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf_path = tmp_path / "piece.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    def _raise_timeout(cmd: list[str], **kwargs: object) -> None:
        raise subprocess.TimeoutExpired(cmd, 15)

    monkeypatch.setattr("repertoire.pdf_upload.subprocess.run", _raise_timeout)

    assert generate_pdf_thumbnail(pdf_path) is None
