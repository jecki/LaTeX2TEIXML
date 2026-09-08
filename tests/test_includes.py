
import os
import sys

scriptpath = str(os.path.dirname(__file__)) or '.'
sys.path.append(os.path.abspath(os.path.join(scriptpath, '..')))

from DHParser.pipeline import PseudoJunction
from DHParser.toolkit import ThreadLocalSingletonFactory

import LaTeXParser
from LaTeXParser import preprocessor_factory, compile_src


def compile_wo_include(source):
    save = LaTeXParser.RE_INPUT
    LaTeXParser.RE_INPUT = r'\\(?:input|include)\{(?P<name>.*)\}'
    LaTeXParser.preprocessing = PseudoJunction(ThreadLocalSingletonFactory(preprocessor_factory))
    result, errors = compile_src(source)
    LaTeXParser.RE_INPUT = save
    LaTeXParser.preprocessing = PseudoJunction(ThreadLocalSingletonFactory(preprocessor_factory))
    return result, errors


class TestInclude:
    def setup_class(cls):
        for fname in os.listdir(os.path.join(scriptpath, 'data')):
            if fname.endswith('.pickledAST'):
                os.remove(os.path.join(scriptpath, 'data', fname))

    def teardown_class(cls):
        for fname in os.listdir(os.path.join(scriptpath, 'data')):
            if fname.endswith('.pickledAST'):
                os.remove(os.path.join(scriptpath, 'data', fname))

    def test_simple_include(self):
        result1, errors1 = compile_wo_include(os.path.join(scriptpath, 'data/main1.tex'))
        result2, errors2 = compile_src(os.path.join(scriptpath, 'data/main1.tex'))
        result3, errors3 = compile_src(os.path.join(scriptpath, 'data/main1.tex'))
        assert not errors1 and not errors2 and not errors3
        assert not result1.equals(result2)  # this is not generally the same, because sections are close within the included file when unsing "\include" vs. "\input"
        assert result2.equals(result3)

    def test_nested_include(self):
        result1, errors1 = compile_src(os.path.join(scriptpath, 'data/main2.tex'))
        result2, errors2 = compile_src(os.path.join(scriptpath, 'data/main2.tex'))
        assert not errors1 and not errors2
        assert result1.equals(result2)

    def test_error_reporting(self):
        result1, errors1 = compile_src(os.path.join(scriptpath, 'data/main3.tex'))
        result2, errors2 = compile_src(os.path.join(scriptpath, 'data/main3.tex'))
        assert result1.equals(result2)
        assert errors1 == errors2
        assert len(errors1) == 2
        err1, err2 = errors1
        assert err1.orig_doc == 'include4.tex'
        assert err2.orig_doc == 'main3.tex'  # errors that are caught only the AST-Transformation
            # can only be related to the location of the faulty include in the main text, unfortunately!
        assert err1.line == 7
        assert err2.line == 17




