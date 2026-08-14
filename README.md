# AGENT // SYSTEM

Ein interaktiver Feldführer durch die KI-Agenten-Landschaft — für Einsteiger,
zweisprachig, Stand August 2026.

Zwei Ergebnisse aus einer Quelle:

| | |
|---|---|
| **Website** | `site/index.html` (DE) · `site/index.en.html` (EN) — je eine einzige Datei, per Doppelklick zu öffnen |
| **Präsentation** | `KI-Agenten-Landschaft.pptx` — 22 Folien, 16:9 |

## Was drinsteht

Sieben Bausteine, aus denen jeder KI-Agent besteht, mit **109 Steckbriefen**
zu den Modellen, Werkzeugen und Diensten dahinter. Dazu ein Wizard, der aus
der eigenen Arbeitsart ein Setup zusammenstellt — samt der Voraussetzungen,
die dasein müssen, und einem Markdown-Blatt, das man dem eigenen Agenten
zum Einrichten gibt.

## Bauen

Die beiden HTML-Dateien sind **Erzeugnisse**. Wer sie direkt bearbeitet,
verliert die Änderung beim nächsten Bauen.

```bash
python3 build/build.py            # baut beide Sprachdateien
python3 build/build.py --pruefen  # baut nur und meldet Abweichungen
```

Ohne Abhängigkeiten ausser Python 3. Node wird nur für `build/extract.py`
gebraucht, und das lief einmalig.

## Aufbau

```
content/     die Inhalte — Steckbriefe, Bausteine, Glossar, Arbeitsarten
build/       Vorlage und Bauskript
site/        die gebauten Seiten
media/       Bilder für die Präsentation
DESIGN.md    das Designsystem, mit benannten Regeln
PRODUCT.md   Zweck, Zielgruppe, Grundsätze
```

## Zweisprachigkeit

Übersetzte Werte stehen in `content/` **nebeneinander** als
`{"de": …, "en": …}`. Was in beiden Sprachen gleich ist — Namen, Links,
Farben —, steht nur einmal da. Eine fehlende Übersetzung fällt dadurch im
Nachbarschlüssel auf und wird zusätzlich von der Prüfung abgefangen.

## Was die Prüfung abfängt

Sie läuft vor jedem Schreiben und bricht ab, bevor etwas kaputtgeht:

- eine fehlende oder leere Übersetzung
- ein Chip, hinter dem kein Steckbrief liegt
- ein Steckbrief, den keine Kachel erreicht
- eine Marke in der Vorlage ohne Inhalt und umgekehrt

## Grundsätze

Keine erfundenen Angaben. Fehlt ein Link, wird er weggelassen statt geraten —
deshalb tragen Begriffe und Fähigkeiten keine Herstellerverweise. Was als
Vorschlag markiert ist, ist eine Meinung und kein Befund, und die Oberfläche
sagt das auch.

„Stand August 2026" ist ein Pflegeversprechen, kein Zeitstempel.

## Präsentation bauen

```bash
python3 build_pptx.py      # erzeugt die PPTX aus media/
python3 verify_pptx.py     # prüft sie gegen die Akzeptanzkriterien
```
