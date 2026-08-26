#!/usr/bin/env python3
"""Wann ein Steckbrief zuletzt inhaltlich anders aussah — aus der Historie.

Kein Feld im JSON. Ein handgepflegtes Datum rottet wie alles Handgepflegte,
und zwar lautlos: niemandem faellt auf, dass es nicht mitgezogen wurde. Git
weiss es ohnehin, kann es nicht vergessen, und kein Agent kann es faelschen.

Verglichen wird der geparste Eintrag, nicht sein Text. Eine Umformatierung der
Datei verschiebt deshalb kein einziges Datum, eine echte Aenderung an genau
einem Steckbrief nur dessen eigenes.

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
            s = json.dumps(v, sort_keys=True, ensure_ascii=False)
            if vorher.get(k) != s:
                datum[k] = tag
                vorher[k] = s

    # Eintraege, die es einmal gab und heute nicht mehr, interessieren nicht.
    return {k: v for k, v in datum.items() if k in jetzt}


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--alle", action="store_true", help="alle statt der ältesten 20")
    args = p.parse_args()

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
