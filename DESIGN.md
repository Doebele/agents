---
name: AGENT // SYSTEM
description: Nächtliches Feldbuch zur KI-Agenten-Landschaft — Editorial-Typografie auf Beinahe-Schwarz, sieben Registerfarben, Leuchten nur als Zustand.
colors:
  void: "#06070B"
  surface: "#0A0C13"
  surface-raised: "#10131D"
  ink: "#F1F3F8"
  ink-dim: "#B6BCCE"
  muted: "#9aa1b4"
  hairline: "rgba(255,255,255,.08)"
  hairline-strong: "rgba(255,255,255,.14)"
  signal-cyan: "#34E7E4"
  ember: "#FF7A33"
  lime: "#B6FF3D"
  violet: "#9B7BF7"
  pink: "#FF4D8D"
  sky: "#4DA8FF"
  amber: "#FFC24D"
typography:
  display:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "clamp(54px, 12vw, 168px)"
    fontWeight: 300
    lineHeight: 0.92
    letterSpacing: "-0.02em"
  display-strong:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "clamp(54px, 12vw, 168px)"
    fontWeight: 900
    lineHeight: 0.92
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "clamp(34px, 5.4vw, 68px)"
    fontWeight: 600
    lineHeight: 1.02
    letterSpacing: "-0.02em"
  statement:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "clamp(26px, 3.4vw, 44px)"
    fontWeight: 500
    lineHeight: 1.18
    letterSpacing: "-0.01em"
  lead:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "clamp(16px, 1.6vw, 20px)"
    fontWeight: 300
    lineHeight: 1.6
    letterSpacing: "normal"
  quote:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "clamp(30px, 5vw, 60px)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.02em"
  title-lg:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "38px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.02em"
  numeral:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "42px"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "23px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  body-small:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 300
    lineHeight: 1.6
    letterSpacing: "normal"
  caption:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  body:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "clamp(15px, 1.5vw, 18px)"
    fontWeight: 300
    lineHeight: 1.6
    letterSpacing: "normal"
  label-lg:
    fontFamily: "Fira Code, ui-monospace, monospace"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "0.1em"
  label:
    fontFamily: "Fira Code, ui-monospace, monospace"
    fontSize: "11px"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "0.16em"
rounded:
  xs: "6px"
  sm: "8px"
  pop: "10px"
  md: "12px"
  card: "14px"
  lg: "16px"
  xl: "20px"
  full: "50%"
spacing:
  xs: "8px"
  sm: "12px"
  md: "18px"
  lg: "26px"
  xl: "46px"
components:
  chip:
    backgroundColor: "rgba(255,255,255,.02)"
    textColor: "{colors.ink-dim}"
    rounded: "{rounded.sm}"
    padding: "7px 12px"
    typography: "{typography.body}"
  chip-hover:
    textColor: "{colors.ink}"
  module-card:
    backgroundColor: "{colors.void}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "26px 24px 24px"
    height: "230px"
  glossary-term:
    backgroundColor: "transparent"
    textColor: "inherit"
    padding: "0"
  glossary-term-open:
    textColor: "{colors.signal-cyan}"
  glossary-popover:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.ink-dim}"
    rounded: "{rounded.pop}"
    padding: "12px 14px"
    width: "min(320px, 78vw)"
  nav-dot:
    backgroundColor: "transparent"
    rounded: "{rounded.full}"
    padding: "0"
    size: "10px"
  rule-card:
    backgroundColor: "transparent"
    textColor: "{colors.ink-dim}"
    rounded: "{rounded.card}"
    padding: "24px"
    height: "210px"
  drawer:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    padding: "26px 32px 50px"
    width: "min(620px, 100%)"
---

# Design System: AGENT // SYSTEM

## Overview

**Creative North Star: „Das nächtliche Feldbuch"**

Ein Nachschlagewerk, das nachts gelesen wird. Die Seite ist kein Dashboard und kein
Messgerät — sie ist eine Publikation: große, eng gesetzte Display-Typografie trägt die
Argumentation, Mono-Marginalien führen am Rand Buch, und ein 77 Einträge starker
Katalog liegt darunter. Das Beinahe-Schwarz ist kein Stilzitat, sondern die Lesesituation:
jemand sitzt abends davor und will etwas nachschlagen.

Die sieben Neonfarben sind **Registerfarben**, keine Dekoration. Jede gehört genau einem
Baustein und begleitet ihn durch die ganze Publikation — vom 3D-Kern im Hero über die
Modulkarte und den Drawer bis zum Chip-Hover. Wer die Farbe kennt, weiß, wo er ist. Das
ist die einzige Navigationshilfe, die ohne Beschriftung funktioniert, und deshalb darf sie
nirgends verrutschen.

Der Ton ist sachlich und direkt, nie feierlich. Hierarchie entsteht aus Schriftgröße,
Gewicht und Weißraum; Haarlinien trennen, wo Weißraum nicht reicht. Flächen sind ruhig
und beinahe unbegrenzt — Karten sind Rahmen, keine Kästen.

**Key Characteristics:**
- Beinahe-Schwarz (`#06070B`) als Papier, nicht als Effekt
- Sieben Registerfarben, 1:1 an die sieben Bausteine gebunden
- Ein Schriftpaar: Fira Sans für Argument, Fira Code für Beleg
- Betonung ist Schriftstärke (300 bis 900), nie Farbe und nie kursiv
- Haarlinien statt Rahmen, Weißraum statt Trennern
- Leuchten ausschließlich als Zustand, nie im Ruhezustand
- Atmosphärenebenen (Korn, Scanline, Vignette) bleiben unter 5 % Deckkraft

## Colors

Eine tiefe, fast blaustichige Schwarzskala, auf der sieben gesättigte Neontöne als Register
sitzen. Es gibt keine Grautreppe für Flächen — Tiefe entsteht über drei eng beieinander
liegende Hintergrundwerte und Haarlinien mit Alpha.

### Primary
- **Signalcyan** (`#34E7E4`): Die Systemfarbe der Oberfläche. Fortschrittsbalken,
  Fokusring, aktiver Kreislaufknoten, geöffneter Glossarbegriff, Mono-Kicker und
  Indexziffern. Baustein 01 (Sprachmodell) trägt dieselbe Farbe, und das ist beabsichtigt:
  das Modell ist der Kern des Systems, also führt es dessen Farbe. Was Cyan **nicht** tut:
  ein Wort im Fließtext betonen — das ist Sache der Schriftstärke.

### Secondary
- **Ember** (`#FF7A33`): Baustein 02 (Harness), Warnhinweise, der Rücklaufpfad im
  Kreislaufdiagramm, der aktive Cursor-Zustand. Wo Cyan „hier bist du" sagt, sagt Ember
  „hier passiert etwas". Auch Ember betont keinen Text.

### Tertiary
Die fünf verbleibenden Registerfarben. Sie treten nur im Kontext ihres Bausteins auf und
haben keine Rolle in der Oberfläche.

- **Lime** (`#B6FF3D`): Baustein 03, Skills.
- **Violett** (`#9B7BF7`): Baustein 04, MCP.
- **Pink** (`#FF4D8D`): Baustein 05, Tools.
- **Sky** (`#4DA8FF`): Baustein 06, Medien-Modelle. Zusätzlich das Partikelfeld im Hero.
- **Amber** (`#FFC24D`): Baustein 07, Arbeitsumgebung.

### Neutral
- **Void** (`#06070B`): Der Seitengrund. Jede Fläche liegt darauf.
- **Surface** (`#0A0C13`): Drawer, Knotenfüllung, Navigationsgrund beim Scrollen.
- **Surface Raised** (`#10131D`): Alles, was über der Seite schwebt — Glossar-Popover,
  Suchdialog.
- **Ink** (`#F1F3F8`): Fließtext-Höchstwert, Überschriften, Auszeichnung.
- **Ink Dim** (`#B6BCCE`): Der eigentliche Lesegrauwert für Absätze.
- **Muted** (`#9aa1b4`): Labels, Bildunterschriften, inaktive Zustände.
- **Haarlinie** (`rgba(255,255,255,.08)`) und **Haarlinie stark** (`rgba(255,255,255,.14)`):
  Trennung und Kartenkontur. Nie eine Volltonlinie.

### Named Rules

**Die Registerregel.** Eine Registerfarbe gehört genau einem Baustein und wechselt nie.
Sie wird nicht für Zustände, Diagrammserien oder Kategorien recycelt. Prüfung: eine Farbe
aus dem Screenshot isolieren — sie muss eindeutig auf genau einen der sieben Bausteine
zeigen.

**Die Zwei-Stimmen-Regel.** Auf einer Bildschirmhöhe stehen höchstens zwei Registerfarben
gleichzeitig, außer in den beiden Übersichten, die absichtlich alle sieben zeigen (3D-Kern
im Hero, Modulraster). Sonst wird das Register zum Konfetti.

**Die Alpha-Linien-Regel.** Konturen sind immer weißes Alpha auf dem Grund, nie ein
eigener Grauwert. Dadurch bleibt jede Kante unabhängig davon stimmig, welcher der drei
Hintergrundwerte darunterliegt.

## Typography

**Display Font:** Fira Sans (Fallback: `system-ui`, `sans-serif`)
**Body Font:** Fira Sans
**Label/Mono Font:** Fira Code (Fallback: `ui-monospace`, `monospace`)

**Character:** Ein einziges Schriftpaar aus derselben Familie. Fira Sans führt das
Argument — humanistisch, in großen Graden eng gesetzt, dadurch redaktionell statt
technisch. Fira Code führt Buch: Kicker, Ziffern, Labels, Messwerte. Die Trennung ist
inhaltlich, nicht dekorativ.

### Hierarchy
- **Display** (300 / 900, `clamp(54px, 12vw, 168px)`, LH 0.92): nur die Hero-Zeile. Zwei
  Zeilen, zwei Extreme derselben Schrift — Zeile 1 im Light-Schnitt (300, LS -0.02em),
  Zeile 2 im Black-Schnitt (900, LS -0.03em). Beide in `ink`; der Kontrast ist die
  Schriftstärke, nicht die Farbe.
- **Headline** (600, `clamp(34px, 5.4vw, 68px)`, LH 1.02, LS -0.02em): Sektionsüberschriften.
  Das hervorgehobene `<em>` darin springt auf 900, gleiche Farbe.
- **Title** (600, 23–38px, LS -0.01em bis -0.02em): Kartenüberschriften (23px),
  Drawer-Titel (38px).
- **Body** (300, `clamp(15px, 1.5vw, 18px)`, LH 1.6): Fließtext in `--ink-dim`.
  Zeilenlänge über den Container begrenzt, nicht über `max-width` am Absatz.
- **Label** (Fira Code, 400, 10–12px, LS 0.16em, Versalien): Kicker, Gruppentitel,
  Bausteinziffern, Tabellenköpfe, Popover-Überschrift.

**Bekannter Wildwuchs (Stand dieser Aufnahme).** Neben den obigen Rollen stehen im Code
noch vereinzelte Einmalgrößen: 9px, 10px, 17px, 22px und 24px. Sie gehören zu
keiner Rolle und sind nicht als Skala gemeint — sie sind der Rest, der beim Bauen
entstanden ist. Wer eine neue Fläche baut, greift zu den dokumentierten Rollen; wer
aufräumt, führt diese sechs Werte auf die nächstliegende Rolle zurück. Dasselbe gilt für
die Radien 3px, 4px, 9px, 18px und 999px.

### Named Rules

**Die Beleg-Regel.** Mono ist für Belege reserviert: Ziffern, Kennungen, Labels, Messwerte,
Code. Nie für Fließtext und nie, um etwas „technisch" aussehen zu lassen.

**Die Enge-Regel.** Je größer der Grad, desto enger die Laufweite (-0.03em im Display,
normal im Fließtext). Unter 34px wird nie negativ gesperrt. Der Light-Schnitt bekommt eine
Stufe weniger Enge als der Black-Schnitt (-0.02em gegen -0.03em), weil dünne Formen mehr
Luft brauchen.

**Die Schnitt-statt-Farbe-Regel.** Betonung im Text ist eine Schriftstärke, nie eine Farbe
und nie kursiv. Im Display- und Headline-Grad springt das betonte Wort auf **900**, im
Fließtext auf **700**; die Farbe bleibt unverändert. Farbe ist im System für Identität
reserviert (siehe Registerregel) — würde sie zusätzlich betonen, hieße dasselbe Signal
zweierlei. Kursive Schnitte kommen nicht vor und werden auch nicht geladen. Prüfung: ein
farbiges Wort im Fließtext ist immer ein Fehler.

**Die Kickerlos-Regel.** Über einer Überschrift steht kein Eyebrow. Die Mono-Labels der
Seite stehen neben, unter oder in Karten — nie als Vorspann über einer Headline.

## Layout

Ein zentrierter Container von 1240px mit 28px Innenabstand trägt die ganze Seite. Innerhalb
davon arbeitet ein 12-Spalten-Raster mit 18px Rinne; Modulkarten belegen 4 Spalten, die
siebte zentriert sich als `5 / span 4`. Der Rhythmus ist großzügig: Sektionen atmen über
Weißraum, nicht über Trennlinien, und über einer Überschrift steht mehr Raum als darunter.

Breakpoints: 1000px (Regelraster auf zwei Spalten), 900px (These einspaltig), 860px
(Modulkarten volle Breite, Hardwarespalten untereinander), 760px (Navigationsmeta und
Bausteinpunkte aus), 680px (Vergleichslisten und Glossar einspaltig), 560px (Regeln und
Providerkarten einspaltig).

Unter 760px verliert die Navigation bewusst Elemente statt sie zu schrumpfen: Marke, Suche
und Sprachschalter behalten ihre volle Größe, alles andere entfällt.

## Elevation & Depth

Das System ist im Ruhezustand **flach**. Tiefe entsteht aus drei Dingen, in dieser
Reihenfolge: den drei eng gestaffelten Hintergrundwerten, den Alpha-Haarlinien und dem
Weißraum. Es gibt keine Ruhe-Schatten auf Karten, Chips oder Knoten.

Zwei Ausnahmen, beide begründet:

**Leuchten ist Zustand.** Ein farbiger Halo ohne Versatz zeigt ausschließlich Aktivität —
Hover, Auswahl, laufendes Signal. Nichts leuchtet, weil es hübsch ist. Der Puls im
Kreislaufdiagramm leuchtet, weil er die laufende Schleife *ist*; ein Bausteinknoten
leuchtet erst unter dem Zeiger.

**Schatten sind Ebene.** Was tatsächlich über der Seite schwebt (Glossar-Popover, Drawer,
Suchdialog), nutzt einen neutralen, versetzten, weichen Schatten — nie einen farbigen.

### Shadow Vocabulary
- **Schwebende Ebene** (`box-shadow: 0 12px 28px rgba(0,0,0,.55)`): Popover und
  überlagernde Flächen. Versatz nach unten, kräftige Weichzeichnung, ohne Farbe.
- **Zustandshalo** (`box-shadow: 0 0 34px color-mix(in srgb, var(--mc) 55%, transparent)`):
  ausschließlich auf `:hover` eines Registerobjekts, in dessen eigener Registerfarbe.
- **Signalspur** (`filter: drop-shadow(0 0 6px var(--cyan))`): nur der animierte Puls im
  Kreislaufdiagramm.

### Named Rules

**Die Ruhe-ist-flach-Regel.** Kein Element trägt im Ruhezustand einen Schatten oder Halo.
Prüfung: Screenshot ohne Mauszeiger — es darf nichts leuchten außer dem laufenden Puls und
der 3D-Szene.

**Die Farbe-schwebt-nicht-Regel.** Schwebende Ebenen bekommen neutrale Schatten. Ein
farbiger Schatten sagt „Zustand", nie „Ebene". Ein mechanischer Slop-Detektor wird den
Hover-Halo als `dark-glow` melden — das ist eine bewusste, hier dokumentierte Entscheidung
und kein Befund.

## Shapes

Zwei Formfamilien, klar getrennt. **Flächen sind weich gerundet:** Chips 8px, Popover 10px,
Modul- und Regelkarten 14–16px, große Vergleichsflächen 18–20px — die Rundung wächst mit
der Fläche. **Systemobjekte sind Kreise:** Kreislaufknoten, Bausteinknoten,
Navigationspunkte, Cursor, 3D-Knoten. Was zum Agentenmodell gehört, ist rund; was Inhalt
trägt, ist ein gerundetes Rechteck.

Konturen sind durchgehend 1px Alpha-Weiß. Die einzige stärkere Linie ist die 2px-Kontur der
Bausteinknoten, weil sie dort die Registerfarbe trägt und die Fläche nur zu 12 % füllt.

Der Glossarbegriff ist die einzige gestrichelte Linie im System: 1px gestrichelt unter dem
Wort, in `hairline-strong`, beim Öffnen in Cyan. Gestrichelt heißt hier „hier steckt eine
Erklärung" — und weil es die einzige Strichelung ist, ist sie eindeutig.

### Named Rules

**Die Rund-ist-System-Regel.** Kreisformen sind für Bestandteile des Agentenmodells und für
Steuerpunkte reserviert. Inhalt bekommt nie einen Kreis.

## Components

### Chips (Steckbrief-Auslöser)
- **Style:** Fast unsichtbarer Aufheller (`rgba(255,255,255,.02)`), 1px Haarlinie-stark,
  8px Radius, 7×12px Innenabstand, Text in `ink-dim` mit dem Produktnamen in `ink`.
- **State:** Beim Hover wandert die Kontur auf die Registerfarbe des Bausteins und der Text
  auf `ink`. Chips ohne hinterlegten Steckbrief tragen `.static` und reagieren nicht — der
  Unterschied ist bewusst nur an der ausbleibenden Hover-Reaktion erkennbar.

### Cards / Containers
- **Corner Style:** 16px (Modul), 14px (Regel), 18–20px (Vergleich).
- **Background:** Ein sehr flacher Weiß-Verlauf von 2,5 % nach 0 % über dem Seitengrund —
  kein eigener Flächenwert.
- **Shadow Strategy:** keine. Siehe Elevation & Depth.
- **Border:** 1px Haarlinie. Im Hover blendet stattdessen eine 1px-Maskenkontur in der
  Registerfarbe ein, und die Karte hebt sich 4px.
- **Internal Padding:** 24–26px.

### Inputs / Fields
- **Style:** Der Suchdialog ist das einzige Eingabefeld. Randlos auf `surface-raised`,
  Lupe links, ESC-Schaltfläche rechts.
- **Focus:** Der globale Fokusring (2px Cyan, 3px Versatz) gilt überall und wird nirgends
  abgeschaltet.
- **Empty:** Ohne Treffer nennt der Leerzustand einen konkreten nächsten Versuch, nicht nur
  „nichts gefunden".

### Navigation
- **Style:** Fixiert, mit Weichzeichnung hinterlegt, Kontur erscheint erst beim Scrollen.
  Marke in Mono-Versalien, sieben Bausteinpunkte à 10px mit auf 24px erweiterter
  Trefferfläche, Sprachschalter mit vollständigem Namen für Screenreader.
- **Mobile:** Unter 760px entfallen Meta und Bausteinpunkte vollständig.

### Glossary Term (Signaturkomponente)
Der Begriff im Fließtext ist die charakteristischste Komponente des Systems: ein Wort, das
seine eigene Definition trägt.

- **Ruhe:** Wortlaut unverändert, 1px gestrichelte Linie in `hairline-strong` darunter.
- **Hover / offen:** Wort und Linie in Signalcyan.
- **Erklärung:** Ein einziges Popover an `<body>` — nicht am Wort — damit weder
  `overflow:hidden` einer Karte noch ein transformierter Vorfahr es beschneiden kann. Es
  klemmt sich in beide Viewport-Kanten und kippt am unteren Rand nach oben.
- **Screenreader:** Die Definition steht dauerhaft unsichtbar am Begriff und ist über
  `aria-describedby` verbunden. Wer vorliest, bekommt sie ohne Aufklappen.
- **Herkunft:** Die Begriffe werden zur Laufzeit aus dem Glossar abgeleitet, nicht
  händisch ausgezeichnet. Ein neuer Glossareintrag verlinkt sich dadurch selbst.

## Do's and Don'ts

### Do:
- **Do** jede Registerfarbe genau bei ihrem Baustein halten (`01` Cyan, `02` Ember,
  `03` Lime, `04` Violett, `05` Pink, `06` Sky, `07` Amber).
- **Do** Konturen als weißes Alpha setzen (`rgba(255,255,255,.08)` und `.14`), damit sie auf
  allen drei Hintergrundwerten stimmen.
- **Do** Mono für Ziffern, Labels und Belege einsetzen — und nur dafür.
- **Do** betonen, indem du die Schriftstärke erhöhst: 900 im Display- und Headline-Grad,
  700 im Fließtext.
- **Do** neue schwebende Ebenen an `<body>` hängen und mit dem neutralen Versatzschatten
  versehen.
- **Do** Atmosphärenebenen unter 5 % Deckkraft halten (Korn 5 %, Scanline 1,2 %).
- **Do** Trefferflächen auf mindestens 24px bringen, auch wenn die Optik 10px bleibt.

### Don't:
- **Don't** im Ruhezustand leuchten lassen. Halos sind Hover, Auswahl oder laufendes Signal.
- **Don't** farbige Schatten für Ebenen benutzen. Farbe heißt Zustand.
- **Don't** ein Wort im Fließtext einfärben, um es zu betonen. Dafür ist die Schriftstärke da.
- **Don't** kursive Schnitte einsetzen; sie sind nicht Teil des Systems und werden nicht geladen.
- **Don't** einen Kicker über eine Überschrift setzen.
- **Don't** eine achte Akzentfarbe einführen. Reicht das Register nicht, ist die
  Informationsarchitektur falsch, nicht die Palette.
- **Don't** Kreisformen für Inhalt verwenden; sie gehören dem Agentenmodell.
- **Don't** eine zweite gestrichelte Linie einführen — die Strichelung ist als eindeutiges
  Zeichen für „Erklärung dahinter" vergeben.
- **Don't** eine Displayschrift des Systems (Impact, Arial Black, Platform-Sans) einsetzen;
  das Paar ist Fira Sans und Fira Code, mit `system-ui` nur als Notfall-Fallback.
