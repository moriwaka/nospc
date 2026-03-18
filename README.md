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

You can choose between two highlighting methods: color and brackets. By default, if the output is a TTY, color highlighting is enabled. If the output is not a TTY, bracket highlighting is enabled. If `termcolor` is not installed, `--color` falls back to plain text output instead of failing.

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
