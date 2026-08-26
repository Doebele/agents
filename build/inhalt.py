#!/usr/bin/env python3
"""Welche Steckbriefe am laengsten niemand angesehen hat.

Das Gegenstueck zur Preisrotation, nur fuer den Text: stimmt noch, was der
Eintrag behauptet? Gibt es das Produkt ueberhaupt noch, heisst es noch so,
steht es im richtigen Baustein?

    python3 build/inhalt.py auftrag --anzahl 25

"Zuletzt angesehen" ist das spaetere von zwei Daten:

  contentChecked  jemand hat den Eintrag geprueft und nichts gefunden
  stand           der Eintrag war zuletzt inhaltlich anders (aus der Historie)

Beide braucht es. Ohne `stand` liefe ein frisch geschriebener Steckbrief
sofort wieder in die Pruefung. Ohne `contentChecked` bliebe ein geprueftes,
aber unveraendertes vorne stehen — denn wer nichts findet, aendert nichts,
und was sich nicht aendert, bewegt die Historie nicht.
"""
import argparse
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STECKBRIEF = ROOT / "content" / "steckbrief.json"

try:
    import stand as _stand
except ImportError:  # stand.py liegt noch nicht vor
    _stand = None


def gesehen():
    """{Steckbrief: 'JJJJ-MM-TT' oder ''} — je das spaetere der beiden Daten."""
    d = json.loads(STECKBRIEF.read_text(encoding="utf-8"))
    historie = _stand.stand() if _stand else {}
    return {k: max(v.get("contentChecked", ""), historie.get(k, "")) for k, v in d.items()}


def auftrag(args):
    d = json.loads(STECKBRIEF.read_text(encoding="utf-8"))
    g = gesehen()
    reihe = sorted((v, k) for k, v in g.items())
    gewaehlt = reihe[: args.anzahl]

    out = {
        "erstellt": datetime.date.today().isoformat(),
        "anzahl": len(gewaehlt),
        "eintraege": [{"name": k,
                       "gesehen": v or None,
                       "home": (d[k].get("links") or {}).get("home", "")}
                      for v, k in gewaehlt],
    }
    pathlib.Path(args.out).write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not _stand or not _stand.stand():
        print("Hinweis: keine Historie verfügbar — die Reihenfolge stützt sich")
        print("         allein auf contentChecked.")
    print(f"{len(gewaehlt)} Steckbriefe im Auftrag → {args.out}")
    for wann, k in gewaehlt:
        print(f"  {wann or 'nie':>10}  {k}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="befehl", required=True)
    a = sub.add_parser("auftrag", help="die am längsten ungesehenen Steckbriefe")
    a.add_argument("--anzahl", type=int, default=25)
    a.add_argument("--out", default="auftrag-inhalt.json")
    a.set_defaults(func=auftrag)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
