#!/bin/env python3

import os
import re
import sys
import argparse
from termcolor import colored
import unicodedata

all_whitespace_pattern = re.compile(r'\s')

exclude_chars = [' ', '\t']

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
                unicode_info = f"U+{ord(char):04X} {unicodedata.name(char)}"
                highlighted_space = f"[{unicode_info}]"
            if use_color:
                highlighted_space = colored(highlighted_space, 'red', attrs=['reverse', 'blink'])
            highlighted_line += line[offset:start] + highlighted_space
            offset = end
    highlighted_line += line[offset:]
    return highlighted_line, found_non_standard

def filter_non_standard_whitespace(file, filename, use_color, use_bracket):
    for line_number, line in enumerate(file, 1):
        # Keep leading and trailing whitespace when analyzing the line
        highlighted_line, line_found_non_standard = highlight_non_standard_whitespace(line.rstrip('\n'), use_color, use_bracket)
        if line_found_non_standard:
            print(f"{filename}:{line_number}:{highlighted_line}")

def process_file(filename, use_color, use_bracket):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            filter_non_standard_whitespace(file, filename, use_color, use_bracket)
    except UnicodeDecodeError:
        print(f"{filename}: is binary file.")
    except IsADirectoryError:
        print(f"{filename}: is not a regular file.")
    except Exception as e:
        print(f"{filename}: could not be processed. ({str(e)})")

def process_directory(directory, use_color, use_bracket):
    for root, _, files in os.walk(directory):
        for name in files:
            filepath = os.path.join(root, name)
            process_file(filepath, use_color, use_bracket)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect and highlight non-ASCII whitespace characters.")
    parser.add_argument('filenames', metavar='N', type=str, nargs='+', help='Input file names or directories')
    parser.add_argument('-c', '--color', action='store_true', help='Enable color highlighting')
    parser.add_argument('-b', '--bracket', action='store_true', help='Enable bracket highlighting with Unicode information')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursively process directories')

    args = parser.parse_args()
    filenames = args.filenames
    use_color = args.color or (sys.stdout.isatty() and not args.bracket)
    use_bracket = args.bracket or (not sys.stdout.isatty() and not args.color)
    recursive = args.recursive

    for filename in filenames:
        if filename == "-":
            filter_non_standard_whitespace(sys.stdin, "-", use_color, use_bracket)
        else:
            if os.path.isdir(filename):
                if recursive:
                    process_directory(filename, use_color, use_bracket)
                else:
                    print(f"{filename}: is not a regular file.")
            else:
                process_file(filename, use_color, use_bracket)

