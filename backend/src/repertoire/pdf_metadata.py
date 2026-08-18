import io
import re
from dataclasses import dataclass

import pdfplumber

TOP_FRACTION = 0.4
LINE_TOLERANCE = 2.0
MAX_COMPOSER_LINE_LENGTH = 60
COMPOSER_LOOKAHEAD_LINES = 3

TEMPO_MARKINGS = {
    "adagio",
    "allegretto",
    "allegro",
    "andante",
    "andantino",
    "grave",
    "largo",
    "larghetto",
    "lento",
    "maestoso",
    "moderato",
    "presto",
    "prestissimo",
    "sostenuto",
    "vivace",
}

COMPOSER_PREFIX_RE = re.compile(r"^(?:by|arr\.?|arranged by|music by)\s+(.+)$", re.IGNORECASE)


@dataclass
class _Line:
    text: str
    font_size: float
    top: float


def _lines_from_chars(chars: list[dict]) -> list[_Line]:
    printable = [c for c in chars if c.get("text", "") != ""]
    if not printable:
        return []
    printable.sort(key=lambda c: (c["top"], c["x0"]))

    groups: list[list[dict]] = []
    current: list[dict] = []
    current_top: float | None = None
    for ch in printable:
        if current_top is None or abs(ch["top"] - current_top) <= LINE_TOLERANCE:
            current.append(ch)
            current_top = ch["top"] if current_top is None else current_top
        else:
            groups.append(current)
            current = [ch]
            current_top = ch["top"]
    if current:
        groups.append(current)

    lines = []
    for group in groups:
        group.sort(key=lambda c: c["x0"])
        text = "".join(c["text"] for c in group).strip()
        if not text:
            continue
        lines.append(
            _Line(
                text=text,
                font_size=max(c["size"] for c in group),
                top=min(c["top"] for c in group),
            )
        )
    return lines


def _looks_like_tempo_marking(text: str) -> bool:
    return text.strip().lower().rstrip(".") in TEMPO_MARKINGS


def _guess_composer(lines: list[_Line], title_index: int) -> str | None:
    lookahead = lines[title_index + 1 : title_index + 1 + COMPOSER_LOOKAHEAD_LINES]
    for line in lookahead:
        text = line.text.strip()
        match = COMPOSER_PREFIX_RE.match(text)
        if match:
            return match.group(1).strip()
        if _looks_like_tempo_marking(text):
            continue
        if len(text) <= MAX_COMPOSER_LINE_LENGTH:
            return text
    return None


def extract_title_and_composer(pdf_bytes: bytes) -> tuple[str | None, str | None]:
    """Best-effort page-1 title/composer guess from the PDF text layer.

    Never raises: scanned PDFs (no text layer) or unparseable files return (None, None).
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if not pdf.pages:
                return None, None
            page = pdf.pages[0]
            lines = _lines_from_chars(page.chars)
            page_height = page.height
    except Exception:
        return None, None

    if not lines:
        return None, None

    top_region_limit = page_height * TOP_FRACTION
    candidates = [line for line in lines if line.top <= top_region_limit]
    if not candidates:
        return None, None

    title_line = max(candidates, key=lambda line: line.font_size)
    title_index = lines.index(title_line)
    composer = _guess_composer(lines, title_index)

    return title_line.text, composer
