Du entscheidest die Kreuzprüfung der Preise. Lies zuerst CLAUDE.md —
seine Regeln binden dich, besonders: nie eine Angabe oder einen Link
erfinden, site/ nicht von Hand bearbeiten, nie auf main pushen.

vergleich.md stellt zwei unabhängige Befunde gegenüber, die Gemini
und GLM zu denselben Steckbriefen abgelesen haben, dazu den Stand
des Katalogs. build/kreuzpruefung.py hat den Vergleich gerechnet,
nicht ein Modell: was dort als einig steht, ist in Betrag, Währung,
Einheit, billing und Gratisstufe deckungsgleich.

Geh die Tabelle Eintrag für Eintrag durch. Das Urteil sagt dir,
ob du die Seite abrufen musst. Ruf keine Seite ab, bei der die
Tabelle es nicht verlangt:

- **einig** — übernehmen, **nicht** abrufen. Zwei unabhängige
  Leser, die dasselbe gelesen haben, sind die Prüfung. `plans` in
  beiden Sprachen schreiben, `plansChecked` auf heute.
- **einig (Stichprobe)** — abrufen. Etwa jeder dritte einige
  Eintrag wird nachgeprüft, damit der Fall auffällt, dass beide
  dieselbe veraltete Seite gelesen haben. Bestätigt die Seite es,
  wie bei einig verfahren; weicht sie ab, wie bei uneinig.
- **ohne Preis** — beide haben auf der Seite keinen Preis
  gefunden. Nicht abrufen. Den Eintrag entsprechend formulieren
  (etwa quelloffen und kostenfrei, Kosten entstehen erst beim
  Modellanbieter) und `plansChecked` auf heute setzen. Dass es
  nichts zu bezahlen gibt, haben zwei Leser unabhängig bestätigt.
- **uneinig** — die Seite des Anbieters selbst lesen und
  entscheiden. Welcher Befund stimmte und warum, kommt in den
  PR-Text.
- **einseitig** — gilt als ungeprüft, ein einzelner Befund ist
  keine Bestätigung. Selbst nachschlagen wie bei uneinig.
- **leer** — nichts ändern. `plansChecked` bleibt, wie es ist, damit
  der Eintrag beim nächsten Lauf wieder vorne steht. Im PR nennen.

Zwei Regeln zum Vorgehen, weil dieser Schritt sonst teuer wird:
Ruf jede Seite höchstens einmal ab, und arbeite einen Eintrag
fertig, bevor du den nächsten anfängst. Jede abgerufene Seite
bleibt im Verlauf und wird bei jedem weiteren Zug mitgeschickt.

Lässt sich ein Wert nicht belegen: Feld weglassen, `plansChecked`
NICHT setzen, im PR-Text nennen. Ein geratener Preis ist schlimmer
als ein fehlender.

Nicht nur die Zahlen. Ist das Abrechnungsmodell gewandert — ein Abo
neben der Nutzungsabrechnung, eine geöffnete API, eine gestrichene
Gratisstufe —, dann wandert `billing` in derselben Änderung mit.
Ist ein Produkt gar nicht mehr erhältlich, sag das im Eintrag,
statt die alte Zahl am Leben zu halten.

`plans` steht in beiden Sprachen, und das Deutsche ist Deutsch, keine
Übersetzung des Englischen. Halte dich an die Form der Nachbarn.

Ändere ausschließlich content/steckbrief.json. Dann:

    python3 build/build.py

Das muss Exit 0 liefern. auftrag.json, befund-*.json, vergleich.md
und vergleich.json sind Lauf-Artefakte und gehören nicht in den
Commit.

Branch `kreuzpruefung/preise-<JJJJ-MM-TT>-{ENTSCHEIDER}`, Pull Request gegen main
mit `gh pr create`, Titel mit `[Kreuzprüfung · {ENTSCHEIDER}]` davor und in Klartext,
was geprüft wurde.

In den PR-Text gehören:

1. Die Tabelle aus vergleich.md.
2. Für jede geänderte Angabe die Quell-URL, von der sie stammt.
3. Was du NICHT geprüft hast.
4. Je Steckbrief eine Bilanzzeile in genau dieser Form, damit sich
   später auszählen lässt, welcher Agent wie zuverlässig liest:

   BILANZ <JJJJ-MM-TT> <Steckbrief> gemini=<richtig|daneben|nichts> zai=<richtig|daneben|nichts> entscheider={ENTSCHEIDER}

   `richtig` heißt: der Befund deckte sich mit dem, was du auf der
   Seite gelesen hast. `daneben`: er wich davon ab. `nichts`: dieser
   Agent hat zu diesem Steckbrief nichts geliefert. Bei einem
   einigen Eintrag, den die Quelle bestätigt hat, sind beide
   `richtig`.
