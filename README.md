LaTeX2TEIXML
============

Parser and (TEI-)XML/HTML-converter for a subset of LaTeX.

This software is open source software under the Apache 2.0-License (see section License, below).

Copyright 2022  Eckhart Arnold, Bavarian Academy of Sciences and Humanities

Status
------

Currently, this software is in early alpha-stage. There is a working LaTeX-Parser
for a common subset of LaTeX. The XML-output presently represents only an Abstract-Syntax-Tree
of the LaTeX-document. Conversion to TEI-XMl and/or HTML is pending. Use at your own risk...

Usage
-----

This is an early experimental version of the software!

To convert a LaTeX-file to XML, either call the file `LaTeXApp.py`, 
or - if you have not installed Python on your system - one of the 
executables in the "dist"-subdirectory and select
the file to convert by clicking on the "Pick sources...:" button, or
type on the command line:

    $ python LaTeXParser.py --xml FILENAME.tex

Presently, the generated XML more or 
less represents the abstract-syntax-tree of the LaTeX-document. 
Support for TEI-XML and HTML will be added in the future.

LaTeX2TEIXML requires the [DHParser](https://gitlab.lrz.de/badw-it/DHParser)-framework. 
For convenience, LaTeX2TEIXML comes with its own copy of DHParser in a subdirectory.
This also helps to avoid Version-incompatibilities between DHParser and LaTeX2TEIXML,
because the bundled DHParser-version is always sure to work.

Alternatively, it is of course also possible to install DHParser in the usual way
with Python's package-manager pip:

    $ pip install DHParser

LaTeX2TEIXML assumes LaTeX-files to be stored in the Unicode utf-8-format. Older manuscripts
can be converted with the `tex2utf8.py`-script. 

See: https://tex.stackexchange.com/questions/4201/is-there-a-bnf-grammar-of-the-tex-language 
for why only a subset of LaTeX can be supported. 

Executables
-----------

In the "dist"-subdirectories there may be executables of t

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
