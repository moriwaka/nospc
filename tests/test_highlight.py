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


def test_standard_whitespace_ignored():
    line = " \t"
    highlighted, found = nospc.highlight_non_standard_whitespace(line, False, True)
    assert not found
    assert highlighted == " \t"
