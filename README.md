LaTeX2TEIXML
============

Parser and (TEI-)XML/HTML-converter for a subset of LaTeX.

This software is open source software under the Apache 2.0-License (see section License, below).

Copyright 2022  Eckhart Arnold, Bavarian Academy of Sciences and Humanities

Usage
-----

This is an early experimental version of the software!

To convert a LaTeX-file to XML, simply type:

    $ python LaTeXParser.py --xml FILENAME.tex

Presently, the generated XML more or 
less represents the abstract-syntax-tree of the LaTeX-document. 
Support for TEI-XML and HTML will be added in the future.

LaTeX2TEIXMl requires the [DHParser](https://gitlab.lrz.de/badw-it/DHParser)-framework. 
To install the DHParser, type:

    $ pip install DHParser

LaTeX2TEIXML assumes LaTeX-files to be stored in the unicode utf-8-format. Older manuscripts
can be converted with the `tex2utf8.py`-script. 

License
-------

DHParser is open source software under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0).

Copyright 2022  Eckhart Arnold, Bavarian Academy of Sciences and Humanities

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
