import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "nospc.py"


def run_cli(args, input_text=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        input=input_text,
        text=True,
        capture_output=True,
        cwd=REPO_ROOT,
    )


def run_cli_bytes(args, input_bytes=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        input=input_bytes,
        capture_output=True,
        cwd=REPO_ROOT,
    )


def test_cli_file(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("a\u00A0b\n", encoding="utf-8")
    result = run_cli([str(sample)])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == [f"{sample}:1:a[U+00A0 NO-BREAK SPACE]b"]


def test_cli_stdin():
    result = run_cli(["-"], input_text="x\u00A0y\n")
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == ["-:1:x[U+00A0 NO-BREAK SPACE]y"]


def test_cli_multiple_non_standard_whitespaces(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("A\u00A0B\u2002C\n", encoding="utf-8")
    result = run_cli([str(sample)])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == [f"{sample}:1:A[U+00A0 NO-BREAK SPACE]B[U+2002 EN SPACE]C"]


def test_cli_zero_width_space(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("a\u200Bb\n", encoding="utf-8")
    result = run_cli([str(sample)])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == [f"{sample}:1:a[U+200B ZERO WIDTH SPACE]b"]


def test_cli_utf8_bom_is_reported(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("\uFEFFabc\n", encoding="utf-8")
    result = run_cli([str(sample)])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == [f"{sample}:1:[U+FEFF ZERO WIDTH NO-BREAK SPACE]abc"]


def test_cli_unnamed_non_standard_whitespace(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("A\vB\n", encoding="utf-8")
    result = run_cli([str(sample)])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == [f"{sample}:1:A[U+000B VERTICAL TAB]B"]


def test_cli_standard_whitespace_ignored(tmp_path):
    sample = tmp_path / "spaces.txt"
    sample.write_text(" \t\n", encoding="utf-8")
    result = run_cli([str(sample)])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == []


def test_cli_carriage_return_is_reported_but_line_feed_is_not(tmp_path):
    sample = tmp_path / "crlf.txt"
    sample.write_bytes(b"a\r\nb\r")
    result = run_cli([str(sample)])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == [
        f"{sample}:1:a[U+000D CARRIAGE RETURN]",
        f"{sample}:2:b[U+000D CARRIAGE RETURN]",
    ]


def test_cli_crlf_option_ignores_cr_only_in_crlf_endings(tmp_path):
    sample = tmp_path / "crlf.txt"
    sample.write_bytes(b"a\r\nb\r")
    result = run_cli(["--crlf", str(sample)])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == [f"{sample}:2:b[U+000D CARRIAGE RETURN]"]


def test_cli_color_output_without_termcolor(tmp_path):
    import importlib.util
    import pytest
    if importlib.util.find_spec("termcolor") is not None:
        pytest.skip("termcolor installed")
    sample = tmp_path / "color.txt"
    sample.write_text("a\u00A0b\n", encoding="utf-8")
    result = run_cli([str(sample), "--color"])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == [f"{sample}:1:a\u00A0b"]


def test_cli_recursive_directory_processing(tmp_path):
    root = tmp_path / "dir"
    sub = root / "sub"
    sub.mkdir(parents=True)
    file = sub / "sample.txt"
    file.write_text("x\u00A0y\n", encoding="utf-8")
    result = run_cli(["-r", str(root)])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == [f"{file}:1:x[U+00A0 NO-BREAK SPACE]y"]


def test_cli_directory_without_recursive_option(tmp_path):
    root = tmp_path / "dir"
    root.mkdir()
    result = run_cli([str(root)])
    assert result.returncode == 1
    assert result.stdout == ""
    output = result.stderr.strip().splitlines()
    assert output == [f"{root}: is not a regular file."]


def test_cli_binary_file(tmp_path):
    binary = tmp_path / "data.bin"
    binary.write_bytes(b"\x00\xff\x00")
    result = run_cli([str(binary)])
    assert result.returncode == 1
    assert result.stdout == ""
    output = result.stderr.strip().splitlines()
    assert output == [f"{binary}: is not valid UTF-8 text."]


def test_cli_non_utf8_text_is_reported_as_binary(tmp_path):
    non_utf8 = tmp_path / "latin1.txt"
    non_utf8.write_bytes(b"a\xa0b\n")
    result = run_cli([str(non_utf8)])
    assert result.returncode == 1
    assert result.stdout == ""
    output = result.stderr.strip().splitlines()
    assert output == [f"{non_utf8}: is not valid UTF-8 text."]


def test_cli_non_utf8_stdin_is_reported_as_binary():
    result = run_cli_bytes(["-"], input_bytes=b"a\xa0b\n")
    assert result.returncode == 1
    assert result.stdout == b""
    output = result.stderr.decode("utf-8").strip().splitlines()
    assert output == ["-: is not valid UTF-8 text."]



def test_cli_nonexistent_path_error(tmp_path):
    missing = tmp_path / "missing.txt"
    result = run_cli([str(missing)])
    assert result.returncode == 1
    assert result.stdout == ""
    output = result.stderr.strip().splitlines()
    assert output[0].startswith(f"{missing}: could not be processed.")


def test_cli_returns_error_when_any_input_fails(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("a\u00A0b\n", encoding="utf-8")
    missing = tmp_path / "missing.txt"
    result = run_cli([str(sample), str(missing)])
    assert result.returncode == 1
    assert result.stdout.strip().splitlines() == [f"{sample}:1:a[U+00A0 NO-BREAK SPACE]b"]
    assert result.stderr.strip().splitlines()[0].startswith(f"{missing}: could not be processed.")
