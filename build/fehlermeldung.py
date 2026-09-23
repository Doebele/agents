#!/usr/bin/env python3
"""Wenn ein Agentenlauf scheitert, der aus einem Issue kam: den Grund dorthin schreiben.

Ein unbeantwortetes Issue sieht aus wie ein kaputter Agent, und so ist es hier
mehrfach passiert. Am 23. September standen drei Auftraege gleichzeitig stumm
da: einer an Z.AI, der in der ersten Minute an Code 1113 starb, und zwei an
Claude, die nach neun Minuten in derselben Sekunde abbrachen. Keiner hat ein
Wort in seinen Thread geschrieben, weil der Agent vor dem Scheitern nicht mehr
dazu kam. Gemerkt hat man es nur daran, dass nichts passierte.

Dieses Skript laeuft als letzter Schritt, nur wenn der Lauf gescheitert ist
(`.github/actions/fehlermeldung`), und schreibt ins Issue:

  - in welchem Schritt es riss, mit Link direkt auf das Log dieses Jobs,
  - einen Grund, wenn ein Schritt einen hinterlassen hat ($RUNNER_TEMP/fehlergrund.txt),
  - bei Claude Turns, Kosten und die Rueckmeldung des Laufs aus dem execution_file,
  - einen Satz Klartext, wenn die Rueckmeldung zu einer bekannten Ursache passt.

Was in einem oeffentlichen Issue landet, wird vorher bereinigt: alles, was nach
Schluessel aussieht, faellt heraus, und ein @ bekommt ein unsichtbares Zeichen
dahinter, damit die Meldung niemanden anpingt und keinen Agenten neu startet.

Das Skript selbst scheitert nie laut. Der Lauf ist bereits rot; ein zweiter
Fehler obendrauf wuerde nur den ersten verdecken.

    python3 build/fehlermeldung.py --selbsttest
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

GRUND_DATEI = "fehlergrund.txt"

# Bekannte Ursachen: Muster in der Rueckmeldung → ein Satz Klartext. Bewusst
# wenige und eindeutige; lieber kein Hinweis als ein falscher.
HINWEISE = [
    (r"credit balance|balance is too low",
     "Das **API-Guthaben** des Anthropic-Kontos reicht nicht. Gemeint ist das "
     "Guthaben in der Console (platform.claude.com), nicht das in der Claude-App — "
     "das sind zwei getrennte Töpfe."),
    (r"\b1113\b|insufficient balance",
     "Z.AI nimmt die Anfrage nicht an: entweder ist das Guthaben leer, oder der "
     "Schlüssel gehört zum Coding-Abo und ging an den Endpunkt für Guthaben."),
    (r"rate[_ ]limit|overloaded",
     "Die API hat gedrosselt oder war überlastet. Ein späterer Versuch hilft meist."),
    (r"error_max_turns|max(imum)?[_ ]turns",
     "Die Obergrenze an Turns war erreicht, bevor der Auftrag fertig war."),
    (r"invalid x-api-key|authentication_error|invalid api key",
     "Der Schlüssel wird nicht angenommen — abgelaufen, widerrufen oder falsch hinterlegt."),
]

SCHLUESSEL = [
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\b[A-Za-z0-9+/_\-]{40,}={0,2}"),   # lange undurchsichtige Zeichenketten
]


def bereinige(text, laenge=600):
    """Fuer ein oeffentliches Issue: ohne Schluessel, ohne Pings, ohne Codeblock-Ausbruch."""
    t = str(text or "")
    for muster in SCHLUESSEL:
        t = muster.sub("[entfernt]", t)
    t = t.replace("```", "'''").replace("@", "@\u200b")
    t = t.strip()
    if len(t) > laenge:
        t = t[:laenge].rstrip() + " …"
    return t


def hinweis(*texte):
    alles = " ".join(str(t or "") for t in texte).lower()
    for muster, satz in HINWEISE:
        if re.search(muster, alles):
            return satz
    return ""


def ergebnis(pfad):
    """Das result-Objekt aus Claudes execution_file, oder {}."""
    if not pfad or not os.path.isfile(pfad):
        return {}
    try:
        roh = open(pfad, encoding="utf-8", errors="replace").read().strip()
    except OSError:
        return {}
    objekte = []
    try:
        d = json.loads(roh)
        objekte = d if isinstance(d, list) else [d]
    except ValueError:
        for zeile in roh.splitlines():
            try:
                objekte.append(json.loads(zeile))
            except ValueError:
                pass
    treffer = [o for o in objekte if isinstance(o, dict) and o.get("type") == "result"]
    return treffer[-1] if treffer else {}


def api(url, token, daten=None):
    kopf = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        kopf["Authorization"] = f"Bearer {token}"
    body = json.dumps(daten).encode() if daten is not None else None
    if body:
        kopf["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=kopf, method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8") or "{}")


def gescheiterter_schritt(basis, repo, lauf, versuch, token, job_schluessel):
    """(Schrittname, Job-URL) aus der Actions-API, soweit sie es schon weiss."""
    try:
        jobs = api(f"{basis}/repos/{repo}/actions/runs/{lauf}/attempts/{versuch}/jobs", token)
    except Exception as e:  # fehlende Berechtigung, Netz
        print(f"Jobs nicht lesbar: {e}", file=sys.stderr)
        return "", ""
    laufend = [j for j in jobs.get("jobs", []) if j.get("status") != "completed"]
    kandidaten = [j for j in laufend if j.get("name") == job_schluessel] or laufend
    for job in kandidaten:
        for schritt in job.get("steps", []):
            if schritt.get("conclusion") == "failure":
                return schritt.get("name", ""), job.get("html_url", "")
        if job.get("html_url"):
            return "", job["html_url"]
    return "", ""


def zahl_de(x, stellen=2):
    return f"{x:,.{stellen}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def verfasse(agent, schritt, log_url, grund, erg):
    """Der Kommentar selbst. Ohne Netz, damit er sich pruefen laesst."""
    zeilen = [f"**Der Lauf ist abgebrochen.** {agent} hat diesen Auftrag nicht zu Ende "
              "gebracht, ein Pull Request ist daraus nicht entstanden.", ""]
    zeilen.append(f"- Gescheitert im Schritt: `{bereinige(schritt, 120)}`" if schritt
                  else "- Gescheitert in einem Schritt, den die Actions-API nicht nennen konnte")
    if erg:
        teile = []
        if erg.get("num_turns") is not None:
            teile.append(f"{erg['num_turns']} Turns")
        if isinstance(erg.get("total_cost_usd"), (int, float)):
            teile.append(f"{zahl_de(erg['total_cost_usd'])} USD geschätzt")
        if erg.get("permission_denials_count"):
            teile.append(f"{erg['permission_denials_count']} verweigerte Werkzeugaufrufe")
        if erg.get("subtype") and erg.get("subtype") != "success":
            teile.append(f"Abschluss `{bereinige(erg['subtype'], 40)}`")
        if teile:
            zeilen.append("- " + " · ".join(teile))
    if log_url:
        zeilen.append(f"- [Log dieses Laufs]({log_url})")

    rueckmeldung = grund or (erg.get("result") if erg.get("is_error") else "")
    satz = hinweis(grund, erg.get("result"), erg.get("subtype"), schritt)
    if satz:
        zeilen += ["", satz]
    if rueckmeldung:
        zeilen += ["", "Rückmeldung des Laufs:", "", "```text", bereinige(rueckmeldung), "```"]

    zeilen += ["", "Der Auftrag bleibt offen. Ein neuer Kommentar mit der Erwähnung "
               "des Agenten startet ihn neu.", "", "---",
               "_Automatisch geschrieben von `.github/actions/fehlermeldung` — "
               "ein unbeantwortetes Issue sähe sonst aus wie ein kaputter Agent._"]
    return "\n".join(zeilen)


def main():
    try:
        ereignis = json.load(open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8"))
    except (KeyError, OSError, ValueError):
        print("Kein Ereignis lesbar — nichts zu melden.")
        return 0
    nummer = (ereignis.get("issue") or {}).get("number") or \
             (ereignis.get("pull_request") or {}).get("number")
    if not nummer:
        print("Der Lauf kam nicht aus einem Issue — niemand wartet auf eine Antwort.")
        return 0

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    basis = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    lauf = os.environ.get("GITHUB_RUN_ID", "")
    versuch = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    lesen = os.environ.get("GH_TOKEN_LESEN", "")
    schreiben = os.environ.get("GH_TOKEN_SCHREIBEN", "") or lesen

    schritt, job_url = gescheiterter_schritt(basis, repo, lauf, versuch, lesen,
                                             os.environ.get("GITHUB_JOB", ""))
    log_url = job_url or (f"{server}/{repo}/actions/runs/{lauf}" if lauf else "")

    grund = ""
    grund_pfad = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), GRUND_DATEI)
    if os.path.isfile(grund_pfad):
        grund = open(grund_pfad, encoding="utf-8", errors="replace").read()

    text = verfasse(os.environ.get("AGENT", "Der Agent"), schritt, log_url, grund,
                    ergebnis(os.environ.get("EXECUTION", "")))
    try:
        antwort = api(f"{basis}/repos/{repo}/issues/{nummer}/comments", schreiben, {"body": text})
        print(f"Gemeldet in #{nummer}: {antwort.get('html_url', '')}")
    except urllib.error.HTTPError as e:
        print(f"Kommentar nicht geschrieben: HTTP {e.code} {e.read()[:200]!r}", file=sys.stderr)
    except Exception as e:
        print(f"Kommentar nicht geschrieben: {e}", file=sys.stderr)
    return 0


def selbsttest():
    fehler = 0

    def pruefe(name, bedingung):
        nonlocal fehler
        fehler += not bedingung
        print(f"{'ok ' if bedingung else 'FEHLER'}  {name}")

    s = bereinige("key sk-ant-api03-abcdefghijklmnop und ghp_" + "a" * 36)
    pruefe("Anthropic- und GitHub-Schluessel fallen heraus", "sk-ant" not in s and "ghp_" not in s)
    pruefe("Erwaehnung pingt niemanden an", "@claude" not in bereinige("frag @claude"))
    pruefe("kein Ausbruch aus dem Codeblock", "```" not in bereinige("a ``` b"))
    pruefe("lange Rueckmeldung wird gekuerzt", len(bereinige("x " * 800)) <= 602)

    pruefe("Guthaben der Console wird erkannt",
           "API-Guthaben" in hinweis("Your credit balance is too low to access the Anthropic API"))
    pruefe("Z.AI-Code 1113 wird erkannt",
           "Z.AI" in hinweis('{"error":{"code":"1113"}}'))
    pruefe("Zahl 11130 ist nicht Code 1113", hinweis("Token 11130") == "")
    pruefe("unbekannte Ursache ergibt keinen Hinweis", hinweis("irgendwas") == "")

    erg = {"type": "result", "subtype": "success", "is_error": True, "num_turns": 80,
           "total_cost_usd": 3.6938, "permission_denials_count": 3,
           "result": "Your credit balance is too low to access the Anthropic API."}
    t = verfasse("Claude", "Run anthropics/claude-code-action@v1",
                 "https://github.com/x/y/actions/runs/1/job/2", "", erg)
    pruefe("Kommentar nennt Schritt, Turns, Kosten und Log",
           "claude-code-action" in t and "80 Turns" in t and "3,69 USD" in t and "/job/2" in t)
    pruefe("Kommentar erklaert die Ursache und zitiert sie",
           "API-Guthaben" in t and "credit balance is too low" in t)
    pruefe("Kommentar enthaelt keine ausloesende Erwaehnung",
           not re.search(r"@(claude|zai|gemini|kimi)\b", t))

    t = verfasse("Z.AI", "", "", "", {})
    pruefe("ohne Schritt und Log bleibt der Kommentar lesbar",
           "nicht nennen konnte" in t and "Log dieses Laufs" not in t)

    print(f"\n{'alles in Ordnung' if not fehler else f'{fehler} Fehler'}")
    return 1 if fehler else 0


if __name__ == "__main__":
    if "--selbsttest" in sys.argv:
        sys.exit(selbsttest())
    try:
        sys.exit(main())
    except Exception as e:  # nie laut scheitern, siehe oben
        print(f"Fehlermeldung nicht moeglich: {e}", file=sys.stderr)
        sys.exit(0)
