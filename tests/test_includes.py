
import os
import sys

scriptpath = str(os.path.dirname(__file__)) or '.'
sys.path.append(os.path.abspath(os.path.join(scriptpath, '..')))

from LaTeXParser import compile_src

class TestInclude:
    def test_simple_include(self):
        result, errors = compile_src('tests/data/main1.tex')
        for e in errors: print(e)
        print(result.as_sxpr())

    def test_nested_include(self):
        pass

    def test_error_reporting(self):
        pass

    def test_nested_include_with_error_resporting(self):
        pass


