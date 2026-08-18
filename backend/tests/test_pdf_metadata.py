from pdf_fixtures import build_blank_pdf, build_simple_pdf

from repertoire.pdf_metadata import extract_title_and_composer


def test_extract_title_by_font_size() -> None:
    pdf = build_simple_pdf(
        [
            ("Clair de Lune", 24, 50, 700),
            ("A short subtitle", 10, 50, 670),
        ]
    )
    title, composer = extract_title_and_composer(pdf)
    assert title == "Clair de Lune"
    assert composer == "A short subtitle"


def test_extract_composer_prefix_match() -> None:
    pdf = build_simple_pdf(
        [
            ("Clair de Lune", 24, 50, 700),
            ("by Claude Debussy", 12, 50, 670),
        ]
    )
    title, composer = extract_title_and_composer(pdf)
    assert title == "Clair de Lune"
    assert composer == "Claude Debussy"


def test_tempo_marking_rejected_as_composer() -> None:
    pdf = build_simple_pdf(
        [
            ("Moonlight Sonata", 24, 50, 700),
            ("Allegro", 12, 50, 670),
            ("Ludwig van Beethoven", 12, 50, 650),
        ]
    )
    title, composer = extract_title_and_composer(pdf)
    assert title == "Moonlight Sonata"
    assert composer == "Ludwig van Beethoven"


def test_no_text_layer_bails_out() -> None:
    pdf = build_blank_pdf()
    title, composer = extract_title_and_composer(pdf)
    assert title is None
    assert composer is None


def test_corrupt_pdf_bails_out() -> None:
    title, composer = extract_title_and_composer(b"this is not a pdf file")
    assert title is None
    assert composer is None


def test_title_outside_top_region_is_ignored() -> None:
    pdf = build_simple_pdf([("Buried in the footer", 24, 50, 40)])
    title, composer = extract_title_and_composer(pdf)
    assert title is None
    assert composer is None
