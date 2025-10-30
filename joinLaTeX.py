#!/usr/bin/env python3

"""joinLaTeX.py -- joins a LaTeX file linked by include or input-statements
                   into a single file and (optionally) merges paragraphs to
                   single lines.
"""

from argparse import ArgumentParser
from functools import partial
import os
import re
import sys

from DHParser.preprocess import gen_find_include_func, preprocess_includes


RE_INCLUDE = r'\\(?:input|include)\{(?P<name>.*)\}'
RE_COMMENT = r'%.*'  # must always be the same as Grammar.COMMENT__!z

find_next_include = gen_find_include_func(
    RE_INCLUDE, RE_COMMENT,
    lambda s: s if s[-4:] == '.tex' else s + '.tex')
integrate_includes = partial(preprocess_includes, find_next_include=find_next_include)


if __name__ == "__main__":
    parser = ArgumentParser(description="Joins LaTeX-files that include other files into a single LaTeX file.")
    parser.add_argument('filename', nargs=1)
    parser.add_argument('-n', '--normalize', action='store_const', const='normalize',
                        help='merge paragraphs in single lines')
    args = parser.parse_args()

    src_name = args.filename[0]
    dst_name = os.path.splitext(src_name)[0] + '.singlefile.tex'
    if os.path.exists(dst_name):
        print(f'file "{dst_name}" already exists. Please delete the existing file first.')
        sys.exit(1)

    with open(src_name, 'r', encoding='utf8') as f:
        master = f.read()

    # integrate included files
    result = integrate_includes(master, src_name)
    if result.errors:
        for e in result.errors: print(e)
        sys.exit(1)
    text = result.preprocessed_text

    if args.normalize is not None:
        # replace linefeeds within parahraphs with blanks
        step1 = re.sub(r'%[^\n]*', '', text)
        step2 = re.sub(r'[ \t]+(?=\n)', '', step1)
        step3 = re.sub(r'(?<!\n)[ \t]*\n(?![ \t]*\n)[ \t]*', ' ', step2)
        normalized = re.sub(r'[ \t]*\n[ \t]*(?:\n[ \t]*)+', '\n\n', step3)
        out_text = normalized
    else:
        out_text = text

    with open(dst_name, 'w', encoding='utf-8') as f:
        f.write(out_text)

    print(f'"{dst_name}" written to disk.')
