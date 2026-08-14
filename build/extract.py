#!/usr/bin/env python3
"""Einmaliger Ausbau: zerlegt die beiden fertigen Sprachdateien in eine
gemeinsame Vorlage plus Daten. Danach wird nur noch build.py benutzt.

Zwei Beobachtungen machen das sicher: Beide Dateien haben dieselbe Zeilenzahl
und sind Zeile fuer Zeile deckungsgleich aufgebaut — Uebersetzung ist immer
ein Austausch, nie eine Einfuegung. Und von den zwoelf Feldern eines
Steckbriefs sind nur vier uebersetzt; der Rest steht ohnehin nur einmal da.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE, BUILD, CONTENT = ROOT/"site", ROOT/"build", ROOT/"content"
CONTENT.mkdir(exist_ok=True)

# Reihenfolge egal, die Namen muessen nur den Konstanten im Dokument entsprechen.
BLOECKE = ["MODULES", "RULES", "OC", "STECKBRIEF", "HARDWARE", "PROVIDERS", "LOOP", "GLOSSARY"]


def spanne(t: str, name: str):
    """Findet 'const NAME = <literal>;' und gibt (start, ende, literaltext)."""
    for muster in (f"const {name} = ", f"const {name}="):
        i = t.find("\n" + muster)
        if i >= 0:
            i += 1
            break
    else:
        raise SystemExit(f"{name}: nicht gefunden")
    j = i + len(muster)
    tiefe, k, im_string, escape = 0, j, "", False
    while k < len(t):
        c = t[k]
        if im_string:
            if escape: escape = False
            elif c == "\\": escape = True
            elif c == im_string: im_string = ""
        elif c in "\"'`": im_string = c
        elif c in "[{": tiefe += 1
        elif c in "]}":
            tiefe -= 1
            if tiefe == 0:
                k += 1
                break
        k += 1
    assert t[k] == ";", f"{name}: erwartete ';' bei {k}, fand {t[k-20:k+5]!r}"
    return i, k + 1, t[j:k]


def als_daten(literal: str):
    """JS-Literal zu Python. Node parst, was Python nicht kann."""
    r = subprocess.run(["node", "-e",
                        "let d=eval('('+require('fs').readFileSync(0,'utf8')+')');"
                        "process.stdout.write(JSON.stringify(d))"],
                       input=literal, capture_output=True, text=True)
    if r.returncode: raise SystemExit(f"node: {r.stderr[:300]}")
    return json.loads(r.stdout)


def zusammenfuehren(d, e, pfad="") -> object:
    """Deutsch und Englisch zu einer Struktur: Gleiches einmal, Uebersetztes
    als {de, en}. So faellt eine fehlende Uebersetzung im Nachbarschluessel auf."""
    if isinstance(d, dict) and isinstance(e, dict):
        assert set(d) == set(e), f"{pfad}: Schluessel weichen ab {set(d)^set(e)}"
        return {k: zusammenfuehren(d[k], e[k], f"{pfad}.{k}") for k in d}
    if isinstance(d, list) and isinstance(e, list):
        assert len(d) == len(e), f"{pfad}: Laenge {len(d)} != {len(e)}"
        return [zusammenfuehren(a, b, f"{pfad}[{i}]") for i, (a, b) in enumerate(zip(d, e))]
    if d == e:
        return d
    assert isinstance(d, str) and isinstance(e, str), f"{pfad}: {d!r} / {e!r}"
    return {"de": d, "en": e}


def main():
    de = (SITE/"index.html").read_text(encoding="utf-8")
    en = (SITE/"index.en.html").read_text(encoding="utf-8")

    # 1) Datenbloecke herausloesen und durch eine Marke ersetzen
    for name in BLOECKE:
        a, b, lit_de = spanne(de, name)
        c, d, lit_en = spanne(en, name)
        daten = zusammenfuehren(als_daten(lit_de), als_daten(lit_en), name)
        (CONTENT/f"{name.lower()}.json").write_text(
            json.dumps(daten, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        de = de[:a] + "{{DATA:" + name + "}}" + de[b:]
        en = en[:c] + "{{DATA:" + name + "}}" + en[d:]
        print(f"  {name:11} → content/{name.lower()}.json")

    # 2) Zeilenweise vergleichen: Gleiches in die Vorlage, Verschiedenes in ui.json
    zd, ze = de.split("\n"), en.split("\n")
    assert len(zd) == len(ze), f"Zeilenzahl weicht ab: {len(zd)} / {len(ze)}"
    vorlage, ui = [], {}
    for zeile_de, zeile_en in zip(zd, ze):
        if zeile_de == zeile_en:
            vorlage.append(zeile_de)
        else:
            schluessel = f"t{len(ui)+1:03d}"
            ui[schluessel] = {"de": zeile_de, "en": zeile_en}
            vorlage.append("{{T:" + schluessel + "}}")

    (BUILD/"template.html").write_text("\n".join(vorlage), encoding="utf-8")
    (CONTENT/"ui.json").write_text(json.dumps(ui, ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")
    print(f"\n  build/template.html  ({len(vorlage)} Zeilen)")
    print(f"  content/ui.json      ({len(ui)} uebersetzte Zeilen)")


# verify.py leiht sich nur spanne() und als_daten() — der Ausbau darf dabei nicht laufen.
if __name__ == "__main__":
    main()
