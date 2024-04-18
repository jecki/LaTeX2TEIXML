#!/usr/bin/env python3

"""joinLaTeX.py -- joins a LaTeX file linked by include or input-statements
                   into a single file and (optionally) merges paragraphs to
                   single lines.
"""

from argparse import ArgumentParser
import re
import sys
from LaTeXParser import preprocessing

if __name__ == "__main__":
    parser = ArgumentParser(description="Joins LaTeX-files that include other files into a single LaTeX file.")
    parser.add_argument('filename', nargs=1)
    parser.add_argument('-n', '--normalize', action='store_const', const='normalize',
                        help='merge paragraphs in single lines')
    args = parser.parse_args()
    with open(args.filename[0], 'r', encoding='utf8') as f:
        master = f.read()

    # integrate included files
    result = preprocessing.factory()(master, args.filename[0])
    if result.errors:
        for e in result.errors: print(e)
        sys.exit(1)
    text = result.preprocessed_text

    if args.normalize is not None:
        # replace linefeeds within parahraphs with blanks
        normalized = re.sub(r'(?<!\n)[ \t]*\n(?![ \t]*\n)[ \t]*', ' ', text)
        out_text = normalized
    else:
        out_text = text





