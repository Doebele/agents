#!/usr/bin/env python3
"""Prueft jede URL in content/*.json und schreibt linkcheck-report.md.

Der Lauf ist Input fuer den Pflege-Agenten, kein Gate: das Skript schreibt
immer Exit 0 (ausser es crascht), der Agent bewertet das Ergebnis. Ein 403
einer bot-geschuetzten Seite ist z.B. kein toter Link.

Sicherheit: nur http/https, und vor dem Zugriff werden Namen und IPs auf
localhost/privat/reserviert geprueft — Daten aus den JSONs koennen sonst als
SSRF-Sprungbrett herhalten.
"""
import concurrent.futures
import datetime
import ipaddress
import json
import pathlib
import socket
import sys
import urllib.request
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
REPORT = ROOT / "linkcheck-report.md"
TIMEOUT = 10
WORKERS = 12


def urls_from_content():
    """Jede Zeichenkette, die als ganze ein http(s)-URL ist, mit Herkunft."""
    found = {}
    for path in sorted(CONTENT.glob("*.json")):
        def walk(o, trail):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(v, f"{trail}.{k}" if trail else k)
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, f"{trail}[{i}]")
            elif isinstance(o, str) and o.startswith(("http://", "https://")):
                found.setdefault(o, f"{path.name} {trail}")
        walk(json.loads(path.read_text(encoding="utf-8")), "")
    return found


def host_unsafe(hostname):
    """True, wenn der Host nicht angefasst wird: Name oder aufgeloeste IP."""
    if not hostname or hostname == "localhost" or hostname.endswith(".localhost"):
        return "localhost"
    try:
        addr = ipaddress.ip_address(hostname)
        if (addr.is_private or addr.is_loopback or addr.is_link_local
                or addr.is_reserved or addr.is_multicast or addr.is_unspecified):
            return f"reserved IP {addr}"
    except ValueError:
        pass  # kein Literal — Name unten aufloesen
    try:
        infos = socket.getaddrinfo(hostname, None)
    except OSError as e:
        return f"DNS: {e}"
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return f"resolves to {ip}"
    return None


def check(entry):
    url, origin = entry
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "agents-site-linkcheck/1.0"})
    try:
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return url, origin, r.status
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 406, 501):  # HEAD abgewiesen — es lebe GET
                req.method = "GET"
                req.headers["Range"] = "bytes=0-0"
                with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                    return url, origin, r.status
            return url, origin, e.code
    except urllib.error.HTTPError as e:
        return url, origin, e.code
    except Exception as e:  # Timeout, DNS, TLS — als Grund mitnehmen
        return url, origin, f"{type(e).__name__}: {e}"


def main():
    urls = urls_from_content()
    results, skipped = [], []
    for entry in urls.items():
        from urllib.parse import urlsplit
        parts = urlsplit(entry[0])
        if parts.scheme not in ("http", "https"):
            skipped.append((entry[0], entry[1], "scheme"))
            continue
        bad = host_unsafe(parts.hostname)
        if bad:
            skipped.append((entry[0], entry[1], bad))
            continue
        results.append(entry)

    outcomes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for out in pool.map(check, results):
            outcomes.append(out)

    ok = sorted(o for o in outcomes if isinstance(o[2], int) and o[2] < 400)
    bad = sorted(o for o in outcomes if o not in ok)

    lines = [
        "# Link-Check",
        "",
        f"{datetime.date.today().isoformat()} · {len(outcomes)} URLs geprüft · "
        f"**{len(bad)} auffällig** · {len(skipped)} übersprungen",
        "",
    ]
    if bad:
        lines += ["## Auffällig", ""]
        lines += [f"- `{u}` — {s} · {o}" for u, o, s in bad]
        lines += [""]
    if skipped:
        lines += ["## Übersprungen (Sperre oder Schema)", ""]
        lines += [f"- `{u}` — {r} · {o}" for u, o, r in skipped]
        lines += [""]
    lines += ["## In Ordnung", ""]
    lines += [f"- `{u}` ({s}) · {o}" for u, o, s in ok]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"{len(ok)} ok · {len(bad)} auffällig · {len(skipped)} übersprungen")
    print(f"Bericht: {REPORT}")
    for u, o, s in bad:
        print(f"  {s}  {u}  ({o})")


if __name__ == "__main__":
    sys.exit(main())
