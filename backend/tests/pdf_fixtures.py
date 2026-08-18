"""Hand-built minimal single-page PDFs for exercising pdfplumber-based extraction
in tests, without adding a PDF-writing library as a dependency.
"""


def _escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def build_simple_pdf(lines: list[tuple[str, int, int, int]]) -> bytes:
    """Build a one-page, Letter-sized PDF with each line drawn via Tf/Td/Tj.

    `lines` is a list of (text, font_size, x, y) tuples in PDF user space
    (origin bottom-left), so a larger `y` is nearer the top of the page.
    """
    content_lines = [
        f"BT /F1 {size} Tf {x} {y} Td ({_escape(text)}) Tj ET" for text, size, x, y in lines
    ]
    content_stream = "\n".join(content_lines).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> "
        b"/MediaBox [0 0 612 792] /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length "
        + str(len(content_stream)).encode()
        + b" >>\nstream\n"
        + content_stream
        + b"\nendstream",
    ]

    buffer = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(buffer))
        buffer += f"{index} 0 obj\n".encode()
        buffer += body
        buffer += b"\nendobj\n"

    xref_offset = len(buffer)
    count = len(objects) + 1
    buffer += f"xref\n0 {count}\n".encode()
    buffer += b"0000000000 65535 f \n"
    for offset in offsets:
        buffer += f"{offset:010d} 00000 n \n".encode()
    buffer += f"trailer\n<< /Size {count} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()

    return bytes(buffer)


def build_blank_pdf() -> bytes:
    """A structurally valid single-page PDF with no text content at all."""
    return build_simple_pdf([])
