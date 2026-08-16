# Telegram-Anbindung des Pflege-Agenten

Ein kleiner Cloudflare Worker (kostenloses Kontingent reicht) verbindet deinen
Telegram-Chat mit dem Agenten-Workflow in GitHub:

```
Telegram-Nachricht  ──▶  Worker  ──▶  repository_dispatch  ──▶  Agent-Workflow
Agent-PR geöffnet   ──▶  GitHub-Webhook  ──▶  Worker  ──▶  Chat mit
                                                              [✅ Freigeben] [❌ Ablehnen]
Knopf drücken       ──▶  Worker  ──▶  Merge/Close per GitHub-API
Merge               ──▶  Deploy-Workflow  ──▶  agents.medvesek.com
```

Ohne diesen Worker läuft alles genauso — nur eben ohne Telegram: Aufträge
dann per Issue oder direkt in GitHub unter *Actions → Agent → Run workflow*.

## Einrichtung (einmalig, ~15 Minuten)

### 1. Bot anlegen
Bei [@BotFather](https://t.me/BotFather) `/newbot`, Name frei, z.B.
`agents-medvesek-bot`. Das Token (`123456:ABC-…`) notieren.

### 2. Eigene Chat-ID ermitteln
Dem neuen Bot eine Nachricht schreiben (z.B. `/start`), dann:

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | grep -o '"chat":{"id":[0-9]*'
```

### 3. Worker deployen

```bash
npm install -g wrangler   # einmalig
cd telegram
wrangler login
wrangler deploy
wrangler secret put TELEGRAM_BOT_TOKEN    # Token aus Schritt 1
wrangler secret put TELEGRAM_CHAT_ID      # Zahl aus Schritt 2
wrangler secret put TG_SECRET             # zufälliger String: openssl rand -hex 16
wrangler secret put GH_TOKEN              # GitHub-PAT, siehe unten
wrangler secret put GH_WEBHOOK_SECRET     # zufälliger String: openssl rand -hex 16
```

`GH_TOKEN`: auf [github.com/settings/tokens](https://github.com/settings/tokens)
ein *fine-grained* Token für das Repo `Doebele/agents` mit
**Contents: Read and write** und **Pull requests: Read and write**
(für Merge/Close und repository_dispatch).

Die Worker-Adresse steht nach `wrangler deploy` in der Ausgabe —
im Folgenden `https://agents-telegram.<subdomain>.workers.dev`.

### 4. Telegram-Webhook setzen

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://agents-telegram.<subdomain>.workers.dev/tg/<TG_SECRET>"
```

### 5. GitHub-Webhook setzen
GitHub → *Doebele/agents → Settings → Webhooks → Add webhook*:

- **Payload URL:** `https://agents-telegram.<subdomain>.workers.dev/gh/<GH_WEBHOOK_SECRET>`
- **Content type:** `application/json`
- **Secret:** der Wert von `GH_WEBHOOK_SECRET`
- **Events:** *Let me select individual events* → **Pull requests**

### 6. Probieren
Dem Bot schreiben: „Prüf, ob alle Links auf der Seite noch leben."
Nach ein paar Minuten sollte der Chat den Pull Request des Agenten zeigen.

## Sicherheit

- Beide Webhook-Türen tragen ihr Geheimnis im Pfad; der GitHub-Weg ist
  zusätzlich HMAC-signiert (`X-Hub-Signature-256`).
- Der Bot reagiert nur auf `TELEGRAM_CHAT_ID` — fremde Chats werden ignoriert.
- Merge und Close laufen über einen Token, dem nur dieses eine Repo gehört.
- Der Worker hält keine Zustände — alles, was er weiß, steht in den Secrets.
