"""Wochenbericht: was die Agenten in den letzten sieben Tagen getan haben.

Laeuft sonntags am Ende von kosten.yml und landet als Issue im Repository.
GitHub schickt dem Maintainer dazu eine Mail, wenn seine Benachrichtigungen
fuer das Repository an sind; ein eigener Mailzugang ist nicht noetig.

    python3 build/wochenbericht.py --kosten metriken/laeufe.csv --out bericht.md
    python3 build/wochenbericht.py --selbsttest

Drei Teile: welche Ablaeufe wie oft gelaufen und wie ausgegangen sind, welche
Pull Requests entstanden und gemergt wurden, und der Aufwand aus der
Kostentabelle. Was die GitHub-API nicht liefert, fehlt im Bericht und wird
nicht geschaetzt.
"""

import argparse
import csv
import datetime
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

# Ablaeufe, die keine Agentenarbeit sind und den Bericht nur fuellen wuerden.
UNWICHTIG = {"Build and deploy", "Taegliche Pflege im Wechsel"}


def api(pfad, token, repo):
    url = pfad if pfad.startswith("http") else f"https://api.github.com/repos/{repo}/{pfad}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def laeufe_holen(token, repo, ab):
    """Alle Workflow-Laeufe seit `ab` (Datum), hoechstens zehn Seiten."""
    alle = []
    for seite in range(1, 11):
        d = api(f"actions/runs?created=%3E%3D{ab.isoformat()}&per_page=100&page={seite}", token, repo)
        runs = d.get("workflow_runs", [])
        alle += runs
        if len(runs) < 100:
            break
    return alle


def prs_holen(token, repo, ab):
    """Pull Requests, die seit `ab` geoeffnet oder gemergt wurden."""
    treffer = []
    for seite in range(1, 6):
        d = api(f"pulls?state=all&sort=updated&direction=desc&per_page=100&page={seite}", token, repo)
        for p in d:
            erstellt = p["created_at"][:10]
            gemergt = (p.get("merged_at") or "")[:10]
            if erstellt >= ab.isoformat() or gemergt >= ab.isoformat():
                treffer.append(p)
        if len(d) < 100 or (d and d[-1]["updated_at"][:10] < ab.isoformat()):
            break
    return treffer


def ohne_erwaehnung(text):
    """Ein @ im Bericht soll niemanden anpingen und keinen Agenten rufen."""
    return str(text).replace("@", "@​")


def abschnitt_laeufe(runs):
    zaehler = {}
    gescheitert = []
    for r in runs:
        name = r.get("name") or "?"
        if name in UNWICHTIG or r.get("conclusion") in (None, "skipped"):
            continue
        z = zaehler.setdefault(name, {"success": 0, "failure": 0, "sonst": 0})
        ergebnis = r.get("conclusion")
        z[ergebnis if ergebnis in ("success", "failure") else "sonst"] += 1
        if ergebnis == "failure":
            gescheitert.append(r)
    zeilen = ["## Läufe", ""]
    if not zaehler:
        return zeilen + ["Keine Agentenläufe in diesem Zeitraum.", ""]
    zeilen += ["| Ablauf | erfolgreich | gescheitert | abgebrochen/sonst |", "|---|---|---|---|"]
    for name in sorted(zaehler):
        z = zaehler[name]
        zeilen.append(f"| {ohne_erwaehnung(name)} | {z['success']} | {z['failure'] or '—'} | {z['sonst'] or '—'} |")
    zeilen.append("")
    if gescheitert:
        zeilen += ["**Gescheitert:**", ""]
        for r in sorted(gescheitert, key=lambda r: r.get("created_at", "")):
            zeilen.append(f"- {r.get('created_at', '')[:10]} · {ohne_erwaehnung(r.get('name'))} · "
                          f"{ohne_erwaehnung(r.get('display_title', ''))[:70]} · [Log]({r.get('html_url')})")
        zeilen.append("")
    return zeilen


def abschnitt_prs(prs, ab):
    neu = [p for p in prs if p["created_at"][:10] >= ab.isoformat()]
    gemergt = [p for p in prs if (p.get("merged_at") or "")[:10] >= ab.isoformat()]
    offen = [p for p in prs if p.get("state") == "open"]
    zeilen = ["## Pull Requests", "",
              f"{len(neu)} geöffnet · {len(gemergt)} gemergt · {len(offen)} davon noch offen", ""]
    if gemergt:
        zeilen += ["**Gemergt:**", ""]
        for p in sorted(gemergt, key=lambda p: p["merged_at"]):
            zeilen.append(f"- #{p['number']} {ohne_erwaehnung(p['title'])} "
                          f"({ohne_erwaehnung(p['user']['login'])})")
        zeilen.append("")
    if offen:
        zeilen += ["**Wartet auf dich:**", ""]
        for p in sorted(offen, key=lambda p: p["number"]):
            zeilen.append(f"- #{p['number']} {ohne_erwaehnung(p['title'])} "
                          f"({ohne_erwaehnung(p['user']['login'])})")
        zeilen.append("")
    return zeilen


def abschnitt_aufwand(pfad, ab):
    zeilen = ["## Aufwand", ""]
    p = pathlib.Path(pfad) if pfad else None
    if not p or not p.exists():
        return zeilen + ["Keine Kostentabelle gefunden.", ""]
    gruppen = {}
    for z in csv.DictReader(p.open(encoding="utf-8")):
        if (z.get("datum") or "") < ab.isoformat():
            continue
        g = gruppen.setdefault((z.get("lauf", ""), z.get("agent", "")),
                               {"n": 0, "usd": 0.0, "dauer": 0.0, "mit_usd": 0, "mit_dauer": 0})
        g["n"] += 1
        for feld, ziel, zaehl in (("kosten_usd", "usd", "mit_usd"), ("dauer_s", "dauer", "mit_dauer")):
            try:
                wert = float(z.get(feld) or "")
            except ValueError:
                continue
            g[ziel] += wert
            g[zaehl] += 1
    if not gruppen:
        return zeilen + ["Keine erfassten Läufe in diesem Zeitraum.", ""]
    zeilen += ["| Ablauf | Agent | Läufe | USD (Schätzung) | ø Dauer |", "|---|---|---|---|---|"]
    for (lauf, agent), g in sorted(gruppen.items()):
        usd = f"{g['usd']:.2f}" if g["mit_usd"] else "—"
        dauer = f"{g['dauer'] / g['mit_dauer'] / 60:.0f} min" if g["mit_dauer"] else "—"
        zeilen.append(f"| {ohne_erwaehnung(lauf)} | {agent} | {g['n']} | {usd} | {dauer} |")
    zeilen += ["", "USD ist die Schätzung des Clients zu API-Preisen. Bei `claude-abo` wurde dafür "
               "nichts abgerechnet, bei Kimi und GLM gibt es keine Zahl, nur die Laufzeit.", ""]
    return zeilen


def bericht(runs, prs, kosten, heute, tage):
    ab = heute - datetime.timedelta(days=tage)
    kw = heute.isocalendar()
    kopf = [f"# Wochenbericht KW {kw[1]}/{kw[0]}", "",
            f"Zeitraum: {ab.strftime('%d.%m.')} bis {heute.strftime('%d.%m.%Y')}", ""]
    return "\n".join(kopf + abschnitt_laeufe(runs) + abschnitt_prs(prs, ab)
                     + abschnitt_aufwand(kosten, ab)
                     + ["---", "_Automatisch geschrieben von `build/wochenbericht.py`._", ""])


def selbsttest():
    fehler = 0

    def pruefe(name, bedingung):
        nonlocal fehler
        fehler += not bedingung
        print(f"{'ok ' if bedingung else 'FEHLER'}  {name}")

    heute = datetime.date(2026, 10, 11)
    runs = [
        {"name": "Weekly upkeep", "conclusion": "success", "created_at": "2026-10-09T06:30:00Z",
         "display_title": "Weekly upkeep", "html_url": "u1"},
        {"name": "Weekly upkeep (Kimi)", "conclusion": "failure", "created_at": "2026-10-10T06:30:00Z",
         "display_title": "@claude kaputt", "html_url": "u2"},
        {"name": "Build and deploy", "conclusion": "success", "created_at": "2026-10-10T07:00:00Z"},
        {"name": "Claude on request", "conclusion": "skipped", "created_at": "2026-10-10T07:00:00Z"},
    ]
    prs = [
        {"number": 160, "title": "Neu", "user": {"login": "claude[bot]"}, "state": "open",
         "created_at": "2026-10-09T08:00:00Z", "merged_at": None},
        {"number": 158, "title": "Alt, gemergt", "user": {"login": "z-ai-upkeep[bot]"}, "state": "closed",
         "created_at": "2026-10-01T08:00:00Z", "merged_at": "2026-10-06T08:00:00Z"},
    ]
    pfad = pathlib.Path(os.environ.get("TMPDIR", "/tmp")) / "wochenbericht-test.csv"
    pfad.write_text("datum,lauf,agent,kosten_usd,dauer_s\n"
                    "2026-10-09,Weekly upkeep,claude-abo,0.57,600\n"
                    "2026-10-10,Weekly upkeep (Kimi),kimi,,420\n"
                    "2026-09-20,Weekly upkeep,claude,9.99,600\n", encoding="utf-8")
    t = bericht(runs, prs, str(pfad), heute, 7)
    pruefe("Kopf nennt KW und Zeitraum", "KW 41/2026" in t and "04.10. bis 11.10.2026" in t)
    pruefe("Deploy und uebersprungene Laeufe fehlen", "Build and deploy" not in t and "Claude on request" not in t)
    pruefe("gescheiterter Lauf mit Log", "Weekly upkeep (Kimi) | 0 | 1" in t and "[Log](u2)" in t)
    pruefe("niemand wird angepingt", "@claude" not in t)
    pruefe("PR-Zaehlung", "1 geöffnet · 1 gemergt · 1 davon noch offen" in t)
    pruefe("offener PR steht unter 'Wartet auf dich'", "**Wartet auf dich:**\n\n- #160" in t)
    pruefe("Aufwand nur aus dem Zeitraum", "0.57" in t and "9.99" not in t)
    pruefe("fehlende Zahl bleibt leer", "| Weekly upkeep (Kimi) | kimi | 1 | — | 7 min |" in t)
    print(f"\n{'alles in Ordnung' if not fehler else f'{fehler} Fehler'}")
    return 1 if fehler else 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--tage", type=int, default=7)
    p.add_argument("--kosten", default="metriken/laeufe.csv")
    p.add_argument("--out", default="bericht.md")
    p.add_argument("--selbsttest", action="store_true")
    args = p.parse_args()
    if args.selbsttest:
        return selbsttest()

    token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repo:
        print("GITHUB_TOKEN oder GITHUB_REPOSITORY fehlt.", file=sys.stderr)
        return 1
    heute = datetime.date.today()
    ab = heute - datetime.timedelta(days=args.tage)
    try:
        runs = laeufe_holen(token, repo, ab)
        prs = prs_holen(token, repo, ab)
    except urllib.error.HTTPError as e:
        print(f"GitHub-API: HTTP {e.code}", file=sys.stderr)
        return 1
    text = bericht(runs, prs, args.kosten, heute, args.tage)
    pathlib.Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
