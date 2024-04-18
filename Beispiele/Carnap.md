# Carnap-Beispiel

## Selbstdefinierte Befehle 1

# Beispiel dasgupta

    Vortrag Professor Dasgupta\IN{\dasgupta} aus Kalkutta\IO{Kalkutta} ,,Geistiges Leben in Indien``, auf Englisch.


## Selbstdefinierte Befehle 2

TeX-code:

    \tbentryllong{24}{3}{1910}{}\ort{Patras}\foto{Wilhelm Dörpfeld}
    \textit{V}\,\editor{ormittags} 11\textsuperscript{h} Abreise nach \textit{\uline{Patras}}\IO{Griechenland!Patras}, An\editor{kunft} abends. Stoltenhoffs\IN{\stoltenhoffs}.\fnE{Die Griechenlandreise, an der Carnap hier unter Leitung seines Onkels Wilhelm Dörp\-feld teilgenommen hat, ist ausführlich dokumentiert in Rüter, ,,Mit Dörpfeld nach Leukas-Ithaka und dem Peloponnes``, hier relevant vor allem Teil I ,,Reisebericht`` (3\hbox{--}33). Eine ausführliche Dokumentation der Reise durch Carnap selbst ist in den tagebuchartigen Briefen an seine Mutter und Schwester (\href{http://doi.org/10.48666/807652}{RC~025"~94"~02}) zu finden.}

"Roher" Syntax-Baum:

    <paragraph>
      <cmd_tbentryllong>
        <block>24</block>
        <block>3</block>
        <block>1910</block>
      </cmd_tbentryllong>
      <cmd_ort>Patras</cmd_ort>
      <cmd_foto>Wilhelm Dörpfeld</cmd_foto>
      <text_command>
        <TXTCOMMAND>\textit</TXTCOMMAND>
      </text_command>
      <block>V</block>
      <text>,</text>
      <cmd_editor>ormittags</cmd_editor>
      <text>11</text>
      <text_command>
        <TXTCOMMAND>\textsuperscript</TXTCOMMAND>
      </text_command>
      <block>h</block>
      <S> </S>
      <text>Abreise nach </text>
      <text_command>
        <TXTCOMMAND>\textit</TXTCOMMAND>
      </text_command>
      <cmd_uline>Patras</cmd_uline>
      <cmd_IO>Griechenland!Patras</cmd_IO>
      <text>, An</text>
      <cmd_editor>kunft</cmd_editor>
      <text>abends. Stoltenhoffs</text>
      <cmd_IN></cmd_IN>
      <text>.</text>
      <cmd_fnE>
        <text>Die Griechenlandreise, an der Carnap hier unter Leitung seines Onkels Wilhelm Dörpfeld teilgenommen hat, ist ausführlich dokumentiert in Rüter, ,,Mit Dörpfeld nach Leukas-Ithaka und dem Peloponnes“, hier relevant vor allem Teil I ,,Reisebericht“ (3</text>
        <cmd_hbox>--</cmd_hbox>
        <text>33). Eine ausführliche Dokumentation der Reise durch Carnap selbst ist in den tagebuchartigen Briefen an seine Mutter und Schwester (</text>
        <href>
          <urlstring>http://doi.org/10.48666/807652</urlstring>
          <block>RC~025"~94"~02</block>
        </href>
        <text>) zu finden.</text>
      </cmd_fnE>
    </paragraph>

Derselbe Syntax-Baum etwas kompater als S-Ausdruck:

    (paragraph
      (cmd_tbentryllong
        (block "24")
        (block "3")
        (block "1910"))
      (cmd_ort "Patras")
      (cmd_foto "Wilhelm Dörpfeld")
      (text_command
        (TXTCOMMAND "\textit"))
      (block "V")
      (text ",")
      (cmd_editor "ormittags")
      (text "11")
      (text_command
        (TXTCOMMAND "\textsuperscript"))
      (block "h")
      (S " ")
      (text "Abreise nach ")
      (text_command
        (TXTCOMMAND "\textit"))
      (cmd_uline "Patras")
      (cmd_IO "Griechenland!Patras")
      (text ", An")
      (cmd_editor "kunft")
      (text "abends. Stoltenhoffs")
      (cmd_IN)
      (text ".")
      (cmd_fnE
        (text "Die Griechenlandreise, an der Carnap hier unter Leitung seines Onkels Wilhelm Dörpfeld teilgenommen hat, ist ausführlich dokumentiert in Rüter, ,,Mit Dörpfeld nach Leukas-Ithaka und dem Peloponnes“, hier relevant vor allem Teil I ,,Reisebericht“ (3")
        (cmd_hbox "--")
        (text "33). Eine ausführliche Dokumentation der Reise durch Carnap selbst ist in den tagebuchartigen Briefen an seine Mutter und Schwester (")
        (href
          (urlstring "http://doi.org/10.48666/807652")
          (block 'RC~025"~94"~02'))
        (text ") zu finden.")))