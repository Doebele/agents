#!/usr/bin/env python3
"""Auftrag und Vergleich fuer die Kreuzpruefung der Preise.

Zwei Agenten lesen dieselben Anbieterseiten und schreiben ihren Befund in ein
festes Schema. Dieses Skript stellt die Befunde gegenueber, bevor ein Modell
sie zu Gesicht bekommt — dieselbe Arbeitsteilung wie bei linkcheck.py: die
mechanische Haelfte deterministisch, damit das Urteil sich auf das Strittige
konzentriert und der Vergleich selbst nachlesbar bleibt.

    python3 build/kreuzpruefung.py auftrag --anzahl 20
    python3 build/kreuzpruefung.py vergleich befund-gemini.json befund-zai.json

Beide Unterbefehle schreiben Exit 0, solange sie nicht abstuerzen. Ein fehlender
oder kaputter Befund ist ein Ergebnis, kein Fehler: dann steht im Bericht, dass
dieser Agent nichts geliefert hat, und die Eintraege gelten als ungeprueft.
"""
import argparse
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STECKBRIEF = ROOT / "content" / "steckbrief.json"

# Schreibweisen, die dasselbe meinen. Bewusst kurz gehalten: die Liste soll
# Tippvarianten einfangen, nicht Einheiten ineinander umrechnen. Was hier nicht
# steht, gilt als verschieden und landet als Abweichung im Bericht — lieber
# einmal zu viel vorgelegt als eine echte Abweichung stillschweigend geglaettet.
WAEHRUNG = {"$": "USD", "us$": "USD", "usd": "USD", "€": "EUR", "eur": "EUR",
            "£": "GBP", "gbp": "GBP"}
EINHEIT = {
    "1m tokens": "1M Tokens", "1m token": "1M Tokens", "1 mio tokens": "1M Tokens",
    "million tokens": "1M Tokens", "je 1m tokens": "1M Tokens", "per 1m tokens": "1M Tokens",
    "1k tokens": "1K Tokens", "1000 tokens": "1K Tokens",
    "monat": "Monat", "month": "Monat", "mo": "Monat", "monatlich": "Monat", "monthly": "Monat",
    "jahr": "Jahr", "year": "Jahr", "jaehrlich": "Jahr", "yearly": "Jahr", "annual": "Jahr",
    "stunde": "Stunde", "hour": "Stunde", "hourly": "Stunde",
    "nutzer/monat": "Nutzer/Monat", "user/month": "Nutzer/Monat",
    "seat/month": "Nutzer/Monat", "platz/monat": "Nutzer/Monat",
    "einmalig": "einmalig", "one-off": "einmalig", "one time": "einmalig",
}


def steckbriefe():
    return json.loads(STECKBRIEF.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- Auftrag

def auftrag(args):
    """Die N Steckbriefe mit dem aeltesten plansChecked, ohne Datum zuerst."""
    d = steckbriefe()
    reihe = sorted((v.get("plansChecked", ""), k) for k, v in d.items() if v.get("plans"))
    gewaehlt = [k for _, k in reihe[: args.anzahl]]

    eintraege = []
    for k in gewaehlt:
        v = d[k]
        eintraege.append({
            "name": k,
            "vendor": v.get("vendor", k),
            "home": (v.get("links") or {}).get("home", ""),
        })
    # Absichtlich ohne die aktuellen Werte: wer den alten Preis vor Augen hat,
    # bestaetigt ihn. Was im Katalog steht, holt der Vergleich unten selbst aus
    # steckbrief.json — die Rechercheure sollen die Seite lesen, nicht uns.
    out = {
        "erstellt": datetime.date.today().isoformat(),
        "anzahl": len(eintraege),
        "eintraege": eintraege,
    }
    pathlib.Path(args.out).write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{len(eintraege)} Steckbriefe im Auftrag → {args.out}")
    for e in eintraege:
        stand = d[e["name"]].get("plansChecked") or "nie"
        print(f"  {stand:>10}  {e['name']}")
    return 0


# ---------------------------------------------------------------- Vergleich

def zahl(s):
    """'0,15' · '$1.234,56' · '12 USD' → '0.15' · '1234.56' · '12'. Sonst None."""
    if s is None:
        return None
    t = re.sub(r"[^\d,.\-]", "", str(s))
    if not t:
        return None
    # Bei beiden Trennzeichen entscheidet das letzte ueber das Komma.
    if "," in t and "." in t:
        dez = max(t.rfind(","), t.rfind("."))
        t = re.sub(r"[,.]", "", t[:dez]) + "." + re.sub(r"[,.]", "", t[dez + 1:])
    elif "," in t:
        t = t.replace(",", ".")
    try:
        f = float(t)
    except ValueError:
        return None
    return f"{f:g}"


def waehrung(s):
    t = str(s or "").strip().lower()
    return WAEHRUNG.get(t, t.upper() or "?")


def einheit(s):
    t = re.sub(r"\s+", " ", str(s or "").strip().lower())
    t = re.sub(r"^(je|pro|per)\s+", "", t)
    return EINHEIT.get(t, t or "?")


def preisschluessel(p):
    """Ein Preis, auf das reduziert, worueber zwei Leser sich einig sein muessen.

    Die Bezeichnung bleibt aussen vor: ob jemand 'GPT-OSS-120B Eingabe' oder
    'gpt-oss-120b input' schreibt, ist Geschmack. Betrag, Waehrung und Einheit
    sind es nicht.
    """
    return (zahl(p.get("betrag")), waehrung(p.get("waehrung")), einheit(p.get("einheit")))


def befund_lesen(pfad):
    """(agent, eintraege, fehler). Ein kaputter Befund ist ein Ergebnis."""
    p = pathlib.Path(pfad)
    name = p.stem.replace("befund-", "") or p.stem
    if not p.exists():
        return name, {}, "keine Datei abgeliefert"
    roh = p.read_text(encoding="utf-8", errors="replace").strip()
    if not roh:
        return name, {}, "Datei ist leer"
    # Modelle rahmen JSON gern in einen Code-Block. Das ist kein Grund, den
    # ganzen Lauf wegzuwerfen.
    if roh.startswith("```"):
        roh = re.sub(r"^```[a-z]*\s*|\s*```$", "", roh, flags=re.S)
    try:
        d = json.loads(roh)
    except json.JSONDecodeError as e:
        return name, {}, f"kein lesbares JSON ({e})"
    if not isinstance(d, dict) or not isinstance(d.get("eintraege"), dict):
        return name, {}, "JSON ohne Objekt 'eintraege'"
    return d.get("agent") or name, d["eintraege"], None


def urteil(a, b):
    """einig · uneinig · einseitig · leer — plus die Felder, die auseinandergehen."""
    if a is None and b is None:
        return "leer", []
    if a is None or b is None:
        return "einseitig", []
    ab = []
    for feld in ("erhaeltlich", "gratis"):
        if a.get(feld) != b.get(feld):
            ab.append(feld)
    if set(a.get("billing") or []) != set(b.get("billing") or []):
        ab.append("billing")
    pa = {preisschluessel(p) for p in (a.get("preise") or []) if isinstance(p, dict)}
    pb = {preisschluessel(p) for p in (b.get("preise") or []) if isinstance(p, dict)}
    if pa != pb:
        ab.append("preise")
    return ("einig" if not ab else "uneinig"), ab


def preiszeile(p):
    if not isinstance(p, dict):
        return f"`{p!r}` (kein Objekt)"
    betrag, wae, ein = preisschluessel(p)
    was = str(p.get("was") or "").strip() or "—"
    return f"{was}: {betrag or '?'} {wae} / {ein}"


def ja_nein(v):
    return {True: "ja", False: "nein", None: "unbekannt"}.get(v, str(v))


def block(agent, e):
    if e is None:
        return [f"- **{agent}**: nichts geliefert"]
    z = [f"- **{agent}** · Quelle: {e.get('quelle') or 'keine genannt'}"]
    z.append(f"  - erhältlich: {ja_nein(e.get('erhaeltlich'))}"
             f" · Gratisstufe: {ja_nein(e.get('gratis'))}"
             f" · billing: {', '.join(e.get('billing') or []) or '—'}")
    preise = e.get("preise") or []
    z += [f"  - {preiszeile(p)}" for p in preise] or ["  - keine Preise genannt"]
    if e.get("notiz"):
        z.append(f"  - Notiz: {e['notiz']}")
    return z


def vergleich(args):
    kat = steckbriefe()
    auf = json.loads(pathlib.Path(args.auftrag).read_text(encoding="utf-8"))
    namen = [e["name"] for e in auf["eintraege"]]

    a_name, a_daten, a_fehler = befund_lesen(args.befund_a)
    b_name, b_daten, b_fehler = befund_lesen(args.befund_b)

    zeilen, tabelle, maschine = [], [], {}
    zaehler = {"einig": 0, "uneinig": 0, "einseitig": 0, "leer": 0}

    for n in namen:
        a, b = a_daten.get(n), b_daten.get(n)
        u, felder = urteil(a, b)
        zaehler[u] += 1
        maschine[n] = {"urteil": u, "felder": felder,
                       a_name: a, b_name: b,
                       "alt": {"plans": kat.get(n, {}).get("plans"),
                               "billing": kat.get(n, {}).get("billing"),
                               "plansChecked": kat.get(n, {}).get("plansChecked")}}

        marke = {"einig": "einig", "uneinig": "**uneinig**",
                 "einseitig": "einseitig", "leer": "leer"}[u]
        tabelle.append(f"| {n} | {kat.get(n, {}).get('plansChecked') or 'nie'} | {marke} | "
                       f"{', '.join(felder) or '—'} |")

        # Wo beide nichts geliefert haben, sagt die Tabelle bereits alles.
        if u == "leer":
            continue

        zeilen.append(f"### {n}")
        zeilen.append("")
        alt = kat.get(n, {}).get("plans") or {}
        zeilen.append(f"- **Katalog** (Stand {kat.get(n, {}).get('plansChecked') or 'nie'}) · "
                      f"billing: {', '.join(kat.get(n, {}).get('billing') or []) or '—'}")
        zeilen.append(f"  - de: {alt.get('de', '—')}")
        zeilen.append(f"  - en: {alt.get('en', '—')}")
        zeilen += block(a_name, a)
        zeilen += block(b_name, b)
        zeilen.append("")

    kopf = [
        "# Kreuzprüfung Preise",
        "",
        f"{datetime.date.today().isoformat()} · {len(namen)} Steckbriefe · "
        f"{zaehler['einig']} einig · **{zaehler['uneinig']} uneinig** · "
        f"{zaehler['einseitig']} einseitig · {zaehler['leer']} ohne Befund",
        "",
    ]
    for agent, fehler in ((a_name, a_fehler), (b_name, b_fehler)):
        if fehler:
            kopf += [f"> {agent}: {fehler}. Alle Einträge dieses Agenten gelten als ungeprüft.", ""]
    kopf += ["| Steckbrief | Stand | Urteil | Strittig |",
             "|---|---|---|---|"] + tabelle + [""]

    pathlib.Path(args.out).write_text("\n".join(kopf + zeilen) + "\n", encoding="utf-8")
    pathlib.Path(args.json).write_text(
        json.dumps({"stand": datetime.date.today().isoformat(),
                    "agenten": [a_name, b_name], "eintraege": maschine},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{zaehler['einig']} einig · {zaehler['uneinig']} uneinig · "
          f"{zaehler['einseitig']} einseitig · {zaehler['leer']} ohne Befund")
    print(f"Bericht: {args.out}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="befehl", required=True)

    a = sub.add_parser("auftrag", help="die N ältesten Preisstände als auftrag.json")
    a.add_argument("--anzahl", type=int, default=20)
    a.add_argument("--out", default="auftrag.json")
    a.set_defaults(func=auftrag)

    v = sub.add_parser("vergleich", help="zwei Befunde gegenüberstellen")
    v.add_argument("befund_a")
    v.add_argument("befund_b")
    v.add_argument("--auftrag", default="auftrag.json")
    v.add_argument("--out", default="vergleich.md")
    v.add_argument("--json", default="vergleich.json")
    v.set_defaults(func=vergleich)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
