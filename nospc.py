#!/usr/bin/env python3

import os
import re
import sys
import argparse
try:
    from termcolor import colored
except ImportError:  # pragma: no cover - fallback if termcolor is missing
    def colored(text, *_, **__):
        return text
import unicodedata

all_whitespace_pattern = re.compile(r'\s')

exclude_chars = [' ', '\t']
ascii_whitespace_names = {
    '\r': "CARRIAGE RETURN",
    '\v': "VERTICAL TAB",
    '\f': "FORM FEED",
    '\x1c': "FILE SEPARATOR",
    '\x1d': "GROUP SEPARATOR",
    '\x1e': "RECORD SEPARATOR",
    '\x1f': "UNIT SEPARATOR",
}

def describe_whitespace(char):
    try:
        name = unicodedata.name(char)
    except ValueError:
        name = ascii_whitespace_names.get(char, "UNNAMED")
    return f"U+{ord(char):04X} {name}"

def highlight_non_standard_whitespace(line, use_color, use_bracket):
    highlighted_line = ''
    offset = 0
    found_non_standard = False
    
    for match in all_whitespace_pattern.finditer(line):
        char = match.group()
        if char not in exclude_chars:
            found_non_standard = True
            start, end = match.span()
            highlighted_space = line[start:end]
            if use_bracket:
                unicode_info = describe_whitespace(char)
                highlighted_space = f"[{unicode_info}]"
            if use_color:
                highlighted_space = colored(highlighted_space, 'red', attrs=['reverse', 'blink'])
            highlighted_line += line[offset:start] + highlighted_space
            offset = end
    highlighted_line += line[offset:]
    return highlighted_line, found_non_standard

def filter_non_standard_whitespace(file, filename, use_color, use_bracket, ignore_crlf=False):
    for line_number, line in enumerate(file, 1):
        # Strip the logical line-feed separator but preserve other whitespace such as carriage return.
        if line.endswith('\n'):
            if ignore_crlf and line.endswith('\r\n'):
                line = line[:-2]
            else:
                line = line[:-1]
        highlighted_line, line_found_non_standard = highlight_non_standard_whitespace(line, use_color, use_bracket)
        if line_found_non_standard:
            print(f"{filename}:{line_number}:{highlighted_line}")

def process_file(filename, use_color, use_bracket, ignore_crlf=False):
    try:
        with open(filename, 'r', encoding='utf-8', newline='') as file:
            filter_non_standard_whitespace(file, filename, use_color, use_bracket, ignore_crlf)
    except UnicodeDecodeError:
        print(f"{filename}: is binary file.")
    except IsADirectoryError:
        print(f"{filename}: is not a regular file.")
    except Exception as e:
        print(f"{filename}: could not be processed. ({str(e)})")

def process_directory(directory, use_color, use_bracket, ignore_crlf=False):
    for root, _, files in os.walk(directory):
        for name in files:
            filepath = os.path.join(root, name)
            process_file(filepath, use_color, use_bracket, ignore_crlf)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Detect and highlight whitespace characters other than the ASCII space and tab.")
    parser.add_argument('filenames', metavar='N', type=str, nargs='+', help='Input file names or directories')
    parser.add_argument('-c', '--color', action='store_true', help='Enable color highlighting')
    parser.add_argument('-b', '--bracket', action='store_true', help='Enable bracket highlighting with Unicode information')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursively process directories')
    parser.add_argument('--crlf', action='store_true', help='Ignore carriage returns that are part of CRLF line endings')

    args = parser.parse_args(argv)
    filenames = args.filenames
    use_color = args.color or (sys.stdout.isatty() and not args.bracket)
    use_bracket = args.bracket or (not sys.stdout.isatty() and not args.color)
    recursive = args.recursive
    ignore_crlf = args.crlf

    for filename in filenames:
        if filename == "-":
            if hasattr(sys.stdin, 'reconfigure'):
                sys.stdin.reconfigure(newline='')
            filter_non_standard_whitespace(sys.stdin, "-", use_color, use_bracket, ignore_crlf)
        else:
            if os.path.isdir(filename):
                if recursive:
                    process_directory(filename, use_color, use_bracket, ignore_crlf)
                else:
                    print(f"{filename}: is not a regular file.")
            else:
                process_file(filename, use_color, use_bracket, ignore_crlf)

if __name__ == "__main__":
    main()
