#!/usr/bin/env python3
"""Abnahme des Bauwegs: Was build.py erzeugt, muss dasselbe bedeuten wie das,
was vorher von Hand in der Datei stand. Zeichengleich wird es nicht — die
Daten stehen jetzt als JSON statt als handgesetztes JS. Also wird getrennt
geprueft: die Daten auf Gleichheit der Struktur, alles uebrige auf jedes Byte.

Aufruf:  python3 build/verify.py <referenz-de.html> <referenz-en.html>
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from extract import spanne, als_daten, BLOECKE  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAARE = [(ROOT/"site"/"index.html", sys.argv[1]), (ROOT/"site"/"index.en.html", sys.argv[2])]

fehler = 0
for neu_pfad, ref_pfad in PAARE:
    neu = neu_pfad.read_text(encoding="utf-8")
    ref = pathlib.Path(ref_pfad).read_text(encoding="utf-8")
    print(f"\n{neu_pfad.name}")
    for name in BLOECKE:
        a, b, lit_neu = spanne(neu, name)
        c, d, lit_ref = spanne(ref, name)
        gleich = als_daten(lit_neu) == als_daten(lit_ref)
        print(f"  {name:11} {'gleich' if gleich else 'ABWEICHUNG'}")
        fehler += not gleich
        neu = neu[:a] + "«" + name + "»" + neu[b:]
        ref = ref[:c] + "«" + name + "»" + ref[d:]
    if neu == ref:
        print("  Rest der Datei: zeichengleich")
    else:
        fehler += 1
        for i, (x, y) in enumerate(zip(neu.split("\n"), ref.split("\n"))):
            if x != y:
                print(f"  Rest ABWEICHUNG ab Zeile {i+1}:\n    neu: {x[:110]}\n    ref: {y[:110]}")
                break
        else:
            print(f"  Rest ABWEICHUNG: Laenge {len(neu)} != {len(ref)}")

print("\n" + ("Abnahme bestanden." if not fehler else f"{fehler} Abweichung(en)."))
sys.exit(1 if fehler else 0)
