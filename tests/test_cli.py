import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "nospc.py"


def run_cli(args, input_text=None):
    result = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        input=input_text,
        text=True,
        capture_output=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0
    return result.stdout.strip().splitlines()


def test_cli_file(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("a\u00A0b\n", encoding="utf-8")
    output = run_cli([str(sample)])
    assert output == [f"{sample}:1:a[U+00A0 NO-BREAK SPACE]b"]


def test_cli_stdin():
    output = run_cli(["-"], input_text="x\u00A0y\n")
    assert output == ["-:1:x[U+00A0 NO-BREAK SPACE]y"]


def test_cli_multiple_non_standard_whitespaces(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("A\u00A0B\u2002C\n", encoding="utf-8")
    output = run_cli([str(sample)])
    assert output == [f"{sample}:1:A[U+00A0 NO-BREAK SPACE]B[U+2002 EN SPACE]C"]


def test_cli_standard_whitespace_ignored(tmp_path):
    sample = tmp_path / "spaces.txt"
    sample.write_text(" \t\n", encoding="utf-8")
    output = run_cli([str(sample)])
    assert output == []


def test_cli_color_output_with_termcolor(tmp_path):
    import pytest
    pytest.importorskip("termcolor")
    sample = tmp_path / "color.txt"
    sample.write_text("a\u00A0b\n", encoding="utf-8")
    output = run_cli([str(sample), "--color"])
    assert any("\x1b[" in line for line in output)


def test_cli_color_output_without_termcolor(tmp_path):
    import importlib.util
    import pytest
    if importlib.util.find_spec("termcolor") is not None:
        pytest.skip("termcolor installed")
    sample = tmp_path / "color.txt"
    sample.write_text("a\u00A0b\n", encoding="utf-8")
    output = run_cli([str(sample), "--color"])
    assert output == [f"{sample}:1:a\u00A0b"]


def test_cli_color_and_bracket_combined(tmp_path):
    import importlib.util
    sample = tmp_path / "combo.txt"
    sample.write_text("a\u00A0b\n", encoding="utf-8")
    output = run_cli([str(sample), "--color", "--bracket"])
    line = output[0]
    assert "[U+00A0 NO-BREAK SPACE]" in line
    if importlib.util.find_spec("termcolor") is not None:
        assert "\x1b[" in line


def test_cli_recursive_directory_processing(tmp_path):
    root = tmp_path / "dir"
    sub = root / "sub"
    sub.mkdir(parents=True)
    file = sub / "sample.txt"
    file.write_text("x\u00A0y\n", encoding="utf-8")
    output = run_cli(["-r", str(root)])
    assert output == [f"{file}:1:x[U+00A0 NO-BREAK SPACE]y"]


def test_cli_directory_without_recursive_option(tmp_path):
    root = tmp_path / "dir"
    root.mkdir()
    output = run_cli([str(root)])
    assert output == [f"{root}: is not a regular file."]


def test_cli_binary_file(tmp_path):
    binary = tmp_path / "data.bin"
    binary.write_bytes(b"\x00\xff\x00")
    output = run_cli([str(binary)])
    assert output == [f"{binary}: is binary file."]


def test_cli_stdin_with_options():
    import importlib.util
    output = run_cli(["-", "--color", "--bracket"], input_text="x\u00A0y\n")
    line = output[0]
    assert "[U+00A0 NO-BREAK SPACE]" in line
    if importlib.util.find_spec("termcolor") is not None:
        assert "\x1b[" in line


def test_cli_nonexistent_path_error(tmp_path):
    missing = tmp_path / "missing.txt"
    output = run_cli([str(missing)])
    assert output[0].startswith(f"{missing}: could not be processed.")
