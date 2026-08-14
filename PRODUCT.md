# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Primär: komplette Einsteiger:innen ohne Entwicklungshintergrund.** Sie haben von
KI-Agenten gehört, wissen aber nicht, woraus so ein System besteht, welche Werkzeuge
es gibt und womit man anfängt. Sie kommen ohne Vorwissen über Modelle, Harnesses oder
MCP und brauchen die Einordnung *vor* dem Katalog.

**Sekundär: der Autor selbst als Nachschlagewerk.** Wiederfinden, was ein bestimmtes
Werkzeug macht, wer es baut und wo dessen Doku liegt — Vollständigkeit zählt hier mehr
als Didaktik.

**Bekannter Konflikt (unaufgelöst, nicht erfunden):** Die Website adressiert im Hero
aktuell „Für Entwickler:innen", und die Hosting-/Hardware-Sektion ist im Expert:innen-
Register geschrieben (VRAM, Quantisierung, ROCm). Das steht im Widerspruch zur
bestätigten primären Zielgruppe. Künftige Arbeit an Copy und Informationsdichte muss
diesen Konflikt auflösen, nicht fortschreiben.

## Product Purpose

Ein **eigenständiges Nachschlagewerk** zur KI-Agenten-Landschaft, unabhängig vom Vortrag
benutzbar. Erfolg heißt: jemand findet ein Werkzeug wieder, versteht wozu es dient, und
klickt von dort zur offiziellen Dokumentation durch.

Die Präsentation (`KI-Agenten-Landschaft.pptx`) ist ein **separates Deliverable** aus
derselben Quelle, kein Vorgänger und keine Abhängigkeit der Website. Beide erklären
dieselben sieben Bausteine, aber die Website ist nicht Begleitmaterial — sie steht für
sich.

## Positioning

Jeder genannte Name ist anklickbar und führt zu einem geprüften Steckbrief mit
Anbieter, Kurzbeschreibung, offiziellen Links und einem Praxis-Tipp — nicht zu einer
Suchmaschine und nicht ins Leere. Das unterscheidet die Seite von einem Blogartikel
(erklärt, verlinkt aber nicht vollständig) und von einer Linkliste (verlinkt, erklärt
aber nicht). Dazu: eine einzelne Datei, die man weitergeben und offline öffnen kann.

## Operating Context

- Wird per Doppelklick auf die HTML-Datei geöffnet oder lokal ausgeliefert; kein Server,
  kein Build-Schritt, keine Installation.
- Nutzung ist stöbernd und nachschlagend, nicht linear: Einstieg über Modul-Deep-Dive,
  über die Suche (Cmd+K) oder über den 3D-Einstieg.
- Sprachwahl passiert über den Schalter in der Navigation; beide Fassungen sind separate
  vollständige Dateien.
- Recherchierte Quellen im Elternordner (`ki-landschaft-praesentation/`,
  `kimi-work-anweisung-praesentation.md`, `ki-landschaft-uebersicht.excalidraw`) wurden
  ausschließlich gelesen und bleiben unverändert.

## Capabilities and Constraints

**Bestätigte, dauerhafte Constraints:**

- **Single-File, offline öffnbar.** Eine Datei pro Sprache, per Doppelklick lauffähig.
  Schließt Bundler, Build-Schritt und das Auslagern in geteilte `app.js`/`app.css` aus.
- **Zweisprachig DE + EN, gleichwertig gepflegt.** `site/index.html` (EN) und
  `site/index.de.html` (DE).
- **Stand August 2026 wird gepflegt.** Das Datum ist ein Versprechen, kein Zeitstempel:
  Steckbriefe, Preise und Modellversionen sollen aktuell gehalten werden.
- **Erweiterbar und aktualisierbar.** Neue Werkzeuge, Modelle und Anbieter kommen dazu;
  die Struktur muss das ohne Umbau tragen.
- **Keine erfundenen Fakten oder Links.** Fehlende Links bleiben weg statt geraten; keine
  erfundenen Benchmarks, Preise, Zitate oder Kund:innen.

**Spannung, die künftige Arbeit tragen muss:** „Single-File" und „erweiterbar/aktuell
halten" ziehen gegeneinander. Aktuell existiert jede Zeile CSS und JavaScript doppelt
(DE und EN, je ~2.000 identische Zeilen), und die Fassungen sind bereits auseinander-
gelaufen. Jede Pflegemaßnahme muss zweimal ausgeführt oder anders gelöst werden, ohne
die Einzeldatei-Auslieferung aufzugeben.

**Bestand:** sieben Bausteine, ein Agenten-Kreislauf, 77 Steckbriefe (alle über Chips
oder Suche erreichbar), Open-vs-Closed-Vergleich, elf Hosting-Anbieter, Hardware-Tiers
nach Betriebssystem, fünf Regeln, Glossar mit 14 Begriffen.

**Terminologie (etabliert, DE):** Baustein, Steckbrief, Harness, Denken/Handeln/
Beobachten, Open-Weight, Frontier.

## Brand Commitments

- Name der Website: **AGENT // SYSTEM**. Titel der Präsentation: **Die KI-Agenten-
  Landschaft**.
- Das Dieter-Rams-Zitat „Weniger, aber besser." ist in beiden Deliverables als Schluss
  gesetzt; die Präsentation ist explizit im Rams-Designsystem gebaut.
- Die Website hat bewusst eine **eigene, gegensätzliche visuelle Welt** (dark, „terminal
  meets editorial", Neon-Akzente, sieben Baustein-Farben) — sie ist keine Web-Fassung
  der hellen Rams-Folien. Das ist eine gesetzte Entscheidung, kein Versehen.
- Ansprache im Deutschen: Du-Form, gegendert (`Entwickler:innen`).

## Evidence on Hand

**Vorhanden:**
- 77 Steckbriefe mit recherchierten, geprüften Links (77× Website, 60× Doku, 47× Code);
  fehlende Links sind bewusst `null`.
- `media/` — sieben Objektbilder, ausschließlich in der PPTX verwendet; die Website
  nutzt keine Bilder.
- `KI-Agenten-Landschaft.pptx` samt Renderer (`build_pptx.py`) und Prüfskript
  (`verify_pptx.py`).
- Zwei frühere Impeccable-Critiques unter `.impeccable/critique/` (zuletzt 29/40).

**Ausdrücklich nicht vorhanden — darf nicht erfunden werden:**
- Keine Nutzerforschung, keine Analytics, keine Testimonials, keine Fallstudien.
- Die Personas „Jordan", „Casey" und „Sam" in der bestehenden Critique sind Hypothesen
  eines Review-Durchgangs, **keine echten Nutzer:innen** und keine bestätigte Evidenz.
- Kein Deploy-Ziel, keine Domain, keine Lizenzentscheidung festgelegt.

## Product Principles

1. **Einordnung vor Katalog.** Die primäre Leserin hat kein Vorwissen; der Katalog ist
   die Belohnung fürs Verstehen, nicht der Einstieg.
2. **Kein erfundener Fakt.** Lieber ein leeres Feld als ein geratener Link. Das ist die
   Grundlage dafür, dass die Seite als Nachschlagewerk taugt.
3. **Eine Datei, die man weitergeben kann.** Portabilität schlägt Architektur-Eleganz.
4. **Beide Sprachen sind erste Klasse.** Was in einer Fassung stimmt, stimmt in beiden.
5. **Der Stand ist ein Versprechen.** Struktur und Pflegeaufwand müssen Aktualisierung
   tragen, nicht nur den einmaligen Wurf.
