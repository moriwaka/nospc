import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import nospc


def test_leading_nbsp_detected():
    line = "\u00A0Hello"
    highlighted, found = nospc.highlight_non_standard_whitespace(line, False, True)
    assert found
    assert highlighted.startswith("[U+00A0 NO-BREAK SPACE]Hello")


def test_trailing_nbsp_detected():
    line = "World\u00A0"
    highlighted, found = nospc.highlight_non_standard_whitespace(line, False, True)
    assert found
    assert highlighted.endswith("World[U+00A0 NO-BREAK SPACE]")


def test_multiple_non_standard_whitespaces_detected():
    line = "a\u00A0b\u2002c"
    highlighted, found = nospc.highlight_non_standard_whitespace(line, False, True)
    assert found
    assert highlighted == "a[U+00A0 NO-BREAK SPACE]b[U+2002 EN SPACE]c"


def test_zero_width_space_detected():
    line = "a\u200Bb"
    highlighted, found = nospc.highlight_non_standard_whitespace(line, False, True)
    assert found
    assert highlighted == "a[U+200B ZERO WIDTH SPACE]b"


def test_zero_width_no_break_space_detected():
    line = "a\uFEFFb"
    highlighted, found = nospc.highlight_non_standard_whitespace(line, False, True)
    assert found
    assert highlighted == "a[U+FEFF ZERO WIDTH NO-BREAK SPACE]b"


def test_unnamed_non_standard_whitespace_detected():
    line = "a\vb"
    highlighted, found = nospc.highlight_non_standard_whitespace(line, False, True)
    assert found
    assert highlighted == "a[U+000B VERTICAL TAB]b"


def test_ascii_control_separator_names_are_mapped():
    line = "a\x1cb\x1dc\x1ed\x1fe"
    highlighted, found = nospc.highlight_non_standard_whitespace(line, False, True)
    assert found
    assert highlighted == (
        "a[U+001C FILE SEPARATOR]b"
        "[U+001D GROUP SEPARATOR]c"
        "[U+001E RECORD SEPARATOR]d"
        "[U+001F UNIT SEPARATOR]e"
    )


def test_standard_whitespace_ignored():
    line = " \t"
    highlighted, found = nospc.highlight_non_standard_whitespace(line, False, True)
    assert not found
    assert highlighted == " \t"
