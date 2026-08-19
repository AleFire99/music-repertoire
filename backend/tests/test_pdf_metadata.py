from pdf_fixtures import build_blank_pdf, build_simple_pdf

from repertoire.pdf_metadata import extract_title_and_composer, parse_composer_title_from_filename


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


def test_duplicate_overlapping_glyphs_are_deduped() -> None:
    # Reproduces the faux-bold export bug: the same title string drawn twice at
    # (near-)identical coordinates, which without dedup concatenates into
    # "RRiiivveerr..."-style garbage instead of readable text.
    pdf = build_simple_pdf(
        [
            ("River flows in you", 24, 50, 700),
            ("River flows in you", 24, 50, 700),
        ]
    )
    title, composer = extract_title_and_composer(pdf)
    assert title == "River flows in you"
    assert composer is None


def test_symbol_only_line_rejected_as_implausible_title() -> None:
    # Stand-in for a bare music-font glyph (e.g. a Private Use Area codepoint):
    # a large-font line with no letters at all should be rejected as a title
    # guess rather than trusted just because it's the largest font on the page.
    pdf = build_simple_pdf([("###///", 32, 50, 700), ("Actual Title", 18, 50, 660)])
    title, composer = extract_title_and_composer(pdf)
    assert title == "Actual Title"


def test_normal_title_passes_plausibility_filter() -> None:
    pdf = build_simple_pdf([("Clair de Lune", 24, 50, 700)])
    title, _composer = extract_title_and_composer(pdf)
    assert title == "Clair de Lune"


def test_parse_composer_title_from_filename_splits_on_space_hyphen_space() -> None:
    composer, title = parse_composer_title_from_filename("Debussy - Clair de lune.pdf")
    assert composer == "Debussy"
    assert title == "Clair de lune"


def test_parse_composer_title_from_filename_handles_en_and_em_dash() -> None:
    composer, title = parse_composer_title_from_filename("Chopin – Nocturne.pdf")
    assert composer == "Chopin"
    assert title == "Nocturne"

    composer, title = parse_composer_title_from_filename("Chopin — Nocturne.pdf")
    assert composer == "Chopin"
    assert title == "Nocturne"


def test_parse_composer_title_from_filename_compound_hyphens_not_split() -> None:
    composer, title = parse_composer_title_from_filename(
        "bach-aria-quarta-corda-facile-piano.pdf"
    )
    assert composer is None
    assert title == "bach-aria-quarta-corda-facile-piano"


def test_parse_composer_title_from_filename_multi_composer_string_passes_through() -> None:
    composer, title = parse_composer_title_from_filename("Gounod, Bach - Ave Maria.pdf")
    assert composer == "Gounod, Bach"
    assert title == "Ave Maria"


def test_parse_composer_title_from_filename_no_separator_falls_back_to_stem() -> None:
    composer, title = parse_composer_title_from_filename("Il mio primo Chopin.pdf")
    assert composer is None
    assert title == "Il mio primo Chopin"


def test_parse_composer_title_from_filename_blank_or_missing() -> None:
    assert parse_composer_title_from_filename(None) == (None, None)
    assert parse_composer_title_from_filename("") == (None, None)
    assert parse_composer_title_from_filename("   ") == (None, None)
