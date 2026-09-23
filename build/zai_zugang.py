#!/usr/bin/env python3
"""Welcher Z.AI-Endpunkt diesen Schluessel annimmt, und mit welchem Modell.

Z.AI verkauft zwei Dinge, und jedes hat seine eigene Tuer:

  Coding-Abo (GLM Coding Plan)   https://api.z.ai/api/coding/paas/v4
  Guthaben, je Token abgerechnet https://api.z.ai/api/paas/v4

Ein Abo-Schluessel an der Guthaben-Tuer bekommt 429 mit Code 1113, "Insufficient
balance or no resource package". Das heisst dann nicht, dass Geld fehlt, sondern
dass an die falsche Tuer geklopft wurde. Genau so hat dieser Agent im September
stillgestanden: die Workflows sprachen fest den Guthaben-Endpunkt an, das
Guthaben lief leer, und das Abo lag die ganze Zeit ungenutzt daneben.

Deshalb wird hier nicht vorausgesetzt, welche Sorte Schluessel vorliegt. Erst die
Abo-Tuer, dann die Guthaben-Tuer, und die erste, die mit einem Modell 200 sagt,
gewinnt. Das Log sagt, aus welchem Topf bezahlt wird.

    ZUGANG=$(python3 build/zai_zugang.py)   # nicht in eval "$(…)": set -e saehe den Fehler nicht
    eval "$ZUGANG"                          # setzt ZAI_BASE, ZAI_MODELL, ZAI_TOPF

    python3 build/zai_zugang.py --selbsttest

Erwartet ZAI_API_KEY in der Umgebung. ZAI_MODEL legt ein Modell fest; dann wird
nur dieses probiert, an beiden Tueren.
"""
import json
import os
import re
import shlex
import sys
import urllib.error
import urllib.request

TUEREN = [
    ("abo", "https://api.z.ai/api/coding/paas/v4"),
    ("guthaben", "https://api.z.ai/api/paas/v4"),
]

# Wenn eine Tuer keine Modellliste herausgibt. Das Coding-Abo fuehrt laut Z.AI
# nur GLM-5.3 und GLM-5.3-Flash; der Rest ist fuer die Guthaben-Tuer.
ERSATZLISTE = ["glm-5.3", "glm-5.3-flash", "glm-4.6"]

# Innerhalb einer Version: das volle Modell vor seinen kleineren Geschwistern.
# Die fruehere Fassung sortierte die Namen einfach rueckwaerts als Text, und
# damit stand glm-5.3-flashx vor glm-5.3 — der Lauf nahm die kleinste Variante.
ZUSATZ_RANG = {"": 0, "turbo": 1, "flash": 2, "flashx": 3, "air": 4}

MODELL_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def reihenfolge(ids):
    """GLM-Modelle, bestes zuerst: hoechste Version, darin das volle Modell."""
    def zerlege(i):
        m = re.match(r"^glm-(\d+(?:\.\d+)*)(?:-(.+))?$", i.lower())
        if not m:
            return (), 99
        version = tuple(int(x) for x in m.group(1).split("."))
        return version, ZUSATZ_RANG.get(m.group(2) or "", 5)
    glm = [i for i in ids if i.lower().startswith("glm")]
    # Zwei stabile Durchgaenge statt eines zusammengesetzten Schluessels: Versionen
    # verschiedener Laenge lassen sich nicht durch Negieren umdrehen, (-5,) sortiert
    # vor (-5, -3). Erst nach Zusatz, dann nach Version rueckwaerts — die Sortierung
    # ist stabil, also bleibt die Zusatz-Reihenfolge innerhalb einer Version stehen.
    glm.sort(key=lambda i: zerlege(i)[1])
    glm.sort(key=lambda i: zerlege(i)[0], reverse=True)
    return glm


def anfrage(url, key, daten=None):
    """(HTTP-Status, Antworttext). Netzfehler werden Status 0, nicht Ausnahme."""
    kopf = {"Authorization": f"Bearer {key}"}
    body = None
    if daten is not None:
        kopf["Content-Type"] = "application/json"
        body = json.dumps(daten).encode()
    req = urllib.request.Request(url, data=body, headers=kopf)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # Zeitueberschreitung, DNS, TLS
        return 0, f"{type(e).__name__}: {e}"


def fehlercode(text):
    """Z.AIs eigener Code aus einer Fehlerantwort, etwa '1113'."""
    try:
        return str(json.loads(text).get("error", {}).get("code", "")) or ""
    except (ValueError, AttributeError):
        return ""


def log(*a):
    print(*a, file=sys.stderr)


def probiere(topf, base, key, gewuenscht):
    """Das erste Modell an dieser Tuer, das 200 sagt — oder None und die Befunde."""
    log(f"--- {topf}: {base}")
    if gewuenscht:
        kandidaten = [gewuenscht]
    else:
        status, text = anfrage(f"{base}/models", key)
        ids = []
        if status == 200:
            try:
                ids = [m["id"] for m in json.loads(text).get("data", [])]
            except (ValueError, KeyError, TypeError):
                ids = []
        log(f"    /models → HTTP {status}" + (f" · {', '.join(ids)}" if ids else ""))
        # /models listet, was die API kennt, nicht was dieser Schluessel darf.
        # Deshalb bekommt jeder Kandidat eine Anfrage mit einem einzigen Token.
        kandidaten = reihenfolge(ids) or ERSATZLISTE

    befunde = []
    for modell in kandidaten:
        status, text = anfrage(f"{base}/chat/completions", key, {
            "model": modell, "max_tokens": 1,
            "messages": [{"role": "user", "content": "hi"}],
        })
        code = fehlercode(text)
        log(f"    {modell} → HTTP {status}" + (f" (Code {code})" if code else ""))
        if status == 200:
            return modell, befunde
        befunde.append((modell, status, code, text[:200]))
    return None, befunde


def urteil(ergebnisse):
    """Was die Befunde an beiden Tueren zusammen bedeuten, in einem Satz."""
    abo = ergebnisse.get("abo", [])
    guthaben = ergebnisse.get("guthaben", [])
    guthaben_leer = any(c == "1113" for _, _, c, _ in guthaben)
    abo_verweigert = bool(abo) and all(s in (401, 403) for _, s, _, _ in abo)
    abo_leer = any(c == "1113" for _, _, c, _ in abo)

    if guthaben_leer and abo_leer:
        return ("Weder Abo noch Guthaben traegt: beide Tueren antworten mit Code 1113. "
                "Entweder ist das Abo-Kontingent fuer dieses Zeitfenster verbraucht, "
                "oder der Schluessel gehoert zu keinem Abo und das Guthaben ist leer.")
    if guthaben_leer:
        return ("Das Guthaben ist leer (Code 1113), und die Abo-Tuer nimmt diesen "
                "Schluessel nicht an. Entweder Guthaben aufladen, oder einen Schluessel "
                "aus dem Coding-Abo als ZAI_API_KEY hinterlegen: "
                "https://z.ai/manage-apikey/apikey-list")
    if abo_verweigert:
        return "Die Abo-Tuer verweigert den Schluessel, und an der Guthaben-Tuer antwortet kein Modell."
    return "An keiner der beiden Tueren hat ein Modell geantwortet; die Befunde stehen oben."


def main():
    key = os.environ.get("ZAI_API_KEY", "")
    if not key:
        log("ZAI_API_KEY ist nicht gesetzt.")
        return 1
    gewuenscht = os.environ.get("ZAI_MODEL", "").strip()
    if gewuenscht and not MODELL_ID.match(gewuenscht):
        log(f"ZAI_MODEL ist kein gueltiger Modellname: {gewuenscht!r}")
        return 1

    ergebnisse = {}
    for topf, base in TUEREN:
        modell, befunde = probiere(topf, base, key, gewuenscht)
        if modell:
            if not MODELL_ID.match(modell):
                log(f"Die API nannte einen Modellnamen, der hier nichts verloren hat: {modell!r}")
                return 1
            log(f"Gewaehlt: {modell} an der {topf.capitalize()}-Tuer — "
                + ("es zahlt das Coding-Abo." if topf == "abo" else "es zahlt das Guthaben, je Token."))
            print(f"ZAI_BASE={shlex.quote(base)}")
            print(f"ZAI_MODELL={shlex.quote(modell)}")
            print(f"ZAI_TOPF={shlex.quote(topf)}")
            return 0
        ergebnisse[topf] = befunde

    log("")
    log(urteil(ergebnisse))
    letzter = next((t for b in reversed(list(ergebnisse.values())) for *_, t in b[-1:]), "")
    if letzter:
        log(f"Letzte Antwort: {letzter}")
    return 1


def selbsttest():
    fehler = 0

    def pruefe(name, ist, soll):
        nonlocal fehler
        ok = ist == soll
        fehler += not ok
        print(f"{'ok ' if ok else 'FEHLER'}  {name}")
        if not ok:
            print(f"        soll {soll!r}\n        ist  {ist!r}")

    # Die Liste, die Z.AI am 23.09.2026 tatsaechlich geliefert hat.
    gelistet = ["glm-4.5", "glm-4.5-air", "glm-4.6", "glm-4.7", "glm-5", "glm-5-turbo",
                "glm-5.1", "glm-5.2", "glm-5.3", "glm-5.3-flash", "glm-5.3-flashx"]
    r = reihenfolge(gelistet)
    pruefe("volles Modell vor seinen Varianten", r[:3], ["glm-5.3", "glm-5.3-flash", "glm-5.3-flashx"])
    pruefe("5.1 vor 5, 5 vor 5-turbo", r[4:7], ["glm-5.1", "glm-5", "glm-5-turbo"])
    pruefe("aelteste zuletzt, air hinter dem vollen", r[-2:], ["glm-4.5", "glm-4.5-air"])
    pruefe("fremde Modelle fallen heraus", reihenfolge(["gpt-x", "glm-5"]), ["glm-5"])
    pruefe("leere Liste bleibt leer", reihenfolge([]), [])

    pruefe("Code 1113 wird erkannt",
           fehlercode('{"error":{"code":"1113","message":"Insufficient balance"}}'), "1113")
    pruefe("kaputtes JSON ergibt keinen Code", fehlercode("<html>"), "")

    leer = [("glm-5.3", 429, "1113", "")]
    zu = [("glm-5.3", 401, "", "")]
    pruefe("Guthaben leer, Abo verweigert → Hinweis auf Abo-Schluessel",
           "apikey-list" in urteil({"abo": zu, "guthaben": leer}), True)
    pruefe("beide 1113 → beide genannt",
           "beide Tueren" in urteil({"abo": leer, "guthaben": leer}), True)

    pruefe("Modellname mit Leerzeichen wird abgewiesen", bool(MODELL_ID.match("glm 5; rm")), False)
    pruefe("Ausgabe ist fuer die Shell gequotet", shlex.quote("https://a/b"), "https://a/b")

    print(f"\n{'alles in Ordnung' if not fehler else f'{fehler} Fehler'}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(selbsttest() if "--selbsttest" in sys.argv else main())
