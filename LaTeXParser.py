#!/usr/bin/env python3

#######################################################################
#
# SYMBOLS SECTION - Can be edited. Changes will be preserved.
#
#######################################################################


import collections
from functools import partial
import os
import sys
from typing import Tuple, List, Union, Any, Optional, Callable, cast

try:
    import regex as re
except ImportError:
    import re

try:
    scriptdir = os.path.dirname(os.path.realpath(__file__))
except NameError:
    scriptdir = ''
if scriptdir and scriptdir not in sys.path: sys.path.append(scriptdir)

try:
    from DHParser import versionnumber
except (ImportError, ModuleNotFoundError):
    i = scriptdir.rfind("/DHParser/")
    if i >= 0:
        dhparserdir = scriptdir[:i + 10]  # 10 = len("/DHParser/")
        if dhparserdir not in sys.path:  sys.path.insert(0, dhparserdir)

import DHParser

from DHParser.compile import Compiler, compile_source, Junction, full_compile
from DHParser.configuration import set_config_value, get_config_value, access_thread_locals, \
    access_presets, finalize_presets, set_preset_value, get_preset_value, NEVER_MATCH_PATTERN
from DHParser import dsl
from DHParser.dsl import recompile_grammar, never_cancel
from DHParser.ebnf import grammar_changed
from DHParser.error import ErrorCode, Error, canonical_error_strings, has_errors, NOTICE, \
    WARNING, ERROR, FATAL
from DHParser.log import start_logging, suspend_logging, resume_logging
from DHParser.nodetree import Node, WHITESPACE_PTYPE, TOKEN_PTYPE, RootNode, Path, flatten_sxpr, \
    add_class
from DHParser.parse import Grammar, PreprocessorToken, Whitespace, Drop, AnyChar, Parser, \
    Lookbehind, Lookahead, Alternative, Pop, Text, Synonym, Counted, Interleave, INFINITE, ERR, \
    Option, NegativeLookbehind, OneOrMore, RegExp, Retrieve, Series, Capture, TreeReduction, \
    ZeroOrMore, Forward, NegativeLookahead, Required, CombinedParser, Custom, mixin_comment, \
    last_value, matching_bracket, optional_last_value
from DHParser.pipeline import PseudoJunction, create_parser_junction, create_junction
from DHParser.preprocess import nil_preprocessor, PreprocessorFunc, PreprocessorResult, \
    gen_find_include_func, preprocess_includes, make_preprocessor, chain_preprocessors, \
    Tokenizer
from DHParser.toolkit import is_filename, load_if_file, cpu_count, RX_NEVER_MATCH, \
    ThreadLocalSingletonFactory, expand_table, abbreviate_middle
from DHParser.trace import set_tracer, resume_notices_on, trace_history
from DHParser.transform import is_empty, remove_if, TransformationDict, TransformerFunc, \
    transformation_factory, remove_children_if, move_fringes, normalize_whitespace, \
    is_anonymous, name_matches, reduce_single_child, replace_by_single_child, replace_or_reduce, \
    remove_whitespace, replace_by_children, remove_empty, remove_tokens, flatten, all_of, \
    any_of, transformer, merge_adjacent, collapse, collapse_children_if, transform_result, \
    remove_children, remove_content, remove_brackets, change_name, remove_anonymous_tokens, \
    keep_children, is_one_of, not_one_of, content_matches, apply_if, peek, \
    remove_anonymous_empty, keep_nodes, traverse_locally, strip, lstrip, rstrip, \
    replace_content_with, forbid, assert_content, remove_infix_operator, add_error, error_on, \
    left_associative, lean_left, node_maker, has_descendant, neg, has_ancestor, insert, \
    positions_of, replace_child_names, add_attributes, delimit_children, merge_connected, \
    has_attr, has_parent, has_children, has_child, apply_unless, apply_ifelse, traverse
from DHParser import parse as parse_namespace__

import DHParser.versionnumber
if DHParser.versionnumber.__version_info__ < (1, 7, 0):
    print(f'DHParser version {DHParser.versionnumber.__version__} is lower than the DHParser '
          f'version 1.5.0, {os.path.basename(__file__)} has first been generated with. '
          f'Please install a more recent version of DHParser to avoid unexpected errors!')



#######################################################################
#
# PREPROCESSOR SECTION - Can be edited. Changes will be preserved.
#
#######################################################################




RE_INCLUDE = r'\\(?:input|include)\{(?P<name>.*)\}'
RE_COMMENT = r'%.*'  # must always be the same as Grammar.COMMENT__!z


def LaTeXTokenizer(original_text) -> Tuple[str, List[Error]]:
    return original_text, []


def preprocessor_factory() -> PreprocessorFunc:
    # below, the second parameter
    find_next_include = gen_find_include_func(RE_INCLUDE, RE_COMMENT, lambda s: s + '.tex')
    include_prep = partial(preprocess_includes, find_next_include=find_next_include)
    tokenizing_prep = make_preprocessor(LaTeXTokenizer)
    return chain_preprocessors(include_prep, tokenizing_prep)


preprocessing = PseudoJunction(ThreadLocalSingletonFactory(preprocessor_factory))


#######################################################################
#
# PARSER SECTION - Don't edit! CHANGES WILL BE OVERWRITTEN!
#
#######################################################################

class LaTeXGrammar(Grammar):
    r"""Parser for a LaTeX source file.
    """
    _block_environment = Forward()
    _inline_math_text = Forward()
    _text_element = Forward()
    block = Forward()
    block_of_paragraphs = Forward()
    item = Forward()
    paragraph = Forward()
    param_block = Forward()
    tabular_config = Forward()
    source_hash__ = "39b6f88ab34ec7687d1fa38d3a2b5d4c"
    early_tree_reduction__ = CombinedParser.MERGE_TREETOPS
    disposable__ = re.compile('_\\w+')
    static_analysis_pending__ = []  # type: List[bool]
    parser_initialization__ = ["upon instantiation"]
    error_messages__ = {'end_generic_block': [(re.compile(r'(?=)'), "A block environment must be followed by a linefeed, not by: {1}")],
                        'item': [(re.compile(r'(?=)'), '\\item without proper content, found: {1}')]}
    COMMENT__ = r'%.*'
    comment_rx__ = re.compile(COMMENT__)
    comment__ = RegExp(comment_rx__)
    WHITESPACE__ = r'[ \t]*(?:\n(?![ \t]*\n)[ \t]*)?'
    whitespace__ = Whitespace(WHITESPACE__)
    WSP_RE__ = mixin_comment(whitespace=WHITESPACE__, comment=COMMENT__)
    wsp__ = Whitespace(WSP_RE__)
    dwsp__ = Drop(Whitespace(WSP_RE__))
    EOF = RegExp('(?!.)')
    _BACKSLASH = RegExp('[\\\\]')
    _DROP_BACKSLASH = Drop(Synonym(_BACKSLASH))
    _LB = Drop(RegExp('\\s*?\\n|$'))
    NEW_LINE = Series(Drop(RegExp('[ \\t]*')), Option(comment__), Drop(RegExp('\\n')))
    _GAP = Drop(Series(RegExp('[ \\t]*(?:\\n[ \\t]*)+\\n'), dwsp__))
    _WSPC = Drop(OneOrMore(Alternative(comment__, Drop(RegExp('\\s+')))))
    _PARSEP = Drop(Series(ZeroOrMore(Series(whitespace__, comment__)), _GAP, Option(_WSPC)))
    S = Series(Lookahead(Drop(RegExp('[% \\t\\n]'))), NegativeLookahead(_GAP), wsp__)
    LFF = Alternative(Series(NEW_LINE, Option(_WSPC)), EOF)
    _LETTERS = RegExp('\\w+')
    CHARS = RegExp('[^\\\\%$&\\{\\}\\[\\]\\s\\n\'`"]+')
    LINE = RegExp('[^\\\\%$&\\{\\}\\[\\]\\n\'`"]+')
    _TEXT_NOPAR = RegExp('(?:[^\\\\%$&\\{\\}\\[\\]\\(\\)\\n]+(?:\\n(?![ \\t]*\\n))?)+')
    _TEXT = RegExp('(?:[^\\\\%$&\\{\\}\\[\\]\\n\'`"]+(?:\\n(?![ \\t]*\\n))?)+')
    _TAG = RegExp('[\\w=?.:\\-%&\\[\\] /]+')
    _RBRACE = Text("}")
    _LBRACE = Text("{")
    _DOLLAR = Text("$")
    _COLON = Text(":")
    _HASH = Text("#")
    _PATHSEP = RegExp('/(?!\\*)')
    _PATH = RegExp('[\\w=~?.,%&\\[\\]-]+')
    UNIT = RegExp('(?!\\d)\\w+')
    _FRAC = RegExp('\\.[0-9]+')
    _INTEGER = RegExp('-?(?:(?:[1-9][0-9]+)|[0-9])')
    _NAME = RegExp('(?!\\d)\\w+\\*?')
    NAME = Capture(Synonym(_NAME), zero_length_warning=True)
    IDENTIFIER = Synonym(_NAME)
    _QUALIFIED = Series(IDENTIFIER, ZeroOrMore(Series(NegativeLookbehind(_BACKSLASH), Drop(RegExp('[:.-]')), IDENTIFIER)))
    LINEFEED = RegExp('[\\\\][\\\\]')
    BRACKETS = RegExp('[\\[\\]]')
    SPECIAL = RegExp('[$&_/\\\\\\\\]')
    QUOTEMARK = RegExp('"[`\']?|``?|\'\'?')
    LEERZEICHEN = RegExp('\\\\\\s+')
    UMLAUT = RegExp('(?x)\\\\(?:(?:"[AEIOUaeiou])|(?:"\\{[AEIOUaeiou]\\})\n                  |(?:\'[AEIOUaeioun])|(?:\'\\{\\\\?[AEIOUaeioun]\\})\n                  |(?:\'\'[AEIOUaeioun])|(?:\'\'\\{\\\\?[AEIOUaeioun]\\})\n                  |(?:`[AEIOUaeiou])|(?:`\\{[AEIOUaeiou]\\})\n                  |(?:[\\^][AEIOUCaeioucg])|(?:[\\^]\\{\\\\?[AEIOUCaeioucgj]\\})\n                  |(?:~[n])|(?:~\\{[n]\\}))')
    ESCAPED = RegExp('\\\\(?:(?:[#%$&_/{} \\n])|(?:~\\{\\s*\\}))')
    TXTCOMMAND = RegExp('\\\\text\\w+')
    CMDNAME = Series(RegExp('\\\\@?(?:(?![\\d_])\\w)+'), dwsp__)
    WARN_Komma = Series(Text(","), dwsp__)
    esc_char = RegExp('[,~$_^{}]')
    number = Series(_INTEGER, Option(_FRAC))
    magnitude = Series(number, Option(UNIT))
    info_value = Series(_TEXT_NOPAR, ZeroOrMore(Series(S, _TEXT_NOPAR)))
    info_key = Series(Drop(Text("/")), _NAME)
    info_assoc = Series(info_key, dwsp__, Option(Series(Series(Drop(Text("(")), dwsp__), info_value, Series(Drop(Text(")")), dwsp__), mandatory=1)))
    _info_block = Series(Series(Drop(Text("{")), dwsp__), ZeroOrMore(info_assoc), Series(Drop(Text("}")), dwsp__), mandatory=1)
    value = Alternative(magnitude, _LETTERS, CMDNAME, param_block, block)
    key = Synonym(_QUALIFIED)
    flag = Alternative(_QUALIFIED, magnitude)
    association = Series(key, dwsp__, Series(Drop(Text("=")), dwsp__), value, dwsp__)
    parameters = Series(Alternative(association, flag), ZeroOrMore(Series(NegativeLookbehind(_BACKSLASH), Series(Drop(Text(",")), dwsp__), Alternative(association, flag))), Option(WARN_Komma))
    heading = Synonym(block)
    special = Alternative(Drop(Text("\\-")), LEERZEICHEN, UMLAUT, QUOTEMARK, Series(Drop(RegExp('\\\\')), esc_char))
    _item_name = Text("item")
    _structure_name = Drop(Alternative(Drop(Text("subsection")), Drop(Text("section")), Drop(Text("chapter")), Drop(Text("subsubsection")), Drop(Text("paragraph")), Drop(Text("subparagraph"))))
    _env_name = Drop(Alternative(Drop(Text("enumerate")), Drop(Text("itemize")), Drop(Text("description")), Drop(Text("figure")), Drop(Text("quote")), Drop(Text("quotation")), Series(Drop(Text("tabular")), Option(Drop(Text("*")))), Series(Drop(Text("tabbing")), Option(Drop(Text("*")))), Series(Drop(Text("displaymath")), Option(Drop(Text("*")))), Series(Drop(Text("equation")), Option(Drop(Text("*")))), Series(Drop(Text("eqnarray")), Option(Drop(Text("*")))), Series(Drop(Text("align")), Option(Drop(Text("ed"))), Option(Drop(Text("*"))))))
    blockcmd = Series(_DROP_BACKSLASH, Alternative(Series(Alternative(Series(Drop(Text("begin{")), dwsp__), Series(Drop(Text("end{")), dwsp__)), _env_name, Series(Drop(Text("}")), dwsp__)), Series(_structure_name, Lookahead(Drop(Text("{")))), Drop(Text("[")), Drop(Text("]")), _item_name))
    no_command = Alternative(Series(Drop(Text("\\begin{")), dwsp__), Series(Drop(Text("\\end{")), dwsp__), Series(_DROP_BACKSLASH, _structure_name, Lookahead(Drop(Text("{")))))
    text = Series(OneOrMore(Alternative(_TEXT, special)), ZeroOrMore(Series(S, OneOrMore(Alternative(_TEXT, special)))))
    cfg_text = Series(ZeroOrMore(Alternative(text, CMDNAME, SPECIAL, block)), dwsp__)
    config = Series(Series(Drop(Text("[")), dwsp__), Alternative(Series(parameters, Lookahead(Series(Drop(Text("]")), dwsp__))), cfg_text), Series(Drop(Text("]")), dwsp__), mandatory=1)
    _block_content = Series(Option(Alternative(_PARSEP, S)), ZeroOrMore(Series(Alternative(_block_environment, _text_element, paragraph), Option(Alternative(_PARSEP, S)))))
    hide_from_toc = Series(Text("*"), dwsp__)
    _pth = OneOrMore(Alternative(_PATH, ESCAPED))
    target = Series(_pth, ZeroOrMore(Series(NegativeLookbehind(Drop(RegExp('s?ptth'))), _COLON, _pth)), Option(Series(Alternative(Series(Option(_DROP_BACKSLASH), _HASH), Series(NegativeLookbehind(Drop(RegExp('s?ptth'))), _COLON)), _TAG)))
    path = Series(_pth, _PATHSEP)
    protocol = RegExp('\\w+://(?!\\*)')
    urlstring = Series(Option(protocol), ZeroOrMore(path), Option(target))
    href = Series(Series(Drop(Text("\\href{")), dwsp__), urlstring, Series(Drop(Text("}")), dwsp__), block)
    url = Series(Series(Drop(Text("\\url{")), dwsp__), urlstring, Series(Drop(Text("}")), dwsp__))
    ref = Series(Alternative(Series(Drop(Text("\\ref{")), dwsp__), Series(Drop(Text("\\pageref{")), dwsp__)), CHARS, Series(Drop(Text("}")), dwsp__))
    label = Series(Series(Drop(Text("\\label{")), dwsp__), CHARS, Series(Drop(Text("}")), dwsp__))
    hypersetup = Series(Series(Drop(Text("\\hypersetup")), dwsp__), param_block)
    pdfinfo = Series(Series(Drop(Text("\\pdfinfo")), dwsp__), _info_block)
    documentclass = Series(Series(Drop(Text("\\documentclass")), dwsp__), Option(config), block)
    column_nr = Synonym(_INTEGER)
    cline = Series(Series(Drop(Text("\\cline{")), dwsp__), column_nr, Series(Drop(Text("-")), dwsp__), column_nr, Series(Drop(Text("}")), dwsp__))
    hline = Series(Text("\\hline"), dwsp__)
    multicolumn = Series(Series(Drop(Text("\\multicolumn")), dwsp__), Series(Drop(Text("{")), dwsp__), column_nr, Series(Drop(Text("}")), dwsp__), tabular_config, block_of_paragraphs)
    caption = Series(Series(Drop(Text("\\caption")), dwsp__), block)
    includegraphics = Series(Series(Drop(Text("\\includegraphics")), dwsp__), Option(config), block)
    footnote = Series(Series(Drop(Text("\\footnote")), dwsp__), block_of_paragraphs)
    citep = Series(Alternative(Series(Drop(Text("\\citep")), dwsp__), Series(Drop(Text("\\cite")), dwsp__)), Option(config), block)
    citet = Series(Series(Drop(Text("\\citet")), dwsp__), Option(config), block)
    starred = Series(Text("*"), dwsp__)
    generic_command = Alternative(Series(NegativeLookahead(no_command), CMDNAME, Option(starred), ZeroOrMore(Series(dwsp__, Alternative(config, block)))), Series(Drop(Text("{")), CMDNAME, _block_content, Drop(Text("}")), mandatory=3))
    assignment = Series(NegativeLookahead(no_command), CMDNAME, Series(Drop(Text("=")), dwsp__), Alternative(Series(number, Option(UNIT)), block, CHARS))
    text_command = Alternative(Series(TXTCOMMAND, ZeroOrMore(block)), ESCAPED, BRACKETS)
    _known_command = Alternative(citet, citep, footnote, includegraphics, caption, multicolumn, hline, cline, documentclass, pdfinfo, hypersetup, label, ref, href, url, item)
    _command = Alternative(_known_command, text_command, assignment, generic_command)
    _inline_math_text_bracket = RegExp('(?:[^\\\\]*(?:(?![\\\\][)])[\\\\])?)*')
    _inline_math_core = RegExp('[^$\\\\{}]+')
    sequence = Series(Option(_WSPC), OneOrMore(Series(Alternative(paragraph, _block_environment), Option(Alternative(_PARSEP, S)))))
    _im_bracket = Series(Drop(Text("\\(")), _inline_math_text_bracket, Drop(Text("\\)")), mandatory=1)
    _im_dollar = Series(Drop(Text("$")), _inline_math_text, Alternative(Drop(Text("$")), Lookahead(Drop(Text("}")))), mandatory=1)
    inline_math = Alternative(_im_dollar, _im_bracket)
    end_environment = Series(Drop(RegExp('\\\\end{')), Pop(NAME), Drop(RegExp('}')), mandatory=1)
    begin_environment = Series(Drop(RegExp('\\\\begin{')), NegativeLookahead(_env_name), NAME, Drop(RegExp('}')), mandatory=2)
    _end_inline_env = Synonym(end_environment)
    _begin_inline_env = Alternative(Series(NegativeLookbehind(_LB), begin_environment), Series(begin_environment, NegativeLookahead(LFF)))
    generic_inline_env = Series(_begin_inline_env, dwsp__, paragraph, NegativeLookahead(_PARSEP), _end_inline_env, mandatory=4)
    _known_inline_env = Synonym(inline_math)
    _inline_environment = Alternative(_known_inline_env, generic_inline_env)
    _line_element = Alternative(text, _inline_environment, _command, block)
    SubParagraph = Series(Series(Drop(Text("\\subparagraph")), dwsp__), heading, Option(sequence))
    SubParagraphs = OneOrMore(Series(Option(_WSPC), SubParagraph))
    Paragraph = Series(Series(Drop(Text("\\paragraph")), dwsp__), heading, ZeroOrMore(Alternative(sequence, SubParagraphs)))
    Paragraphs = OneOrMore(Series(Option(_WSPC), Paragraph))
    tabcmd = Series(RegExp("\\\\[><'`'+-]"), dwsp__)
    tabrow = Series(Option(tabcmd), ZeroOrMore(Alternative(Series(_line_element, Option(Alternative(S, _PARSEP))), tabcmd)), Alternative(Series(Series(Drop(Text("\\\\")), dwsp__), Option(config), Option(_PARSEP)), Lookahead(Drop(Text("\\end{tabbing}")))))
    settab = Series(Series(Drop(Text("\\=")), dwsp__), Option(config))
    tabdefs = Series(Option(settab), ZeroOrMore(Alternative(Series(NegativeLookahead(Drop(Text("\\kill"))), _line_element, Option(Alternative(S, _PARSEP))), settab)), Alternative(Series(Drop(Text("\\\\")), dwsp__), Series(Drop(Text("\\kill")), dwsp__)), Option(config), Option(_PARSEP))
    tabbing = Series(Series(Drop(Text("\\begin{tabbing}")), dwsp__), tabdefs, ZeroOrMore(Alternative(tabrow, _WSPC)), Series(Drop(Text("\\end{tabbing}")), dwsp__), mandatory=3)
    cfg_right_seq = Series(Drop(Text("<")), block)
    cfg_left_seq = Series(Drop(Text(">")), block)
    cfg_separator = Alternative(Drop(Text("|")), Series(Drop(Text("!")), block))
    cfg_unit = Series(Drop(Text("{")), number, UNIT, Drop(Text("}")))
    cfg_celltype = RegExp('[lcrp]')
    cfg_colsep = Series(Drop(Text("@")), block)
    frontpages = Synonym(sequence)
    rb_down = Series(Series(Drop(Text("[")), dwsp__), number, UNIT, dwsp__, Series(Drop(Text("]")), dwsp__))
    rb_up = Series(Series(Drop(Text("[")), dwsp__), number, UNIT, dwsp__, Series(Drop(Text("]")), dwsp__))
    rb_offset = Series(Series(Drop(Text("{")), dwsp__), number, UNIT, dwsp__, Series(Drop(Text("}")), dwsp__))
    raisebox = Series(Series(Drop(Text("\\raisebox")), dwsp__), rb_offset, Option(rb_up), Option(rb_down), block)
    tabular_cell = Alternative(Series(raisebox, Option(Alternative(S, _PARSEP))), ZeroOrMore(Series(Alternative(_line_element, _block_environment), Option(Alternative(S, _PARSEP)))))
    tabular_row = Series(Alternative(multicolumn, tabular_cell), ZeroOrMore(Series(Series(Drop(Text("&")), dwsp__), Alternative(multicolumn, tabular_cell))), Alternative(Series(Series(Drop(Text("\\\\")), dwsp__), Alternative(hline, ZeroOrMore(cline)), Option(_PARSEP)), Lookahead(Drop(Text("\\end{tabular}")))))
    full_width = Text("*")
    tabular = Series(Drop(Text("\\begin{tabular")), Option(full_width), Series(Drop(Text("}")), dwsp__), Option(cfg_unit), tabular_config, ZeroOrMore(Alternative(tabular_row, _WSPC)), Drop(Text("\\end{tabular")), Option(Drop(Text("*"))), Series(Drop(Text("}")), dwsp__), mandatory=6)
    no_numbering = Text("*")
    _block_math = RegExp('(?:[^\\\\]*[\\\\]?(?!end\\{(?:eqnarray|equation|displaymath|aligned|align)\\*?\\}|\\])\\s*)*')
    align = Series(Drop(Text("\\begin{align")), Option(Drop(Text("ed"))), Option(no_numbering), Series(Drop(Text("}")), dwsp__), _block_math, Drop(Text("\\end{align")), Option(Drop(Text("ed"))), Option(Drop(Text("*"))), Series(Drop(Text("}")), dwsp__), mandatory=4)
    eqnarray = Series(Drop(Text("\\begin{eqnarray")), Option(no_numbering), Series(Drop(Text("}")), dwsp__), _block_math, Drop(Text("\\end{eqnarray")), Option(Drop(Text("*"))), Series(Drop(Text("}")), dwsp__), mandatory=3)
    equation = Series(Drop(Text("\\begin{equation")), Option(no_numbering), Series(Drop(Text("}")), dwsp__), _block_math, Drop(Text("\\end{equation")), Option(Drop(Text("*"))), Series(Drop(Text("}")), dwsp__), mandatory=3)
    _dmath_short_form = Series(Series(Drop(Text("\\[")), dwsp__), _block_math, Series(Drop(Text("\\]")), dwsp__), mandatory=1)
    _dmath_long_form = Series(Drop(Text("\\begin{displaymath")), Option(no_numbering), Series(Drop(Text("}")), dwsp__), _block_math, Drop(Text("\\end{displaymath")), Option(Drop(Text("*"))), Series(Drop(Text("}")), dwsp__), mandatory=3)
    displaymath = Alternative(_dmath_long_form, _dmath_short_form)
    verbatim_text = RegExp('(?:(?!\\\\end{verbatim})[\\\\]?[^\\\\]*)*')
    verbatim = Series(Series(Drop(Text("\\begin{verbatim}")), dwsp__), verbatim_text, Series(Drop(Text("\\end{verbatim}")), dwsp__), mandatory=2)
    quotation = Alternative(Series(Series(Drop(Text("\\begin{quotation}")), dwsp__), sequence, Series(Drop(Text("\\end{quotation}")), dwsp__), mandatory=2), Series(Series(Drop(Text("\\begin{quote}")), dwsp__), sequence, Series(Drop(Text("\\end{quote}")), dwsp__), mandatory=2))
    figure = Series(Series(Drop(Text("\\begin{figure}")), dwsp__), sequence, Series(Drop(Text("\\end{figure}")), dwsp__), mandatory=2)
    SubSubSection = Series(Drop(Text("\\subsubsection")), Option(hide_from_toc), heading, ZeroOrMore(Alternative(sequence, Paragraphs)))
    _itemsequence = Series(Option(_WSPC), ZeroOrMore(Series(Alternative(item, _command), Option(_WSPC))))
    description = Series(Series(Drop(Text("\\begin{description}")), dwsp__), _itemsequence, Series(Drop(Text("\\end{description}")), dwsp__), mandatory=2)
    enumerate = Series(Series(Drop(Text("\\begin{enumerate}")), dwsp__), _itemsequence, Series(Drop(Text("\\end{enumerate}")), dwsp__), mandatory=2)
    itemize_kind = RegExp('item\\w+')
    itemize = Series(Drop(Text("\\begin{")), itemize_kind, Series(Drop(Text("}")), dwsp__), _itemsequence, Drop(Text("\\end{")), itemize_kind, Series(Drop(Text("}")), dwsp__), mandatory=4)
    end_generic_block = Series(end_environment, Alternative(Series(Option(Series(dwsp__, Drop(Text("&")))), LFF), Series(dwsp__, Lookahead(Drop(Text("}"))))), mandatory=1)
    begin_generic_block = Series(Lookbehind(_LB), begin_environment)
    generic_block = Series(begin_generic_block, ZeroOrMore(Alternative(sequence, item)), end_generic_block, mandatory=2)
    math_block = Alternative(equation, eqnarray, displaymath, align)
    _known_environment = Alternative(itemize, enumerate, description, figure, tabular, tabbing, quotation, verbatim, math_block)
    _has_block_start = Drop(Alternative(Drop(Text("\\begin{")), Drop(Text("\\["))))
    preamble = OneOrMore(Series(Option(_WSPC), Alternative(_command, Series(NegativeLookahead(Series(Drop(Text("\\begin{document}")), dwsp__)), _block_environment))))
    SubSubSections = OneOrMore(Series(Option(_WSPC), SubSubSection))
    Index = Series(Option(_WSPC), Series(Drop(Text("\\printindex")), dwsp__))
    Bibliography = Series(Option(_WSPC), Series(Drop(Text("\\bibliography")), dwsp__), heading)
    SubSection = Series(Drop(Text("\\subsection")), Option(hide_from_toc), heading, ZeroOrMore(Alternative(sequence, SubSubSections, Paragraphs)))
    SubSections = OneOrMore(Series(Option(_WSPC), SubSection))
    Section = Series(Drop(Text("\\section")), Option(hide_from_toc), heading, ZeroOrMore(Alternative(sequence, SubSections, Paragraphs)))
    Sections = OneOrMore(Series(Option(_WSPC), Section))
    Chapter = Series(Drop(Text("\\chapter")), Option(hide_from_toc), heading, ZeroOrMore(Alternative(sequence, Sections, Paragraphs)))
    Chapters = OneOrMore(Series(Option(_WSPC), Chapter))
    document = Series(Option(_WSPC), Series(Drop(Text("\\begin{document}")), dwsp__), frontpages, Alternative(Chapters, Sections), Option(Bibliography), Option(Index), Option(_WSPC), Series(Drop(Text("\\end{document}")), dwsp__), Option(_WSPC), EOF, mandatory=2)
    param_block.set(Series(Series(Drop(Text("{")), dwsp__), Option(parameters), Series(Drop(Text("}")), dwsp__)))
    block.set(Series(Series(Drop(Text("{")), dwsp__), _block_content, Drop(Text("}")), mandatory=2))
    _inline_math_text.set(ZeroOrMore(Alternative(_inline_math_core, Series(_BACKSLASH, Option(Alternative(_LBRACE, _RBRACE, _DOLLAR))), Series(_LBRACE, _inline_math_text, _RBRACE))))
    _text_element.set(Alternative(_line_element, LINEFEED))
    paragraph.set(OneOrMore(Series(NegativeLookahead(blockcmd), _text_element, Option(S))))
    block_of_paragraphs.set(Series(Series(Drop(Text("{")), dwsp__), Option(sequence), Series(Drop(Text("}")), dwsp__), mandatory=2))
    tabular_config.set(Series(Series(Drop(Text("{")), dwsp__), OneOrMore(Alternative(Series(Option(cfg_left_seq), cfg_celltype, Option(cfg_unit), Option(cfg_right_seq)), cfg_separator, cfg_colsep, Drop(RegExp(' +')))), Series(Drop(Text("}")), dwsp__), mandatory=2))
    item.set(Series(Series(Drop(Text("\\item")), dwsp__), Option(config), sequence, mandatory=2))
    _block_environment.set(Series(Lookahead(_has_block_start), Alternative(_known_environment, generic_block)))
    latexdoc = Series(preamble, document, mandatory=1)
    root__ = latexdoc
        
parsing: PseudoJunction = create_parser_junction(LaTeXGrammar)
get_grammar = parsing.factory # for backwards compatibility, only


#######################################################################
#
# AST SECTION - Can be edited. Changes will be preserved.
#
#######################################################################


def streamline_whitespace(context):
    # if context[-2].name == TOKEN_PTYPE:
    #     return
    node = context[-1]
    assert node.name in ['WSPC', ':Whitespace', 'S']
    s = node.content
    if s.find('%') >= 0:
        node.result = '\n'
        # c = s.find('%')
        # node.result = ('  ' if (n >= c) or (n < 0) else '\n')+ s[c:].rstrip(' \t')
        # node.parser = MockParser('COMMENT', '')
    elif s.find('\n') >= 0:
        node.result = '\n'
    else:
        node.result = ' ' if s else ''


def watch(node):
    print(node.as_sxpr())

# flatten_structure = flatten(lambda context: is_one_of(
#     context, {"Chapters", "Sections", "SubSections", "SubSubSections", "Paragraphs",
#               "SubParagraphs", "sequence"}), recursive=True)


def transform_generic_command(context: List[Node]):
    node = context[-1]
    if node.children and node.children[0].name in ('CMDNAME', 'TXTCOMMAND'):
        node.name = 'cmd_' + node.children[0].content.lstrip('\\')
        node.result = node.children[1:]


def transform_generic_block(context: List[Node]):
    node = context[-1]
    if not node.children or not node.children[0].children:
        context[0].new_error(node, 'unknown kind of block: '
            + abbreviate_middle(flatten_sxpr(node.as_sxpr()), 60))
    else:
        # assert node.children[0].name == "begin_generic_block"
        # assert node.children[0].children[0].name == "begin_environment"
        # assert node.children[-1].name == "end_generic_block"
        # assert node.children[-1].children[0].name == "end_environment"
        node.name = 'env_' + node.children[0].children[0].content.lstrip('\\')
        node.result = node.children[1:-1]


def transform_generic_itemization(path: List[Node]):
    node = path[-1]
    if not node.children or node[0].name != "itemize_kind" or node[-1].name != "itemize_kind":
        cast(RootNode, path[0]).new_error(node, 'bad tree-structure for itemize: '
            + abbreviate_middle(flatten_sxpr(node.as_sxpr()), 60))
        return
    kind = node[0].content
    if node[-1].content != kind:
        cast(RootNode, path[0]).new_error(
            node, f'\\end{{{node[-1].content}}} does not match \\begin{{{kind}}}!')
        return
    if kind != 'itemize':   add_class(node, kind)
    node.result = node.children[1:-1]


def replace_Umlaut(context: List[Node]):
    umlaute = {'"a': 'ä', '"o': 'ö', '"u': 'ü', '"e': 'ë',
               '"A': 'Ä', '"Ö': 'Ö', '"U': 'Ü', "'A": 'Á', "'E": 'É',
               "''a": 'ä', "''o": 'ö', "''u": 'ü', "''e": 'ë',
               "''A": 'Ä', "''Ö": 'Ö', "''U": 'Ü', "'A": 'Á', "'E": 'É',
               "'a": 'á', "'e": 'é', "'i": 'í', "'o": 'ó', "'u": 'ú',
               "`a": 'à', "`e": 'è', "`i": 'ì', "`o": 'ò', "`u": 'ù',
               "^a": 'â', "^e": 'ê', "^i": 'î', "^o": 'ô', "^u": 'û',
               '^C': 'Ĉ',
               '^c': 'ĉ', '^g': 'ĝ', "'n": 'ń', '~n': 'ñ',
               '^j': 'ĵ'}
    node = context[-1]
    try:
        node.result = umlaute[node.content.replace('\\','').replace('{', '').rstrip('}')]
    except KeyError as e:
        print("UMLAUT NICHT GEFUNDEN:", e)


def replace_quotationmark(context: List[Node]):
    quotationmarks = { '``': '“', "''": '”', '"`': '„', '"' + "'": '”' }
    node = context[-1]
    content = node.content
    node.result = quotationmarks.get(content, content)
    

def is_expendable(context: List[Node]):
    node = context[-1]
    return not node._result and node.name != "math_mode" \
            and node.name[0:4] not in ('cmd_', 'cfg_', )


def show(context: List[Node]):
    print(context[-1].as_xml())


LaTeX_AST_transformation_table = {
    # AST Transformations for the LaTeX-grammar
    "<": [flatten, remove_children_if(is_expendable)],
    "latexdoc": [],
    "document": [],
    "pdfinfo": [],
    "_TEXT_NOPAR": [apply_unless(normalize_whitespace, has_children)],
    "info_assoc": [change_name('association'), replace_by_single_child],
    "info_key": [change_name('key')],
    "info_value": [apply_unless(normalize_whitespace, has_children), change_name('value')],
    "parameters": [replace_by_single_child],
    "association": [replace_by_single_child],
    "key": reduce_single_child,
    "frontpages": reduce_single_child,
    "Chapters, Sections, SubSections, SubSubSections, Paragraphs, SubParagraphs": [],
    "Chapter, Section, SubSection, SubSubSection, Paragraph, SubParagraph": [],
    "hide_from_toc, no_numbering": [replace_content_with('')],
    "heading": reduce_single_child,
    "Bibliography": [],
    "Index": [],
    "_block_environment": replace_by_single_child,
    "_known_environment": replace_by_single_child,
    "generic_block": [transform_generic_block],
    "generic_command, text_command": [transform_generic_command, reduce_single_child],
    "begin_generic_block, end_generic_block": [],
    "itemize": [transform_generic_itemization],
    "enumerate": [],
    "item": [],
    "figure": [],
    "quotation": [reduce_single_child, remove_brackets],
    "verbatim": [],
    "tabular": [],
    "tabular_config, block_of_paragraphs": [remove_brackets, reduce_single_child],
    "tabular_row": [remove_tokens('&', '\\')],
    "tabular_cell": [remove_whitespace],
    "multicolumn": [remove_tokens('{', '}')],
    "hline": [remove_whitespace, reduce_single_child],
    "ref, label, url": reduce_single_child,
    "sequence": [],
    "paragraph": [strip(is_one_of({'S'}))],
    "_text_element": replace_by_single_child,
    "_line_element": replace_by_single_child,
    "_inline_environment": replace_by_single_child,
    "_known_inline_env": replace_by_single_child,
    "generic_inline_env": [],
    "_begin_inline_env, _end_inline_env": [replace_by_single_child],
    "begin_environment, end_environment": [],  # [remove_brackets, reduce_single_child],
    "inline_math": [reduce_single_child],
    "_command": replace_by_single_child,
    "_known_command": replace_by_single_child,
    "citet, citep": [reduce_single_child],
    "footnote": [],
    "includegraphics": [],
    "caption": [],
    "config": [reduce_single_child],
    "cfg_text": [reduce_single_child],
    "block": [reduce_single_child],
    "flag": [reduce_single_child],
    "text": collapse,
    "urlstring": collapse,
    "no_command, blockcmd": [],
    "_structure_name": [],
    "CMDNAME": [remove_whitespace, reduce_single_child],
    "TXTCOMMAND": [remove_whitespace, reduce_single_child],
    "NAME": [reduce_single_child, remove_whitespace, reduce_single_child],
    "ESCAPED": [apply_ifelse(transform_result(lambda result: result[1:]),
                             replace_content_with('~'),
                             lambda ctx: '~' not in ctx[-1].content)],
    "UMLAUT": replace_Umlaut,
    "LEERZEICHEN": replace_content_with(' '),
    "QUOTEMARK": replace_quotationmark,
    "BRACKETS": [],
    # "LF": [],
    "_GAP": [],
    "_LB": [],
    "_BACKSLASH": [],
    "EOF": [],
    "_PARSEP": [replace_content_with('\n\n')],
    ":Whitespace, _WSPC, S": streamline_whitespace,
    "WARN_Komma": add_error('No komma allowed at the end of a list', WARNING),
    "*": apply_if(replace_by_single_child,
                  lambda ctx: ctx[-1].name[:4] in ('cmd_', 'env_'))
}

def LaTeXTransformer() -> TransformerFunc:
    return partial(transformer, transformation_table=LaTeX_AST_transformation_table.copy(),
                   src_stage='cst', dst_stage='ast')

ASTTransformation: Junction = Junction(
    'cst', ThreadLocalSingletonFactory(LaTeXTransformer), 'ast')


#######################################################################
#
# COMPILER SECTION - Can be edited. Changes will be preserved.
#
#######################################################################


def empty_defaultdict():
    """Returns a defaultdict with an empty defaultdict as default value."""
    return collections.defaultdict(empty_defaultdict)


class LaTeXCompiler(Compiler):
    """Compiler for the abstract-syntax-tree of a LaTeX source file.
    """
    KNOWN_DOCUMENT_CLASSES = {'book', 'article'}
    KNOWN_LANGUAGES = {'english', 'german'}

    def __init__(self):
        super(LaTeXCompiler, self).__init__()
        self.forbid_returning_None = True  # set to False if any compilation-method is allowed to return None
        self.metadata = collections.defaultdict(empty_defaultdict)

    def reset(self):
        super().reset()
        # initialize your variables here, not in the constructor!
        self.tree.inline_tags = set()  # {'paragraph'}
        self.tree.empty_tags = set()
        self.tree.string_tags = {'S', 'PARSEP'}

    def prepare(self, root: RootNode) -> None:
        assert root.stage == "ast", f"Source stage `ast` expected, `but `{root.stage}` found."

    def finalize(self, result: Any) -> Any:
        if isinstance(self.tree, RootNode):
            self.tree.stage = "LaTeXML".lower()
        return result

    def fallback_generic_command(self, node: Node) -> Node:
        # if not node.result:
        #      return EMPTY_NODE
        return node

    def fallback_generic_environment(self, node) -> Node:
        node = super().fallback_compiler(node)
        # node.name = 'VOID'
        return node

    def fallback_compiler(self, node: Node) -> Any:
        if node.name.startswith('cmd_'):
            node = self.fallback_generic_command(node)
        elif node.name.startswith('env_'):
            node = self.fallback_generic_environment(node)
        else:
            node = super().fallback_compiler(node)
        # replace void nodes by their children
        if node.children:
            result = [];  void_flag = False
            for child in node.children:
                if child.name == 'VOID' and child.children:
                    result.extend(child.children);  void_flag = True
                else:
                    result.append(child)
            if void_flag:  # use flag, because assignment can be costly
                node.result = tuple(result)
        return node

    def on_latexdoc(self, node):
        return self.fallback_compiler(node)

    def get_author_year(self, bibkey: str) -> str:
        return bibkey  # for now...

    def arange_citation(self, node):
        node = self.fallback_compiler(node)
        if node.children:
            config = node.pick('config')
            block = node.pick('block')
            bibkey = block.content
            if config is not None:
                assert len(node.children) == 2
                block.result = self.get_author_year(bibkey)
                node.result = (block, Node('text', ', '), config)
            else:
                node.result = self.get_author_year(bibkey)
        else:
            bibkey = node.content
            node.result = self.get_author_year(bibkey)

    def on_citet(self, node):
        self.arange_citation(node)
        return node

    def on_citep(self, node):
        self.arange_citation(node)
        if node.children:
            node.result = (Node('text', '('), *node.children, Node('text', ')'))
        else:
            node.result = '(' + node.content + ')'
        return node

    def on_documentclass(self, node):
        """
        Saves the documentclass (if known) and the language (if given)
        in the metadata dictionary.
        """
        if 'config' in node:
            for it in {part.strip() for part in node['config'].content.split(',')}:
                if it in self.KNOWN_LANGUAGES:
                    if 'language' in self.metadata:
                        self.metadata['language'] = it
                    else:
                        self.tree.new_error(node, 'Only one document language supported. '
                                            'Using %s, ignoring %s.'
                                            % (self.metadata['language'], it), WARNING)
        if node['block'].content in self.KNOWN_DOCUMENT_CLASSES:
            self.metadata['documentclass'] = node['block'].content
        return node


compiling: Junction = create_junction(
    LaTeXCompiler, "ast", "LaTeXML".lower())


#######################################################################
#
# END OF DHPARSER-SECTIONS
#
#######################################################################

#######################################################################
#
# Post-Processing-Stages [add one or more postprocessing stages, here]
#
#######################################################################

# class PostProcessing(Compiler):
#     ...

# # change the names of the source and destination stages. Source
# # ("LaTeX") in this example must be the name of some earlier stage, though.
# postprocessing: Junction = create_junction("LaTeX", "refined", PostProcessing)
#

#######################################################################

# Add your own stages to the junctions and target-lists, below
# (See DHParser.compile for a description of junctions)

# add your own post-processing junctions, here, e.g. postprocessing.junction
junctions = set([ASTTransformation, compiling])
# put your targets of interest, here. A target is the name of result (or stage)
# of any transformation, compilation or postprocessing step after parsing.
# Serializations of the stages listed here will be written to disk when
# calling process_file() or batch_process().
targets = set([compiling.dst])
# add one or more serializations for those targets that are node-trees
serializations = expand_table(dict([('*', ['xml'])]))

#######################################################################

def compile_src(source: str, target: str = "LaTeXML".lower()) -> Tuple[Any, List[Error]]:
    """Compiles the source to a single targte and returns the result of the compilation
    as well as a (possibly empty) list or errors or warnings that have occurred in the
    process.
    """
    full_compilation_result = full_compile(
        source, preprocessing.factory, parsing.factory, junctions, set([target]))
    return full_compilation_result[target]


def process_file(source: str, out_dir: str = '') -> str:
    """Compiles the source and writes the serialized results back to disk,
    unless any fatal errors have occurred. Error and Warning messages are
    written to a file with the same name as `result_filename` with an
    appended "_ERRORS.txt" or "_WARNINGS.txt" in place of the name's
    extension. Returns the name of the error-messages file or an empty
    string, if no errors or warnings occurred.
    """
    return dsl.process_file(source, out_dir, preprocessing.factory, parsing.factory,
                            junctions, targets, serializations)


def _process_file(args: Tuple[str, str]) -> str:
    return process_file(*args)


def batch_process(file_names: List[str], out_dir: str,
                  *, submit_func: Callable = None,
                  log_func: Callable = None,
                  cancel_func: Callable = never_cancel) -> List[str]:
    """Compiles all files listed in file_names and writes the results and/or
    error messages to the directory `our_dir`. Returns a list of error
    messages files.
    """
    return dsl.batch_process(file_names, out_dir, _process_file,
        submit_func=submit_func, log_func=log_func, cancel_func=cancel_func)


def main(called_from_app=False) -> bool:
    # recompile grammar if needed
    scriptpath = os.path.abspath(__file__)
    if scriptpath.endswith('Parser.py'):
        grammar_path = scriptpath.replace('Parser.py', '.ebnf')
    else:
        grammar_path = os.path.splitext(scriptpath)[0] + '.ebnf'
    parser_update = False

    def notify():
        nonlocal parser_update
        parser_update = True
        print('recompiling ' + grammar_path)

    if os.path.exists(grammar_path) and os.path.isfile(grammar_path):
        if not recompile_grammar(grammar_path, scriptpath, force=False, notify=notify):
            error_file = os.path.basename(__file__)\
                .replace('Parser.py', '_ebnf_MESSAGES.txt')
            with open(error_file, 'r', encoding="utf-8") as f:
                print(f.read())
            sys.exit(1)
        elif parser_update:
            print(os.path.basename(__file__) + ' has changed. '
                  'Please run again in order to apply updated compiler')
            sys.exit(0)
    else:
        print('Could not check whether grammar requires recompiling, '
              'because grammar was not found at: ' + grammar_path)

    from argparse import ArgumentParser
    parser = ArgumentParser(description="Parses a LaTeX-file and shows its syntax-tree.")
    parser.add_argument('files', nargs='*' if called_from_app else '+')
    parser.add_argument('-d', '--debug', action='store_const', const='debug',
                        help='Store debug information in LOGS subdirectory')
    parser.add_argument('-o', '--out', nargs=1, default=['out'],
                        help='Output directory for batch processing')
    parser.add_argument('-v', '--verbose', action='store_const', const='verbose',
                        help='Verbose output')
    parser.add_argument('-f', '--force', action='store_const', const='force',
                        help='Write output file even if errors have occurred')
    parser.add_argument('--singlethread', action='store_const', const='singlethread',
                        help='Run batch jobs in a single thread (recommended only for debugging)')
    outformat = parser.add_mutually_exclusive_group()
    outformat.add_argument('-x', '--xml', action='store_const', const='xml', 
                           help='Format result as XML')
    outformat.add_argument('-s', '--sxpr', action='store_const', const='sxpr',
                           help='Format result as S-expression')
    outformat.add_argument('-m', '--sxml', action='store_const', const='sxml',
                           help='Format result as S-expression')
    outformat.add_argument('-t', '--tree', action='store_const', const='tree',
                           help='Format result as indented tree')
    outformat.add_argument('-j', '--json', action='store_const', const='json',
                           help='Format result as JSON')

    args = parser.parse_args()
    file_names, out, log_dir = args.files, args.out[0], ''

    if args.debug is not None:
        log_dir = 'LOGS'
        access_presets()
        set_preset_value('history_tracking', True)
        set_preset_value('resume_notices', True)
        set_preset_value('log_syntax_trees', frozenset(['cst', 'ast']))  # don't use a set literal, here!
        finalize_presets()
    start_logging(log_dir)

    if args.singlethread:
        set_config_value('batch_processing_parallelization', False)

    def echo(message: str):
        if args.verbose:
            print(message)

    if called_from_app and not file_names:  return False

    batch_processing = True
    if len(file_names) == 1:
        if os.path.isdir(file_names[0]):
            dir_name = file_names[0]
            echo('Processing all files in directory: ' + dir_name)
            file_names = [os.path.join(dir_name, fn) for fn in os.listdir(dir_name)
                          if os.path.isfile(os.path.join(dir_name, fn))]
        elif not ('-o' in sys.argv or '--out' in sys.argv):
            batch_processing = False

    if batch_processing:
        if not os.path.exists(out):
            os.mkdir(out)
        elif not os.path.isdir(out):
            print('Output directory "%s" exists and is not a directory!' % out)
            sys.exit(1)
        error_files = batch_process(file_names, out, log_func=print if args.verbose else None)
        if error_files:
            category = "ERRORS" if any(f.endswith('_ERRORS.txt') for f in error_files) \
                else "warnings"
            print("There have been %s! Please check files:" % category)
            print('\n'.join(error_files))
            if category == "ERRORS":
                sys.exit(1)
    else:
        result, errors = compile_src(file_names[0])

        if not errors or (not has_errors(errors, ERROR)) \
                or (not has_errors(errors, FATAL) and args.force):
            if args.xml:  outfmt = 'xml'
            elif args.sxpr:  outfmt = 'sxpr'
            elif args.sxml:  outfmt = 'sxml'
            elif args.tree:  outfmt = 'tree'
            elif args.json:  outfmt = 'json'
            else:  outfmt = 'default'
            print(result.serialize(how=outfmt) if isinstance(result, Node) else result)
            if errors:  print('\n---')

        for err_str in canonical_error_strings(errors):
            print(err_str)
        if has_errors(errors, ERROR):  sys.exit(1)

    return True


if __name__ == "__main__":
    main()
