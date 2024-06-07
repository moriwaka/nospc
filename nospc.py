#!/bin/env python3

import re
import sys
import argparse
from termcolor import colored
import unicodedata

# 正規表現で\sにマッチする空白文字を定義
all_whitespace_pattern = re.compile(r'\s')

# スペースとタブを除外するためのリスト
exclude_chars = [' ', '\t']

def highlight_non_standard_whitespace(line, highlight_type):
    highlighted_line = ''
    offset = 0
    found_non_standard = False
    
    for match in all_whitespace_pattern.finditer(line):
        char = match.group()
        if char not in exclude_chars:
            found_non_standard = True
            start, end = match.span()
            if highlight_type == "color":
                highlighted_space = colored(line[start:end], 'red', attrs=['reverse', 'blink'])
            elif highlight_type == "brackets":
                unicode_info = f"U+{ord(char):04X} {unicodedata.name(char)}"
                highlighted_space = f">>>[{unicode_info}]<<<"
            highlighted_line += line[offset:start] + highlighted_space
            offset = end
    highlighted_line += line[offset:]
    return highlighted_line, found_non_standard

def filter_non_standard_whitespace(file, filename, highlight_type):
    for line_number, line in enumerate(file, 1):
        highlighted_line, line_found_non_standard = highlight_non_standard_whitespace(line.strip(), highlight_type)
        if line_found_non_standard:
            print(f"{filename}:{line_number}:{highlighted_line}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect and highlight non-ASCII whitespace characters.")
    parser.add_argument('filenames', metavar='N', type=str, nargs='+', help='Input file names')
    parser.add_argument('--highlight', choices=['color', 'brackets'], default='color', help='Highlighting method')

    args = parser.parse_args()
    filenames = args.filenames
    highlight_type = args.highlight

    for filename in filenames:
        if filename == "-":
            filter_non_standard_whitespace(sys.stdin, "-", highlight_type)
        else:
            with open(filename, 'r', encoding='utf-8') as file:
                filter_non_standard_whitespace(file, filename, highlight_type)

