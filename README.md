# nospc

nospc is a utility to detect and highlight non-ASCII whitespace characters in text files. It supports highlighting using either colored text or enclosing characters in brackets with Unicode character information.

## Features

- Detects non-ASCII whitespace characters
- Supports multiple input files and directories
- Supports standard input
- Highlighting methods:
  - Colored text
  - Enclosing characters in brackets with Unicode information
- Recursive directory processing

## Requirements

- Python 3.x
- `termcolor` library

## Installation

1. Clone the repository or download the script.
2. Install the required library:
   ```sh
   pip install termcolor
   ```

## Usage

### Basic Usage

To run nospc with a single file:

```sh
python nospc.py <filename>
```

### Multiple Files

To run nospc with multiple files:

```sh
python nospc.py <filename1> <filename2> ...
```

### Standard Input

To run nospc with standard input:

```sh
cat somefile.txt | python nospc.py -
```

### Recursive Directory Processing

To run nospc and process directories recursively:

```sh
python nospc.py -r <directory>
```

### Highlighting Options

You can choose between two highlighting methods: color and brackets. By default, if the output is a TTY, color highlighting is enabled. If the output is not a TTY, bracket highlighting is enabled.

#### Using Colored Text

To enable color highlighting:

```sh
python nospc.py -c <filename>
```

#### Using Brackets with Unicode Information

To enable bracket highlighting:

```sh
python nospc.py -b <filename>
```

#### Using Both Highlighting Methods

To enable both color and bracket highlighting:

```sh
python nospc.py -c -b <filename>
```

## Examples

### Detect and highlight non-ASCII whitespace characters in a file using colored text:

```sh
python nospc.py -c file.txt
```

### Detect and highlight non-ASCII whitespace characters in a file using brackets:

```sh
python nospc.py -b file.txt
```

### Process a directory recursively and highlight using both methods:

```sh
python nospc.py -r -c -b directory_name
```


