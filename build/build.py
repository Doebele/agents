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
ARBEITSARTEN_ROH = json.loads((CONTENT/"arbeitsarten.json").read_text(encoding="utf-8"))


def _arbeitsarten():
    q = ARBEITSARTEN_ROH
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


def pruefe_wizard(roh, steckbriefe):
    """Jede Kandidaten- und Empfehlungszeile des Wizards muss auf einen
    vorhandenen Steckbrief zeigen — arbeitsarten.json sagt das selbst
    ("Alle Einträge zeigen auf vorhandene Steckbriefe"), nur hat es bisher
    niemand nachgehalten. Ein Tippfehler oder ein umbenannter Steckbrief
    hinterlaesst sonst eine Option, die der Wizard anbietet und die ins Leere
    fuehrt. Leere Kandidatenlisten sind erlaubt: das sind die erklaerten
    Luecken."""
    fehler = []

    def station(s, wo):
        kand = s.get("kandidaten", [])
        for k in kand:
            if k not in steckbriefe:
                fehler.append(f"Wizard {wo}: Kandidat ohne Steckbrief: {k!r}")
        # Eine Empfehlung ausserhalb der Kandidaten kann der Nutzer nicht
        # waehlen — sie ist keine Vorauswahl, sondern ein Fehler.
        for k in s.get("empfehlung", []):
            if k not in kand:
                fehler.append(f"Wizard {wo}: Empfehlung {k!r} steht nicht in kandidaten")

    for n, s in roh.get("globale_wahl", {}).get("stationen", {}).items():
        station(s, f"globale_wahl/{n}")
    for a in roh.get("arbeitsarten", []):
        for n, s in a.get("stationen", {}).items():
            station(s, f"{a['id']}/{n}")
        for o in a.get("varianten", {}).get("optionen", []):
            for n, s in o.get("stationen", {}).items():
                station(s, f"{a['id']}/{o['id']}/{n}")
    return fehler


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

    fehler += pruefe_wizard(ARBEITSARTEN_ROH, sb)

    # billing: optional, aber wenn gesetzt, nur bekannte Abrechnungsarten.
    for k, d in daten["STECKBRIEF"].items():
        b = d.get("billing")
        if b is None: continue
        if not isinstance(b, list) or not b or any(x not in ("abo", "api") for x in b):
            fehler.append(f"Steckbrief {k!r}: billing muss Liste aus 'abo'/'api' sein")

    # plansJahr: der Preis bei Jahreszahlung, und nur wo der Anbieter ihn
    # selbst ausweist. Ohne plans hat er nichts, wogegen er stuende — der
    # Umschalter in der Schublade braucht beide Seiten. Und wer einen zweiten
    # Preis eintraegt, hat die Preisseite gelesen: ohne plansChecked waere das
    # eine Zahl ohne Datum, also eine, der niemand ansieht, wie alt sie ist.
    for k, d in daten["STECKBRIEF"].items():
        if not d.get("plansJahr"): continue
        if not d.get("plans"):
            fehler.append(f"Steckbrief {k!r}: plansJahr ohne plans")
        if not d.get("plansChecked"):
            fehler.append(f"Steckbrief {k!r}: plansJahr ohne plansChecked")

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


def stand_datum(lang):
    """Der Stand des Katalogs als Monatsname: aus dem letzten Commit, der
    content/ oder build/ beruehrt — derselbe Trick wie in stand.py. Ein
    handgepflegtes Datum rottet lautlos; git kann nicht vergessen. Ohne
    Historie (flacher Klon) zaehlt der Bautag, der in der CI ohnehin der
    Veröffentlichungstag ist."""
    import subprocess
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", "content", "build"],
                           capture_output=True, text=True, timeout=30)
        iso = r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    except (OSError, subprocess.SubprocessError):
        iso = None
    if not iso:
        iso = datetime.date.today().isoformat()
    jahr, monat, _ = iso.split("-")
    monate = {
        "de": ["januar", "februar", "märz", "april", "mai", "juni", "juli",
               "august", "september", "oktober", "november", "dezember"],
        "en": ["january", "february", "march", "april", "may", "june", "july",
               "august", "september", "october", "november", "december"],
    }
    return f"{monate[lang][int(monat)-1]} {jahr}"


def baue(lang):
    t = VORLAGE
    for b in BLOECKE:
        # </ maskieren, sonst beendet ein Text im JSON das <script> vorzeitig.
        j = json.dumps(fuer(daten[b], lang), ensure_ascii=False, indent=1).replace("</", "<\\/")
        t = t.replace("{{DATA:"+b+"}}", f"const {b} = {j};")
    for k, v in ui.items():
        t = t.replace("{{T:"+k+"}}", v[lang])
    # Der Stand im Boot-Bildschirm: aus git abgeleitet, nicht von Hand.
    t = t.replace("{{STAND}}", stand_datum(lang))
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

def selbsttest():
    """Die Wizard-Pruefung an gebauten Faellen, damit sie nicht stumm
    verfaellt: eine bestandene Pruefung auf sauberen Inhalten beweist nur,
    dass sie nichts meldet — nicht, dass sie etwas finden wuerde."""
    sb = {"Claude Code", "Aider"}
    gut = {"globale_wahl": {"stationen": {"01": {"kandidaten": ["Aider"],
                                                "empfehlung": ["Aider"]}}},
           "arbeitsarten": [{"id": "bauen",
                             "stationen": {"03": {"kandidaten": [], "empfehlung": []}},
                             "varianten": {"optionen": [
                                 {"id": "web", "stationen": {"04": {"kandidaten": ["Claude Code"]}}}]}}]}
    assert pruefe_wizard(gut, sb) == [], pruefe_wizard(gut, sb)

    tippfehler = json.loads(json.dumps(gut))
    tippfehler["arbeitsarten"][0]["varianten"]["optionen"][0]["stationen"]["04"]["kandidaten"] = ["Claude Kode"]
    f = pruefe_wizard(tippfehler, sb)
    assert len(f) == 1 and "bauen/web/04" in f[0] and "Claude Kode" in f[0], f

    daneben = json.loads(json.dumps(gut))
    daneben["globale_wahl"]["stationen"]["01"]["empfehlung"] = ["Claude Code"]
    f = pruefe_wizard(daneben, sb)
    assert len(f) == 1 and "steht nicht in kandidaten" in f[0], f

    # Eine Luecke ist kein Fehler.
    luecke = json.loads(json.dumps(gut))
    luecke["arbeitsarten"][0]["stationen"]["03"]["luecke"] = "kein Eintrag im Katalog"
    assert pruefe_wizard(luecke, sb) == []

    print("build.py: Wizard-Pruefung in Ordnung")


if "--selbsttest" in sys.argv:
    selbsttest()
    sys.exit(0)

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
