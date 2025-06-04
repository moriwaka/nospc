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
