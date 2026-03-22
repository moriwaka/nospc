# nospc

nospc is a utility to detect and highlight whitespace characters other than the ASCII space and tab in text files. It reports carriage returns (`\r`) and other non-standard whitespace within each input line, while line feeds (`\n`) are treated as line separators.

## Features

- Detects whitespace characters other than ASCII space and tab within each input line
- Reports carriage return (`\r`) while treating line feed (`\n`) as the line separator
- Supports `--crlf` to ignore carriage return only when it is part of a `CRLF` line ending
- Supports multiple input files and directories
- Supports standard input
- Highlighting methods:
  - Colored text
  - Enclosing characters in brackets with Unicode information
- Recursive directory processing

## Target Characters

`nospc` reports this target set:

- Unicode whitespace matched by Python `str.isspace()`, except ASCII space (`U+0020`), tab (`U+0009`), and line feed (`U+000A`)
- Extra invisible format characters that are commonly problematic in text:
  - `U+200B` ZERO WIDTH SPACE
  - `U+2060` WORD JOINER
  - `U+FEFF` ZERO WIDTH NO-BREAK SPACE

In regex form, the current target set is:

```regex
[\u000B-\u000D\u001C-\u001F\u0085\u00A0\u1680\u2000-\u200B\u2028\u2029\u202F\u205F\u2060\u3000\uFEFF]
```

This covers:

- `U+000B` VERTICAL TAB
- `U+000C` FORM FEED
- `U+000D` CARRIAGE RETURN
- `U+001C` FILE SEPARATOR
- `U+001D` GROUP SEPARATOR
- `U+001E` RECORD SEPARATOR
- `U+001F` UNIT SEPARATOR
- `U+0085` NEXT LINE
- `U+00A0` NO-BREAK SPACE
- `U+1680` OGHAM SPACE MARK
- `U+2000` EN QUAD
- `U+2001` EM QUAD
- `U+2002` EN SPACE
- `U+2003` EM SPACE
- `U+2004` THREE-PER-EM SPACE
- `U+2005` FOUR-PER-EM SPACE
- `U+2006` SIX-PER-EM SPACE
- `U+2007` FIGURE SPACE
- `U+2008` PUNCTUATION SPACE
- `U+2009` THIN SPACE
- `U+200A` HAIR SPACE
- `U+200B` ZERO WIDTH SPACE
- `U+2028` LINE SEPARATOR
- `U+2029` PARAGRAPH SEPARATOR
- `U+202F` NARROW NO-BREAK SPACE
- `U+205F` MEDIUM MATHEMATICAL SPACE
- `U+2060` WORD JOINER
- `U+3000` IDEOGRAPHIC SPACE
- `U+FEFF` ZERO WIDTH NO-BREAK SPACE

## Requirements

- Python 3.x
- UTF-8 encoded input files
- `termcolor` for colorized output only

## Installation

Install from the repository root:

```sh
pip install .
```

If you want ANSI color output, install the optional color extra:

```sh
pip install '.[color]'
```

For local script usage without installation, you can still run `python nospc.py ...`.

## Usage

### Basic Usage

To run nospc with a single file:

```sh
nospc <filename>
```

`nospc` reads files as UTF-8. Files that cannot be decoded as UTF-8 are reported as `is not valid UTF-8 text.` Line feeds (`\n`) delimit lines and are not reported; carriage returns (`\r`) inside those lines are reported. With `--crlf`, a carriage return is ignored only when it appears immediately before the line feed in a `CRLF` ending.

### Multiple Files

To run nospc with multiple files:

```sh
nospc <filename1> <filename2> ...
```

### Standard Input

To run nospc with standard input:

```sh
cat somefile.txt | nospc -
```

### Recursive Directory Processing

To run nospc and process directories recursively:

```sh
nospc -r <directory>
```

### CRLF Handling

To ignore carriage return only when it is part of a `CRLF` line ending:

```sh
nospc --crlf <filename>
```

### Highlighting Options

You can choose between two highlighting methods: color and brackets. By default, if the output is a TTY, color highlighting is enabled. If the output is not a TTY, bracket highlighting is enabled. If `termcolor` is not installed, `--color` falls back to bracket highlighting instead of failing or emitting raw control characters.

#### Using Colored Text

To enable color highlighting:

```sh
nospc -c <filename>
```

#### Using Brackets with Unicode Information

To enable bracket highlighting:

```sh
nospc -b <filename>
```

#### Using Both Highlighting Methods

To enable both color and bracket highlighting:

```sh
nospc -c -b <filename>
```

## Examples

### Detect and highlight whitespace characters other than the ASCII space and tab in a file using colored text:

```sh
nospc -c file.txt
```

### Detect and highlight whitespace characters other than the ASCII space and tab in a file using brackets:

```sh
nospc -b file.txt
```

### Process a directory recursively and highlight using both methods:

```sh
nospc -r -c -b directory_name
```

### Ignore carriage return only in CRLF line endings:

```sh
nospc --crlf file.txt
```
