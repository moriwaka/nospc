# nospc

nospc is a utility to detect and highlight non-ASCII whitespace characters in text files. It supports highlighting using either colored text or enclosing characters in brackets with Unicode character information.

## Features

- Detects non-ASCII whitespace characters
- Supports multiple input files
- Supports standard input
- Highlighting methods:
  - Colored text
  - Enclosing characters in brackets with Unicode character information

## Requirements

- Python 3.x
- termcolor library

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
nospc.py <filename>
```

### Multiple Files

To run nospc with multiple files:

```sh
nospc.py <filename1> <filename2> ...
```

### Standard Input

To run nospc with standard input:

```sh
cat somefile.txt | nospc.py -
```

### Highlighting Options

You can choose between two highlighting methods: `color` (default) and `brackets`.

#### Using Colored Text

```sh
nospc.py <filename>
```

#### Using Brackets 

```sh
nospc.py --highlight brackets <filename>
```

### Unicode Information

You can show unicode information like: U+xxxx CHAR NAME

```sh
nospc.py -v <filename>
nospc.py -v --highlight brackets <filename>
```


