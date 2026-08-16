// Telegram ↔ GitHub für den Pflege-Agenten.
//
// Zwei Türen, beide mit Geheimnis im Pfad:
//   POST /tg/<TG_SECRET>   Telegram-Webhook: Textnachricht = Auftrag,
//                          landet als repository_dispatch beim Agenten.
//   POST /gh/<GH_SECRET>   GitHub-Webhook: neuer agent/*-Pull Request
//                          bekommt Freigabe-Knöpfe in den Chat.
//
// Einrichtung Schritt für Schritt: README.md nebenan.

const TG_API = "https://api.telegram.org/bot";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/healthz") {
      return new Response("ok");
    }

    // --- Telegram ------------------------------------------------------
    if (request.method === "POST" && url.pathname === `/tg/${env.TG_SECRET}`) {
      return telegram(request, env);
    }

    // --- GitHub --------------------------------------------------------
    if (request.method === "POST" && url.pathname === `/gh/${env.GH_WEBHOOK_SECRET}`) {
      if (!(await signed(request, env))) return new Response("bad signature", { status: 403 });
      return github(request, env);
    }

    return new Response("not found", { status: 404 });
  },
};

/* Telegram wiederholt Updates, solange kein 200 kommt — auch bei
   ignorierten Nachrichten also immer 200 sagen. */
async function telegram(request, env) {
  let update;
  try { update = await request.json(); } catch { return ok(); }

  try {
    if (update.callback_query) return await onCallback(update.callback_query, env);
    const msg = update.message;
    if (msg && msg.text && String(msg.chat.id) === String(env.TELEGRAM_CHAT_ID)) {
      return await onMessage(msg, env);
    }
  } catch (e) {
    await tg(env, "sendMessage", { chat_id: env.TELEGRAM_CHAT_ID,
                                   text: "Fehler: " + e.message });
  }
  return ok();
}

async function onMessage(msg, env) {
  const text = msg.text.trim();
  if (text === "/start" || text === "/help") {
    await tg(env, "sendMessage", {
      chat_id: env.TELEGRAM_CHAT_ID,
      text: "Schreib mir einfach, was der Agent tun soll — zum Beispiel:\n"
          + "„Füge Tool X im Baustein Tools hinzu“\n"
          + "„Prüf die Preise bei den Modell-Anbietern“\n\n"
          + "Jede Nachricht startet einen Lauf. Das Ergebnis kommt als "
          + "Pull Request mit Freigabe-Knöpfen hierher."
    });
    return ok();
  }

  const r = await gh(env, "POST", "/repos/" + env.GH_REPO + "/dispatches", {
    event_type: "telegram",
    client_payload: { task: text, from: msg.from?.username || msg.from?.first_name || "?" },
  });
  if (r.status !== 204) {
    await tg(env, "sendMessage", { chat_id: env.TELEGRAM_CHAT_ID,
      text: "GitHub hat den Auftrag abgelehnt (HTTP " + r.status + "). "
          + "Prüf GH_TOKEN und repository_dispatch-Rechte." });
    return ok();
  }
  await tg(env, "sendMessage", {
    chat_id: env.TELEGRAM_CHAT_ID,
    text: "Auftrag eingereicht — der Agent läuft gleich los. "
        + "Sein Pull Request kommt hierher, sobald er fertig ist." });
  return ok();
}

async function onCallback(q, env) {
  const [action, n] = (q.data || "").split(":");
  let outcome;
  if (action === "merge") {
    const r = await gh(env, "PUT", `/repos/${env.GH_REPO}/pulls/${n}/merge`,
                       { merge_method: "squash" });
    outcome = r.ok ? `✅ PR #${n} gemergt — Deploy zu Strato läuft.` : `Merge fehlgeschlagen (HTTP ${r.status}).`;
  } else if (action === "close") {
    const r = await gh(env, "PATCH", `/repos/${env.GH_REPO}/pulls/${n}`,
                       { state: "closed" });
    outcome = r.ok ? `❌ PR #${n} abgelehnt und geschlossen.` : `Schließen fehlgeschlagen (HTTP ${r.status}).`;
  } else {
    outcome = "Unbekannter Knopf.";
  }
  await tg(env, "answerCallbackQuery", { callback_query_id: q.id });
  if (q.message) {
    await tg(env, "editMessageText", {
      chat_id: q.message.chat.id, message_id: q.message.message_id, text: outcome });
  }
  return ok();
}

async function github(request, env) {
  const body = await request.json();
  if (request.headers.get("x-github-event") !== "pull_request"
      || body.action !== "opened"
      || !String(body.pull_request?.head?.ref || "").startsWith("agent/")) {
    return ok();   // nur Agenten-PRs fragen um Freigabe
  }
  const pr = body.pull_request;
  await tg(env, "sendMessage", {
    chat_id: env.TELEGRAM_CHAT_ID,
    text: `🤖 Pull Request #${pr.number}: ${pr.title}\n${pr.html_url}\n\n${pr.body || ""}`.slice(0, 4000),
    reply_markup: { inline_keyboard: [[
      { text: "✅ Freigeben", callback_data: `merge:${pr.number}` },
      { text: "❌ Ablehnen", callback_data: `close:${pr.number}` },
    ]] },
  });
  return ok();
}

/* --- Hilfsfunktionen --------------------------------------------------- */

async function tg(env, method, payload) {
  return fetch(`${TG_API}${env.TELEGRAM_BOT_TOKEN}/${method}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
}

async function gh(env, method, path, payload) {
  return fetch("https://api.github.com" + path, {
    method,
    headers: {
      "authorization": `Bearer ${env.GH_TOKEN}`,
      "accept": "application/vnd.github+json",
      "content-type": "application/json",
      "user-agent": "agents-telegram-worker",
    },
    body: payload ? JSON.stringify(payload) : undefined,
  });
}

async function signed(request, env) {
  const got = request.headers.get("x-hub-signature-256") || "";
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(env.GH_WEBHOOK_SECRET),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = await crypto.subtle.sign("HMAC", key, await request.clone().arrayBuffer());
  const want = "sha256=" + [...new Uint8Array(mac)]
    .map(b => b.toString(16).padStart(2, "0")).join("");
  // timingSafeEqual gibt es in Workern nicht — Längenvergleich vorneweg
  return got.length === want.length && got === want;
}

function ok() { return new Response("ok"); }
