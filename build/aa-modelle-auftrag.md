Du frischst die Werte von Artificial Analysis in den Modell-Steckbriefen auf.
Lies zuerst CLAUDE.md, besonders den Abschnitt „The coding-agent benchmark
rots the same way“. Seine Regeln binden dich: nie eine Zahl, einen
Modellnamen oder einen Link erfinden, site/ nicht von Hand bearbeiten, nie auf
main pushen.

Du bist {AGENT}. Das Datum heute: `date +%F`.

## 0. Gibt es den Vorschlag schon?

`gh pr list --state open --search "head:aa-werte/"` zeigt offene Vorschläge
dieser Routine. Ist einer von heute dabei, egal von wem, schreib `pr` in
`aa-status.txt` und hör auf. Zwei PRs zum selben Stand sind doppelte
Prüfarbeit.

## 1. Kommst du an die Quelle?

Öffne https://artificialanalysis.ai/leaderboards/models. Liefert die Seite
keine Rangliste (gesperrt, 403, leere Seite, nur Skripte ohne Zahlen), dann
schreib in die Datei `aa-status.txt` im Wurzelverzeichnis genau das Wort

    kein-zugang

und hör auf. Ändere nichts, öffne nichts. Ein anderer Agent übernimmt dann.
Rate in diesem Fall keine Werte aus dem Gedächtnis.

## 2. Die zehn besten Modelle

Maßstab ist der Intelligence Index. AA listet ein Modell oft mehrfach, je
Reasoning-Stufe getrennt. Fasse die Varianten eines Modells zusammen und
zähle es einmal, an der Stelle seiner besten Zeile. Die ersten **zehn
verschiedenen** Modelle sind deine Liste. Darunter liest du nicht weiter.

## 3. Für jedes dieser zehn Modelle

Prüf in `content/steckbrief.json`, ob der Katalog die Familie führt (über
`aa.url` und den Namen).

- **Der Katalog führt sie:** Öffne die AA-Modellseite und frische den
  `aa`-Block auf: `intel`, `speed`, `cost`, `verb`, jeweils Wert `v` und Rang
  `rank` (`#n/N`, wie AA ihn zeigt), dazu `u` (1–4), das AA als „N out of 4
  units“ ausweist. **`u` nie aus dem Rang errechnen**: Ist es nicht lesbar,
  bleibt der bisherige Wert stehen, und du vermerkst das im PR. Setz
  `"checked"` auf heute, auch wenn sich nichts bewegt hat. Führt AA von
  derselben Linie eine neuere Generation, hebst du den Steckbrief darauf, wie
  CLAUDE.md es beschreibt: `name`, `blurb`, `tip` (beide Sprachen), `aa.url`
  und die Werte zusammen.
- **Der Katalog führt sie nicht:** Leg **keinen** Steckbrief an. Nenn das
  Modell mit Rang im PR unter „Kandidaten“. Ob es aufgenommen wird, entscheidet
  der Maintainer.

`plans`, `billing` und `plansChecked` fasst du nicht an, die gehören der
Kreuzprüfung. Steckbriefe außerhalb der zehn fasst du auch nicht an.

## 4. Übergabe

`python3 build/build.py` muss mit Exit 0 enden. Dann:

- Zweig `aa-werte/<datum>-{AGENT}`, committen, pushen.
- Pull Request gegen `main` mit `gh pr create`, Titel
  `[AA · {AGENT}] Top 10 vom <datum>`.
- Im PR-Text: die zehn Modelle mit Rang. Je aufgefrischtem Steckbrief eine
  Zeile mit alt → neu für Intelligenz, Tempo, Kosten und Ausführlichkeit, dazu
  die AA-URL und die Variante, die du genommen hast. Dann die Kandidaten. Und
  ausdrücklich: was du nicht prüfen konntest.

Schreib zum Schluss in `aa-status.txt` genau ein Wort: `pr`, wenn du einen
Pull Request geöffnet hast, `unveraendert`, wenn keiner der zehn im Katalog
steht und es nichts zu tun gab. Committe `aa-status.txt` nicht.
