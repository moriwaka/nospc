# nospc AI Agent Guidelines

This document provides context and guidelines for AI agents working with the `nospc` repository.

## Project Overview

`nospc` is a Python-based utility script designed to detect and highlight whitespace characters other than the standard ASCII space and tab (e.g., zero-width spaces, non-breaking spaces). 

## Technology Stack

*   **Language:** Python 3.x
*   **External Dependencies:** `termcolor` (used for terminal color output). There is a fallback mechanism to ignore colors if the module is missing or the output is not a TTY.
*   **Testing Framework:** `pytest`
*   **Documentation:** Man pages (`nospc.1`) and `README.md`

## Architecture and File Structure

*   **`nospc.py`**: The primary executable script. It parses arguments (recursively handling directories or reading from `stdin`) and uses regular expressions (`re`) to locate non-standard whitespaces.
*   **`tests/`**: Contains the testing suite. The tests verify both the CLI parsing (`test_cli.py`) and the logic for highlighting strings and handling files (`test_highlight.py`).
*   **`nospc.1`**: Troff-formatted man page for the `nospc` command.
*   **`pyproject.toml`**: Includes minimal configuration for `pytest` (e.g., setting `-vv`).

## Development & Testing Workflow

### Setup
```bash
# Install required dependencies
pip install termcolor pytest
```

### Running Tests
To ensure you do not break existing functionality, run all tests before marking a task as complete:
```bash
pytest
```

## Implementation Details & Constraints

1.  **Regex Matching:** Non-standard whitespace is matched by taking the `\s` regex pattern outcome and explicitly filtering out `[' ', '\t']`.
2.  **Display Modes:**
    *   **Color Mode (`-c`):** Highlights invalid characters in reversed blinking red text using `termcolor`. Active by default if writing directly to a TTY.
    *   **Bracket Mode (`-b`):** Replaces invalid characters with their Unicode name formatted in brackets like `[U+XXXX CHARACTER NAME]`. Active by default if the output is redirected away from a TTY.
3.  **Cross-Platform Gracefulness:** 
    *   If `termcolor` is unavailable, it imports a dummy function to allow execution to proceed.
    *   `nospc.py` catches `UnicodeDecodeError`, `IsADirectoryError`, and generic `Exception`s gracefully while processing multiple files, rather than halting execution.

When making modifications or adding new features, maintain compatibility with these core behaviors and ensure all exceptions are handled gracefully.
