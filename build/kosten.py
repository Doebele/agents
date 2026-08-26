#!/usr/bin/env python3
"""Was ein Agentenlauf gekostet hat — einsammeln, ablegen, auszaehlen.

Vier Laeufe, drei Harnesses, drei Anbieter: die Zahlen liegen an drei
verschiedenen Stellen und heissen ueberall anders. Dieses Skript bringt sie in
eine Zeile.

    kosten.py lauf   --agent claude --execution <datei>   >> metriken/laeufe.csv
    kosten.py lauf   --agent gemini --telemetrie <datei>
    kosten.py bericht metriken/laeufe.csv

Was nicht auffindbar ist, bleibt leer. Eine leere Spalte sagt "hier gibt es
keine Zahl", eine geratene sagt etwas Falsches — und eine Kostenaufstellung,
der man nicht glauben kann, ist keine.

Zu den Kostenzahlen von Claude Code: die stehen im Ausfuehrungsprotokoll der
Action und sind eine Schaetzung des Clients. Als Verlauf taugen sie, als
Abrechnung nicht — dafuer gibt es kosten.py anthropic.
"""
import argparse
import csv
import datetime
import json
import os
import pathlib
import sys

SPALTEN = ["datum", "lauf", "agent", "modell", "input", "output",
           "cache_write", "cache_read", "kosten_usd", "turns", "dauer_s",
           "run_id", "run_url"]

# Wie die Felder in den drei Welten heissen. Links der Name in unserer Zeile,
# rechts alles, was dasselbe meint.
TOKENFELDER = {
    "input": ("input_tokens", "uncached_input_tokens", "prompt_tokens",
              "promptTokenCount", "input"),
    "output": ("output_tokens", "completion_tokens", "candidatesTokenCount",
               "output"),
    "cache_write": ("cache_creation_input_tokens", "cache_creation", "cache_write"),
    "cache_read": ("cache_read_input_tokens", "cachedContentTokenCount",
                   "cached_tokens", "cache_read"),
}


def nach_muster(objekt):
    """Zweiter Anlauf: jeder Zahlenwert, dessen Schluessel 'token' enthaelt.

    Gedacht fuer Protokolle, deren Feldnamen wir nicht kennen — lieber ueber ein
    Muster gefunden als gar nicht. Was sich keiner Spalte zuordnen laesst, faellt
    weg statt irgendwo hineingerechnet zu werden.
    """
    eimer = {k: 0 for k in TOKENFELDER}
    getroffen = set()

    def geh(o):
        if isinstance(o, dict):
            for k, v in o.items():
                kl = k.lower()
                if isinstance(v, (int, float)) and not isinstance(v, bool) and "token" in kl:
                    if "cach" in kl:
                        ziel = "cache_read"
                    elif "input" in kl or "prompt" in kl:
                        ziel = "input"
                    elif "output" in kl or "candidate" in kl or "completion" in kl:
                        ziel = "output"
                    else:
                        continue
                    eimer[ziel] += v
                    getroffen.add(ziel)
                geh(v)
        elif isinstance(o, list):
            for v in o:
                geh(v)

    geh(objekt)
    return {k: v for k, v in eimer.items() if k in getroffen}


def tief_suchen(objekt, namen, summe=False):
    """Groesster Zahlenwert unter einem dieser Schluessel, irgendwo im Baum.

    Die Protokolle sind verschachtelt und je nach Harness anders geschnitten.
    Statt drei Formate nachzubauen — die sich unter uns aendern koennen — wird
    gesucht. Groesster Wert, weil Gesamtsummen weiter oben stehen als die
    Einzelposten darunter.
    """
    treffer = []

    def geh(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in namen:
                    if isinstance(v, bool):
                        pass
                    elif isinstance(v, (int, float)):
                        treffer.append(v)
                    elif isinstance(v, dict):
                        # z.B. cache_creation: {ephemeral_5m…, ephemeral_1h…}
                        summe = sum(x for x in v.values() if isinstance(x, (int, float)))
                        if summe:
                            treffer.append(summe)
                geh(v)
        elif isinstance(o, list):
            for v in o:
                geh(v)

    geh(objekt)
    if not treffer:
        return ""
    # Ein Ergebnisobjekt traegt die Summe schon, viele Einzelmeldungen nicht.
    return sum(treffer) if summe else max(treffer)


def laden(pfad):
    """JSON oder JSONL, beides kommt vor. Rueckgabe: Liste von Objekten."""
    p = pathlib.Path(pfad)
    if not p.exists():
        return []
    roh = p.read_text(encoding="utf-8", errors="replace").strip()
    if not roh:
        return []
    try:
        d = json.loads(roh)
        return d if isinstance(d, list) else [d]
    except json.JSONDecodeError:
        pass
    zeilen = []
    for z in roh.splitlines():
        z = z.strip()
        if not z:
            continue
        try:
            zeilen.append(json.loads(z))
        except json.JSONDecodeError:
            continue
    return zeilen


def lauf(args):
    quelle = args.execution or args.telemetrie
    daten = laden(quelle) if quelle else []

    zeile = {s: "" for s in SPALTEN}
    zeile["datum"] = datetime.date.today().isoformat()
    zeile["lauf"] = args.lauf or os.environ.get("GITHUB_WORKFLOW", "")
    zeile["agent"] = args.agent
    zeile["run_id"] = os.environ.get("GITHUB_RUN_ID", "")
    if zeile["run_id"]:
        zeile["run_url"] = (f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
                            f"{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{zeile['run_id']}")
    if args.dauer:
        zeile["dauer_s"] = args.dauer

    # Claude Code schliesst sein Protokoll mit einem Objekt vom Typ "result" ab,
    # und dort stehen die Summen. Gibt es das, zaehlt nur das — sonst koennte die
    # Suche unten den groessten Einzelposten fuer die Gesamtsumme halten.
    alle = daten
    ergebnis = [o for o in daten if isinstance(o, dict) and o.get("type") == "result"]
    daten = ergebnis or daten

    if daten:
        for feld, namen in TOKENFELDER.items():
            zeile[feld] = tief_suchen(daten, namen, summe=bool(args.telemetrie))
        if all(zeile[f] == "" for f in TOKENFELDER):
            # Die Feldnamen der Gemini-Telemetrie sind nicht in Stein gemeisselt.
            # Also zweiter Anlauf ueber alles, was "token" im Namen hat.
            for feld, wert in nach_muster(daten).items():
                zeile[feld] = wert
        kosten = tief_suchen(daten, ("total_cost_usd", "cost_usd", "totalCostUsd"))
        if kosten != "":
            zeile["kosten_usd"] = f"{float(kosten):.4f}"
        turns = tief_suchen(daten, ("num_turns", "turns", "sessionTurnCount"))
        if turns != "":
            zeile["turns"] = int(turns)
        ms = tief_suchen(daten, ("duration_ms", "durationMs"))
        if ms != "" and not zeile["dauer_s"]:
            zeile["dauer_s"] = int(float(ms) / 1000)
        modell = ""
        for o in alle:
            modell = modell or _modell(o)
        zeile["modell"] = args.modell or modell
    else:
        zeile["modell"] = args.modell

    schreiben(args.out, zeile)
    fehlend = [k for k in ("input", "output") if zeile[k] == ""]
    hinweis = f"  (keine Tokenzahlen in {quelle or 'ohne Quelle'})" if fehlend else ""
    print(f"{zeile['agent']}: in {zeile['input'] or '—'} · out {zeile['output'] or '—'} · "
          f"{zeile['kosten_usd'] or '—'} USD · {zeile['turns'] or '—'} Turns{hinweis}")
    return 0


def _modell(o, tiefe=0):
    if tiefe > 6 or not isinstance(o, (dict, list)):
        return ""
    if isinstance(o, dict):
        for k in ("model", "modell", "model_id", "modelName"):
            v = o.get(k)
            if isinstance(v, str) and v:
                return v
        for v in o.values():
            t = _modell(v, tiefe + 1)
            if t:
                return t
    else:
        for v in o:
            t = _modell(v, tiefe + 1)
            if t:
                return t
    return ""


def schreiben(pfad, zeile):
    p = pathlib.Path(pfad)
    p.parent.mkdir(parents=True, exist_ok=True)
    neu = not p.exists() or p.stat().st_size == 0
    with p.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SPALTEN)
        if neu:
            w.writeheader()
        w.writerow(zeile)


# ---------------------------------------------------------------- Bericht

def bericht(args):
    p = pathlib.Path(args.csv)
    if not p.exists():
        print(f"{args.csv} gibt es noch nicht — noch kein Lauf erfasst.")
        return 0
    zeilen = list(csv.DictReader(p.open(encoding="utf-8")))
    if not zeilen:
        print("Noch keine Zeilen.")
        return 0

    def zahl(z, k):
        try:
            return float(z.get(k) or 0)
        except ValueError:
            return 0.0

    gruppen = {}
    for z in zeilen:
        monat = (z.get("datum") or "")[:7]
        k = (monat, z.get("lauf", ""), z.get("agent", ""))
        g = gruppen.setdefault(k, {"laeufe": 0, "input": 0.0, "output": 0.0,
                                   "cache_read": 0.0, "kosten": 0.0, "dauer": 0.0})
        g["laeufe"] += 1
        for feld in ("input", "output", "cache_read"):
            g[feld] += zahl(z, feld)
        g["kosten"] += zahl(z, "kosten_usd")
        g["dauer"] += zahl(z, "dauer_s")

    print("| Monat | Lauf | Agent | Läufe | Input | Output | Cache gelesen | USD | ø Dauer |")
    print("|---|---|---|---|---|---|---|---|---|")
    for (monat, lf, agent), g in sorted(gruppen.items()):
        dauer = g["dauer"] / g["laeufe"] if g["laeufe"] else 0
        def z(wert, form):
            return format(wert, form) if wert else "—"
        print(f"| {monat} | {lf} | {agent} | {g['laeufe']} | {z(g['input'], ',.0f')} | "
              f"{z(g['output'], ',.0f')} | {z(g['cache_read'], ',.0f')} | "
              f"{z(g['kosten'], '.2f')} | {(f'{dauer/60:.0f} min' if dauer else '—')} |")
    return 0


# ---------------------------------------------------------------- Anthropic

def anthropic(args):
    """Was die Abrechnung sagt, nicht was der Client schaetzt.

    Braucht einen Admin-Schluessel, nicht den normalen API-Key. Ohne den tut
    das Skript nichts und sagt das auch — ein fehlendes Secret ist kein Grund,
    einen Lauf scheitern zu lassen.
    """
    import urllib.request
    import urllib.error

    key = os.environ.get("ANTHROPIC_ADMIN_KEY", "")
    if not key:
        print("ANTHROPIC_ADMIN_KEY ist nicht gesetzt — übersprungen.")
        return 0

    seit = (datetime.date.today() - datetime.timedelta(days=args.tage)).isoformat() + "T00:00:00Z"

    def hole(pfad, felder):
        url = f"https://api.anthropic.com/v1/organizations/{pfad}?starting_at={seit}&" + felder
        req = urllib.request.Request(url, headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            print(f"  {pfad}: HTTP {e.code} — {e.read()[:200].decode('utf-8', 'replace')}")
        except Exception as e:
            print(f"  {pfad}: {type(e).__name__}: {e}")
        return None

    nutzung = hole("usage_report/messages",
                   "bucket_width=1d&group_by[]=api_key_id&group_by[]=model&limit=31")
    if nutzung:
        zeilen = []
        for eimer in nutzung.get("data", []):
            tag = (eimer.get("starting_at") or "")[:10]
            for r in eimer.get("results", []):
                cw = r.get("cache_creation") or {}
                zeilen.append({
                    "datum": tag,
                    "api_key_id": r.get("api_key_id") or "",
                    "modell": r.get("model") or "",
                    "input": r.get("uncached_input_tokens", 0),
                    "output": r.get("output_tokens", 0),
                    "cache_write": sum(v for v in cw.values() if isinstance(v, (int, float))),
                    "cache_read": r.get("cache_read_input_tokens", 0),
                    "web_search": (r.get("server_tool_use") or {}).get("web_search_requests", 0),
                })
        _csv(args.nutzung_out, ["datum", "api_key_id", "modell", "input", "output",
                                "cache_write", "cache_read", "web_search"], zeilen)
        print(f"{len(zeilen)} Nutzungszeilen → {args.nutzung_out}")

    kosten = hole("cost_report", "bucket_width=1d&group_by[]=description&limit=31")
    if kosten:
        zeilen = []
        for eimer in kosten.get("data", []):
            tag = (eimer.get("starting_at") or "")[:10]
            for r in eimer.get("results", []):
                zeilen.append({
                    "datum": tag,
                    "beschreibung": r.get("description") or r.get("cost_type") or "",
                    "modell": r.get("model") or "",
                    # amount kommt in der kleinsten Einheit, also Cent.
                    "betrag_usd": f"{float(r.get('amount', 0)) / 100:.4f}",
                })
        _csv(args.kosten_out, ["datum", "beschreibung", "modell", "betrag_usd"], zeilen)
        summe = sum(float(z["betrag_usd"]) for z in zeilen)
        print(f"{len(zeilen)} Kostenzeilen → {args.kosten_out} · {summe:.2f} USD in {args.tage} Tagen")
    return 0


def _csv(pfad, spalten, zeilen):
    p = pathlib.Path(pfad)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=spalten)
        w.writeheader()
        w.writerows(zeilen)


# ---------------------------------------------------------------- Sammeln

def sammeln(args):
    """Die kosten-Artefakte der letzten Tage einsammeln und zusammenfuehren.

    Jeder Agentenlauf legt seine Zeile als Artefakt ab, statt sie selbst in
    einen Zweig zu schreiben: zwei Jobs, die gleichzeitig fertig werden, wuerden
    sich sonst gegenseitig ueberschreiben. Hier holt sie ein einzelner Lauf ab.
    """
    import io
    import urllib.request
    import urllib.error
    import zipfile

    token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repo:
        print("GITHUB_TOKEN oder GITHUB_REPOSITORY fehlt — übersprungen.")
        return 0

    def api(pfad, roh=False):
        req = urllib.request.Request(
            pfad if pfad.startswith("http") else f"https://api.github.com/repos/{repo}/{pfad}",
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read() if roh else json.load(r)
        except urllib.error.HTTPError as e:
            print(f"  {pfad}: HTTP {e.code}")
        except Exception as e:
            print(f"  {pfad}: {type(e).__name__}: {e}")
        return None

    grenze = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=args.tage)
    bekannt = set()
    p = pathlib.Path(args.out)
    if p.exists():
        for z in csv.DictReader(p.open(encoding="utf-8")):
            bekannt.add((z.get("run_id", ""), z.get("agent", "")))

    neu = []
    seite = 1
    while seite <= 5:
        d = api(f"actions/artifacts?per_page=100&page={seite}")
        if not d or not d.get("artifacts"):
            break
        for a in d["artifacts"]:
            if not a["name"].startswith("kosten-") or a.get("expired"):
                continue
            erzeugt = a.get("created_at", "")
            try:
                wann = datetime.datetime.fromisoformat(erzeugt.replace("Z", "+00:00"))
            except ValueError:
                continue
            if wann < grenze:
                continue
            roh = api(a["archive_download_url"], roh=True)
            if not roh:
                continue
            with zipfile.ZipFile(io.BytesIO(roh)) as z:
                for name in z.namelist():
                    if not name.endswith(".csv"):
                        continue
                    text = z.read(name).decode("utf-8", "replace")
                    for zeile in csv.DictReader(io.StringIO(text)):
                        schluessel = (zeile.get("run_id", ""), zeile.get("agent", ""))
                        if schluessel in bekannt:
                            continue
                        bekannt.add(schluessel)
                        neu.append({s: zeile.get(s, "") for s in SPALTEN})
        seite += 1

    for zeile in sorted(neu, key=lambda z: (z["datum"], z["lauf"], z["agent"])):
        schreiben(args.out, zeile)
    print(f"{len(neu)} neue Zeilen → {args.out}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="befehl", required=True)

    l = sub.add_parser("lauf", help="einen Agentenlauf als CSV-Zeile ablegen")
    l.add_argument("--agent", required=True)
    l.add_argument("--lauf", default="")
    l.add_argument("--modell", default="")
    l.add_argument("--execution", default="", help="execution_file von claude-code-action")
    l.add_argument("--telemetrie", default="", help="Telemetriedatei der Gemini-CLI")
    l.add_argument("--dauer", default="", help="Laufzeit in Sekunden, falls bekannt")
    l.add_argument("--out", default="kosten-lauf.csv")
    l.set_defaults(func=lauf)

    b = sub.add_parser("bericht", help="nach Monat, Lauf und Agent auszählen")
    b.add_argument("csv", nargs="?", default="metriken/laeufe.csv")
    b.set_defaults(func=bericht)

    sa = sub.add_parser("sammeln", help="kosten-Artefakte der letzten Tage zusammenführen")
    sa.add_argument("--tage", type=int, default=8)
    sa.add_argument("--out", default="metriken/laeufe.csv")
    sa.set_defaults(func=sammeln)

    a = sub.add_parser("anthropic", help="Nutzung und Kosten aus der Admin-API")
    a.add_argument("--tage", type=int, default=31)
    a.add_argument("--nutzung-out", default="metriken/anthropic-nutzung.csv")
    a.add_argument("--kosten-out", default="metriken/anthropic-kosten.csv")
    a.set_defaults(func=anthropic)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
