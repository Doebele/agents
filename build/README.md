# Bauweg

Die beiden Seiten in `site/` sind ab jetzt **Erzeugnisse**. Wer sie direkt
bearbeitet, verliert die Änderung beim nächsten Bauen.

```bash
python3 build/build.py            # baut site/index.html und site/index.en.html
python3 build/build.py --pruefen  # baut nur und meldet Abweichungen
```

## Wo was liegt

| Datei | Inhalt |
|---|---|
| `content/steckbrief.json` | die 86 Steckbriefe |
| `content/modules.json` | die sieben Bausteine mit Chips und Gruppen |
| `content/glossary.json` | Glossarbegriffe |
| `content/rules.json`, `oc.json`, `hardware.json`, `providers.json`, `loop.json` | die übrigen Datenblöcke |
| `content/ui.json` | die 88 übersetzten Zeilen der Seite |
| `build/template.html` | Gerüst, CSS und Logik — alles, was in beiden Sprachen gleich ist |

## Zweisprachigkeit

Übersetzte Werte stehen als `{"de": …, "en": …}` **direkt nebeneinander**.
Eine fehlende Übersetzung ist dadurch im Nachbarschlüssel sichtbar und wird
zusätzlich von der Prüfung abgefangen. Alles, was in beiden Sprachen gleich
ist — Namen, Links, Farben, Symbole —, steht nur einmal da.

## Was die Prüfung abfängt

Sie läuft vor jedem Schreiben und bricht ab, bevor etwas kaputtgeht:

- eine fehlende oder leere Übersetzung in einem beliebigen Feld
- ein Chip, hinter dem kein Steckbrief liegt
- ein Steckbrief, den keine Kachel erreicht
- eine Marke in der Vorlage ohne Inhalt und umgekehrt

Gegenprobe: Eine geleerte englische Blurb-Zeile und ein gelöschter Steckbrief
werden beide gemeldet, statt in die Seite zu laufen.

## Bekannte Vereinfachungen

`content/ui.json` arbeitet **zeilenweise**, nicht satzweise. Ein Eintrag kann
deshalb auch Markup enthalten. Das ist gewollt: Die zeilenweise Zuordnung ist
verlustfrei belegbar — beide Sprachdateien hatten dieselbe Zeilenzahl und
unterschieden sich ausschließlich durch Austausch, nie durch Einfügung.
Feiner zerlegen lohnt erst, wenn eine dritte Sprache dazukommt.

Die Schlüssel `t001…t088` sind fortlaufend, nicht sprechend. Neue übersetzte
Zeilen bekommen die nächste freie Nummer.

## Herkunft

`build/extract.py` hat Vorlage und Inhalte einmalig aus den fertigen Seiten
gewonnen. Es wird nicht mehr gebraucht — außer die Zerlegung soll neu
aufgesetzt werden. `build/verify.py` vergleicht ein Erzeugnis gegen eine
Referenzfassung: Datenblöcke auf Gleichheit der Struktur, der Rest auf jedes
Byte. Damit wurde belegt, dass der Bauweg die handgepflegten Seiten
originalgetreu reproduziert.
