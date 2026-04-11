import subprocess
import sys
import io
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


def run_cli_with_closed_pipe(args, pipe_name):
    popen_kwargs = {
        "cwd": REPO_ROOT,
        "text": True,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
    }
    proc = subprocess.Popen([sys.executable, str(SCRIPT)] + args, **popen_kwargs)
    closed_stream = getattr(proc, pipe_name)
    open_stream = proc.stderr if pipe_name == "stdout" else proc.stdout
    closed_stream.close()
    remaining_output = open_stream.read()
    returncode = proc.wait()
    return returncode, remaining_output


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


def test_cli_word_joiner_is_reported(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("a\u2060b\n", encoding="utf-8")
    result = run_cli([str(sample)])
    assert result.returncode == 0
    output = result.stdout.strip().splitlines()
    assert output == [f"{sample}:1:a[U+2060 WORD JOINER]b"]


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


def test_highlight_color_only_substitutes_cf_chars(monkeypatch):
    import nospc

    monkeypatch.setattr(nospc, "colored", lambda text, *a, **k: f"<{text}>")
    out, found = nospc.highlight_non_standard_whitespace("a\u200bb", True, False)
    assert found
    assert out == "a<[U+200B ZERO WIDTH SPACE]>b"


def test_highlight_color_only_substitutes_line_and_paragraph_separator(monkeypatch):
    import nospc

    monkeypatch.setattr(nospc, "colored", lambda text, *a, **k: f"<{text}>")
    out, found = nospc.highlight_non_standard_whitespace("x\u2028y\u2029z", True, False)
    assert found
    assert out == "x<[U+2028 LINE SEPARATOR]>y<[U+2029 PARAGRAPH SEPARATOR]>z"


def test_highlight_color_only_keeps_nbsp_as_character(monkeypatch):
    import nospc

    monkeypatch.setattr(nospc, "colored", lambda text, *a, **k: f"<{text}>")
    out, found = nospc.highlight_non_standard_whitespace("a\u00a0b", True, False)
    assert found
    assert out == "a<\xa0>b"


def test_highlight_color_and_bracket_no_double_label(monkeypatch):
    import nospc

    monkeypatch.setattr(nospc, "colored", lambda text, *a, **k: f"<{text}>")
    out, found = nospc.highlight_non_standard_whitespace("a\u200bb", True, True)
    assert found
    assert out == "a<[U+200B ZERO WIDTH SPACE]>b"


def test_main_color_falls_back_to_brackets_without_termcolor(monkeypatch, tmp_path, capsys):
    import nospc

    sample = tmp_path / "color.txt"
    sample.write_bytes(b"a\x1cb\n")
    monkeypatch.setattr(nospc, "HAS_TERMCOLOR", False)

    assert nospc.main([str(sample), "--color"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [f"{sample}:1:a[U+001C FILE SEPARATOR]b"]
    assert captured.err == ""


def test_cli_quiet_when_stdout_pipe_closes_early(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text(("a\u00A0b\n" * 5000), encoding="utf-8")

    returncode, stderr_output = run_cli_with_closed_pipe([str(sample)], "stdout")

    assert returncode == 1
    assert stderr_output == ""


def test_cli_quiet_when_stderr_pipe_closes_early(tmp_path):
    missing = tmp_path / "missing.txt"

    returncode, stdout_output = run_cli_with_closed_pipe([str(missing)], "stderr")

    assert returncode == 1
    assert stdout_output == ""


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


def test_process_stdin_broken_pipe_propagates(monkeypatch):
    import pytest

    fake_stdin = io.TextIOWrapper(io.BytesIO(b""), encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", fake_stdin)
    monkeypatch.setattr(
        "nospc.filter_non_standard_whitespace",
        lambda *args, **kwargs: (_ for _ in ()).throw(BrokenPipeError("broken pipe")),
    )
    with pytest.raises(BrokenPipeError, match="broken pipe"):
        __import__("nospc").process_stdin(False, True)


def test_process_stdin_accepts_text_only_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("x\u00A0y\n"))
    assert __import__("nospc").process_stdin(False, True) is True
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == ["-:1:x[U+00A0 NO-BREAK SPACE]y"]
    assert captured.err == ""



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
