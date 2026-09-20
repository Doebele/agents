#!/usr/bin/env python3
"""Wann ein Steckbrief zuletzt inhaltlich anders aussah — aus der Historie.

Kein Feld im JSON. Ein handgepflegtes Datum rottet wie alles Handgepflegte,
und zwar lautlos: niemandem faellt auf, dass es nicht mitgezogen wurde. Git
weiss es ohnehin, kann es nicht vergessen, und kein Agent kann es faelschen.

Verglichen wird der geparste Eintrag, nicht sein Text. Eine Umformatierung der
Datei verschiebt deshalb kein einziges Datum, eine echte Aenderung an genau
einem Steckbrief nur dessen eigenes.

Und verglichen werden nur die Felder, die ein Leser sieht: name, vendor, cat,
blurb, tip, links. Preise, Abrechnung und die beiden Pruefdaten bleiben
aussen vor. Sie haben eigene Datumsfelder und eine eigene Rotation, und sie
bewegen sich oft: die Kreuzpruefung setzt zweimal die Woche 25 mal
plansChecked. Zaehlte das als Aenderung, wuerde jeder Preisbesuch den Eintrag
in der Inhalts-Warteschlange nach hinten schieben, ohne dass seinen Text
jemand gelesen haette.

    python3 build/stand.py            # die aeltesten zuerst, als Warteschlange
    python3 build/stand.py --alle

Ohne Historie — flacher Klon, Zip-Download — gibt es nichts zurueck. Dann
zeigt die Seite kein Datum, statt eins zu erfinden.
"""
import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATEI = "content/steckbrief.json"

# Was als Inhalt zaehlt. Alles andere bewegt das Datum nicht: plans,
# plansJahr, plansChecked und billing gehoeren der Preisrotation,
# contentChecked ist Buchhaltung, icon und accent sind Anstrich.
INHALT = ("name", "vendor", "cat", "blurb", "tip", "links")


def _git(*args):
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def verfuegbar():
    """Nur mit vollstaendiger Historie. Ein flacher Klon kennt die frueheren
    Commits nicht und wuerde jedem Eintrag ein zu junges Datum geben — das
    waere schlechter als gar keins."""
    if _git("rev-parse", "--git-dir") is None:
        return False
    flach = _git("rev-parse", "--is-shallow-repository")
    return flach is not None and flach.strip() != "true"


def stand():
    """{Steckbrief: 'JJJJ-MM-TT'} — leer, wenn die Historie fehlt."""
    if not verfuegbar():
        return {}
    jetzt = json.loads((ROOT / DATEI).read_text(encoding="utf-8"))
    log = _git("log", "--format=%H %cs", "--reverse", "--", DATEI)
    if not log:
        return {}

    datum, vorher = {}, {}
    for zeile in log.splitlines():
        teile = zeile.split()
        if len(teile) != 2:
            continue
        commit, tag = teile
        roh = _git("show", f"{commit}:{DATEI}")
        if roh is None:
            continue
        try:
            d = json.loads(roh)
        except json.JSONDecodeError:
            # Ein Zwischenstand, der nicht parst, ist kein Grund aufzugeben.
            continue
        if not isinstance(d, dict):
            continue
        for k, v in d.items():
            if not isinstance(v, dict):
                continue
            s = _kern(v)
            if vorher.get(k) != s:
                datum[k] = tag
                vorher[k] = s

    # Eintraege, die es einmal gab und heute nicht mehr, interessieren nicht.
    return {k: v for k, v in datum.items() if k in jetzt}


def _kern(v):
    """Der Teil eines Eintrags, dessen Aenderung das Datum bewegen darf."""
    return json.dumps({f: v.get(f) for f in INHALT},
                      sort_keys=True, ensure_ascii=False)


def selbsttest():
    """Die eine Regel, die hier kaputtgehen kann: Buchhaltung ist kein Inhalt."""
    a = {"name": "X", "vendor": "Y", "cat": {"de": "c", "en": "c"},
         "blurb": {"de": "b", "en": "b"}, "tip": {"de": "t", "en": "t"},
         "links": {"home": "https://x.example"},
         "plans": {"de": "10 $", "en": "$10"}, "plansChecked": "2026-09-01",
         "billing": ["api"], "contentChecked": "2026-09-01", "icon": "x"}

    def mit(**aenderung):
        b = dict(a); b.update(aenderung); return b

    # Preis, Abrechnung, Pruefdaten und Anstrich bewegen das Datum nicht.
    for feld, wert in (("plansChecked", "2026-09-20"), ("contentChecked", "2026-09-20"),
                       ("plans", {"de": "99 $", "en": "$99"}), ("billing", ["abo", "api"]),
                       ("plansJahr", {"de": "8 $", "en": "$8"}), ("icon", "z")):
        assert _kern(mit(**{feld: wert})) == _kern(a), f"{feld} darf das Datum nicht bewegen"

    # Die sechs Inhaltsfelder bewegen es sehr wohl.
    for feld, wert in (("name", "Z"), ("vendor", "Q"),
                       ("cat", {"de": "d", "en": "d"}),
                       ("blurb", {"de": "neu", "en": "new"}),
                       ("tip", {"de": "neu", "en": "new"}),
                       ("links", {"home": "https://y.example"})):
        assert _kern(mit(**{feld: wert})) != _kern(a), f"{feld} muss das Datum bewegen"

    # Ein weggefallenes Inhaltsfeld ist auch eine Aenderung.
    ohne = {k: v for k, v in a.items() if k != "links"}
    assert _kern(ohne) != _kern(a), "ein entfernter Link muss das Datum bewegen"

    print(f"Selbsttest bestanden — Inhalt sind: {', '.join(INHALT)}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--alle", action="store_true", help="alle statt der ältesten 20")
    p.add_argument("--selbsttest", action="store_true",
                   help="prueft, dass nur Inhaltsfelder das Datum bewegen")
    args = p.parse_args()

    if args.selbsttest:
        return selbsttest()

    d = stand()
    if not d:
        print("Keine Historie verfügbar (flacher Klon?) — kein Datum ableitbar.")
        return 0
    reihe = sorted((v, k) for k, v in d.items())
    print(f"{len(reihe)} Steckbriefe · ältester Stand {reihe[0][0]}")
    for tag, k in (reihe if args.alle else reihe[:20]):
        print(f"  {tag}  {k}")
    if not args.alle and len(reihe) > 20:
        print(f"  … {len(reihe) - 20} weitere, --alle zeigt sie")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # `stand.py | head` ist der Normalfall, kein Fehler.
        sys.exit(0)
