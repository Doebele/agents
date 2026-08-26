#!/usr/bin/env python3
"""Baut site/index.html (EN) und site/index.de.html (DE) aus build/template.html und
content/*.json. Ab jetzt der einzige Weg, die Seiten zu aendern: Inhalte
gehoeren in content/, Geruest in die Vorlage.

Vor dem Schreiben laeuft die Pruefung. Sie faengt genau die Fehler ab, die
beim Bearbeiten von Hand entstehen: eine fehlende Uebersetzung, ein Chip ohne
Steckbrief, ein Steckbrief, den keine Kachel erreicht.

Aufruf:  python3 build/build.py [--check]
         --check baut nur und vergleicht mit dem, was in site/ liegt.
"""
import json
import re, datetime, pathlib, sys, difflib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE, CONTENT = ROOT/"site", ROOT/"content"
VORLAGE = (ROOT/"build"/"template.html").read_text(encoding="utf-8")
# Englisch ist die Standardfassung — wer die Adresse ohne Dateinamen
# aufruft, landet dort. Deutsch haengt am DE-Schalter.
SPRACHEN = {"en": "index.html", "de": "index.de.html"}
BLOECKE = ["MODULES", "RULES", "OC", "STECKBRIEF", "HARDWARE", "PROVIDERS", "LOOP", "GLOSSARY"]

daten = {b: json.loads((CONTENT/f"{b.lower()}.json").read_text(encoding="utf-8")) for b in BLOECKE}
ui = json.loads((CONTENT/"ui.json").read_text(encoding="utf-8"))

# arbeitsarten.json ist Arbeitsdokument und Datenquelle zugleich: Begruendungen,
# Luecken und offene Entscheidungen stehen dort neben dem, was der Wizard zeigt.
# Statt einer zweiten Datei — die sofort auseinanderliefe — wird beim Bauen
# abgeleitet. Was hier nicht auftaucht, erreicht die Seite nicht.
def _arbeitsarten():
    q = json.loads((CONTENT/"arbeitsarten.json").read_text(encoding="utf-8"))
    def station(s):
        k = {f: s[f] for f in ("frage", "notiz", "kandidaten", "empfehlung", "luecke") if f in s}
        k.setdefault("kandidaten", []); k.setdefault("empfehlung", [])
        return k
    def variante(o):
        return {"id": o["id"], "name": o["name"], "sub": o["sub"],
                "stationen": {k: station(v) for k, v in o.get("stationen", {}).items()},
                "voraussetzungen": o.get("voraussetzungen", [])}
    def kunst(a):
        k = {"id": a["id"], "name": a["name"], "beispiele": a["beispiele"],
             "synonyme": a["synonyme"],
             "voraussetzungen": a.get("voraussetzungen", []),
             "stationen": {k: station(v) for k, v in a["stationen"].items()
                           if v.get("im_wizard") is not False}}
        if "varianten" in a:
            k["varianten"] = {"frage": a["varianten"]["frage"],
                              "optionen": [variante(o) for o in a["varianten"]["optionen"]]}
        return k
    return {
        "ui": q["ui"],
        "tutorial": q["tutorial"],
        "global": {k: station(v) for k, v in q["globale_wahl"]["stationen"].items()},
        "arten": [kunst(a) for a in q["arbeitsarten"]],
    }

BLOECKE.append("ARBEITSARTEN")
daten["ARBEITSARTEN"] = _arbeitsarten()

# Wann ein Steckbrief zuletzt inhaltlich anders aussah, steht nicht im JSON,
# sondern in der Historie — build/stand.py leitet es ab. Ohne Historie fehlt
# das Feld, und die Seite zeigt kein Datum, statt eins zu erfinden.
import stand as _stand  # noqa: E402

for _name, _tag in _stand.stand().items():
    if _name in daten["STECKBRIEF"]:
        daten["STECKBRIEF"][_name]["stand"] = _tag


def fuer(o, lang):
    """Zweisprachige Struktur auf eine Sprache eindampfen."""
    if isinstance(o, dict):
        if set(o) == {"de", "en"} and all(isinstance(v, str) for v in o.values()):
            return o[lang]
        return {k: fuer(v, lang) for k, v in o.items()}
    if isinstance(o, list):
        return [fuer(v, lang) for v in o]
    return o


def pruefe():
    fehler = []

    def wandere(o, pfad):
        if isinstance(o, dict):
            if set(o) == {"de", "en"}:
                for l in ("de", "en"):
                    if not isinstance(o[l], str) or not o[l].strip():
                        fehler.append(f"{pfad}: {l} fehlt oder ist leer")
                return
            for k, v in o.items(): wandere(v, f"{pfad}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o): wandere(v, f"{pfad}[{i}]")

    for b in BLOECKE: wandere(daten[b], b)
    for k, v in ui.items():
        for l in ("de", "en"):
            if l not in v: fehler.append(f"ui.{k}: {l} fehlt")

    # Jeder Chip braucht einen Steckbrief, jeder Steckbrief einen Chip.
    sb = set(daten["STECKBRIEF"])
    chips = set()
    for m in daten["MODULES"]:
        for g in m.get("groups", []):
            for it in g.get("items", []):
                # Baustein 05 fuehrt bislang nur Kategorien ohne Steckbrief.
                if not (isinstance(it, dict) and "k" in it): continue
                chips.add(fuer(it["k"], "de"))
    for k in sorted(chips - sb): fehler.append(f"Chip ohne Steckbrief: {k!r}")
    for k in sorted(sb - chips): fehler.append(f"Steckbrief ohne Chip: {k!r}")

    # billing: optional, aber wenn gesetzt, nur bekannte Abrechnungsarten.
    for k, d in daten["STECKBRIEF"].items():
        b = d.get("billing")
        if b is None: continue
        if not isinstance(b, list) or not b or any(x not in ("abo", "api") for x in b):
            fehler.append(f"Steckbrief {k!r}: billing muss Liste aus 'abo'/'api' sein")

    # plansChecked: optional, aber wenn gesetzt, ein echtes Datum in der
    # Vergangenheit. Ein Pruefdatum, das in der Zukunft liegt, ist keine
    # Schlamperei sondern eine Falschaussage: es behauptet eine Pruefung,
    # die nicht stattgefunden hat.
    heute = datetime.date.today().isoformat()
    for k, d in daten["STECKBRIEF"].items():
        s = d.get("plansChecked")
        if s is None: continue
        if not isinstance(s, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
            fehler.append(f"Steckbrief {k!r}: plansChecked muss JJJJ-MM-TT sein, nicht {s!r}")
        elif s > heute:
            fehler.append(f"Steckbrief {k!r}: plansChecked {s} liegt in der Zukunft")
        elif not d.get("plans"):
            fehler.append(f"Steckbrief {k!r}: plansChecked ohne plans")

    # contentChecked: dasselbe fuer den Text. Anders als plansChecked haengt es
    # an keinem zweiten Feld — geprueft werden kann jeder Eintrag.
    for k, d in daten["STECKBRIEF"].items():
        s_ = d.get("contentChecked")
        if s_ is None: continue
        if not isinstance(s_, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s_):
            fehler.append(f"Steckbrief {k!r}: contentChecked muss JJJJ-MM-TT sein, nicht {s_!r}")
        elif s_ > heute:
            fehler.append(f"Steckbrief {k!r}: contentChecked {s_} liegt in der Zukunft")

    # Marken der Vorlage muessen zu den vorhandenen Inhalten passen.
    for b in BLOECKE:
        if "{{DATA:"+b+"}}" not in VORLAGE: fehler.append(f"Vorlage: Marke fuer {b} fehlt")
    for k in ui:
        if "{{T:"+k+"}}" not in VORLAGE: fehler.append(f"Vorlage: Marke fuer ui.{k} fehlt")
    return fehler


def baue(lang):
    t = VORLAGE
    for b in BLOECKE:
        # </ maskieren, sonst beendet ein Text im JSON das <script> vorzeitig.
        j = json.dumps(fuer(daten[b], lang), ensure_ascii=False, indent=1).replace("</", "<\\/")
        t = t.replace("{{DATA:"+b+"}}", f"const {b} = {j};")
    for k, v in ui.items():
        t = t.replace("{{T:"+k+"}}", v[lang])
    # Zaehlmarken zuletzt: sie stehen auch in uebersetzten Zeilen und sollen
    # nie wieder von Hand nachgezogen werden muessen.
    for b in BLOECKE:
        t = t.replace("{{N:"+b+"}}", str(len(daten[b])))
    assert "{{" not in t, "unaufgeloeste Marke: " + t[t.index("{{"):t.index("{{")+40]
    return t


fehler = pruefe()
if fehler:
    print("Pruefung fehlgeschlagen:")
    for f in fehler[:20]: print("  ·", f)
    sys.exit(1)

pruefmodus = "--check" in sys.argv
abweichung = False
for lang, name in SPRACHEN.items():
    neu = baue(lang)
    ziel = SITE/name
    if pruefmodus:
        alt = ziel.read_text(encoding="utf-8")
        if alt == neu:
            print(f"  {name}: deckungsgleich")
        else:
            abweichung = True
            d = list(difflib.unified_diff(alt.split("\n"), neu.split("\n"),
                                          "alt", "neu", lineterm="", n=0))
            print(f"  {name}: {len([x for x in d if x[:1] in '+-' and x[:3] not in ('+++','---')])} abweichende Zeilen")
            for z in d[:12]: print("   ", z[:150])
    else:
        ziel.write_text(neu, encoding="utf-8")
        print(f"  {name}: geschrieben ({len(neu):,} Zeichen)")

# Der Pruefmodus muss scheitern, nicht nur reden: sonst laeuft die Auslieferung
# ueber einen veralteten Stand hinweg, obwohl sie ihn gemeldet hat.
if abweichung:
    print("\nsite/ weicht von content/ ab — erst bauen, dann ausliefern.")
    sys.exit(1)
