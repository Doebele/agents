# Working in this repository

This is a reference work. Its whole value rests on the reader being able to
trust what it says. Everything below follows from that.

## The one rule that matters

**Never invent a fact, a version number, a price or a link.**

If you cannot find a source, say so and leave the field out. An omitted link
is fine — 8 fact sheets deliberately carry none, because concepts and
capabilities have no vendor page. A guessed link is not fine.

Every claim you change or add needs a source URL in the pull request body.
Not "according to the docs" — the address.

## Never edit `site/`

`site/index.html` and `site/index.de.html` are **build outputs**. The deploy
workflow verifies them against a fresh build before uploading. Editing them by
hand is silently undone by the next build.

Content lives in `content/*.json`, structure and logic in
`build/template.html`. After any change, build once to see the result and to
let the validation run:

```bash
python3 build/build.py
```

It refuses to write when something is inconsistent. Commit only the source
change. The pages get built again on merge, which is why two pull requests
can no longer merge into a page that matches neither.

## Both languages or neither

Translated values sit side by side as `{"de": …, "en": …}`. A new fact sheet
without an English blurb fails the build check. Write both, and write the
German as German — not as a translation of the English. The two versions are
equals, not original and copy.

Fields that are the same in both languages — `name`, `vendor`, `links`,
`accent`, `icon`, `open`, `free` — appear once, unqualified.

## Never push to `main`

Open a pull request. Always. The maintainer merges from a phone, and merging
deploys to the live site within a minute.

**One topic per pull request.** A single PR touching forty fact sheets does
not get read — it gets waved through. That defeats the point of having a
review step at all.

## What a fact sheet looks like

Copy the shape of an existing one. Required: `name`, `vendor`, `cat`,
`accent`, `blurb`, `tip`. Optional and only when true: `links`, `open`,
`free`, `plans`, `icon`, `aa`.

The `accent` follows the block: cyan 01, ember 02, lime 03, violet 04,
pink 05, sky 06, amber 07.

A new fact sheet also needs a chip in `content/modules.json`, or the build
check fails with "fact sheet no chip reaches".

## How to write

The audience is a beginner without a development background. Write for them.

Say what the thing does and when someone would reach for it instead of its
neighbour. Name the catch — what it costs, what it needs, where it disappoints.
A blurb that only praises is not describing, it is advertising.

Avoid the word "simply". Nothing here is simple to someone meeting it for the
first time.

Anything you mark as a recommendation is an opinion. The interface says so
out loud; your text should not pretend otherwise.

## The weekly runs

Four upkeep agents share the week — Claude on Mondays (pflege.yml), GLM by way
of Z.AI on Tuesdays (pflege-zai.yml), Gemini on Thursdays (pflege-gemini.yml),
Kimi on Saturdays (pflege-kimi.yml). Each picks exactly one topic per run,
working down the same short list: dead links first, then declared gaps, then
what is genuinely new. `build/linkcheck.py` writes linkcheck-report.md before
the Kimi and Z.AI runs — a 403 from a bot-walled site is not a dead link.

Prices are not on that list. They have a run of their own, twice a week, with
two agents reading every page instead of one; the next section says why.

Branch prefixes tell the proposals apart: `upkeep/<topic>`,
`upkeep-gemini/<topic>`, `upkeep-kimi/<topic>`, `upkeep-zai/<topic>`,
`kreuzpruefung/<topic>`.

## Prices are the first thing to rot

Everything else in a fact sheet ages slowly. A price can be wrong a week
after it was right, and a wrong price is worse than a missing one: the
reader plans around it.

So prices get checked on a rotation, not by whoever remembers.

### Three things change, not one

A price check that only compares numbers misses two thirds of what moves.

**The numbers.** The obvious part. Also watch for a tier that disappeared:
a free plan withdrawn is a bigger change for a beginner than a rate going up
by a dollar.

**The billing model.** A vendor that sold usage by the token adds a monthly
subscription. A subscription vendor opens an API. A coding subscription
starts travelling into third-party tools, which makes it worth mentioning
even though it arrives as a key. None of this changes a single digit, and
all of it changes which readers the entry suits. When the model moved,
`billing` moves with it in the same pull request.

**Whether it is still sold at all.** Products get discontinued, merged into
a bigger suite, or quietly closed to new customers. An entry describing a
plan nobody can buy any more is worse than one with an old number.

Set `billing` while you are there, even on entries that never had it. You
are already reading the page that answers it, and the gap under "What counts
as a declared gap" closes by itself that way.

A fact sheet whose price you verified carries the date you did it:

```json
"plans": { "de": "…", "en": "…" },
"plansChecked": "2026-08-21"
```

The date is the day you read the vendor's page, not the day the price
changed. Set it even when nothing changed — that is the point. An entry with
no `plansChecked` counts as never checked, which puts it first in line.
`build.py` refuses a date that is malformed, that lies in the future, or that
sits on an entry with no `plans`.

### Two read, one decides

One agent reading a pricing page is the thinnest point in the whole routine:
nobody checks it, and the mistake it makes is exactly the mistake a reader
plans around. So prices no longer travel with the weekly list. They have a run
of their own, `.github/workflows/kreuzpruefung.yml`, Mondays and Thursdays.

Twenty fact sheets per run, oldest `plansChecked` first, picked by a script so
that both researchers get the same list:

```bash
python3 build/kreuzpruefung.py auftrag --anzahl 20
```

Gemini and GLM then read the same vendor pages independently and write what
they read into a fixed schema: amount, currency, unit, billing, free tier,
whether it is still on sale, and the URL they read it on. Neither of them sees
the catalogue's current values first — whoever reads the old price confirms
it. Neither may commit or open anything; a finding file is all they produce.

`build/kreuzpruefung.py vergleich` holds the two against each other before any
model sees them and marks every entry einig, uneinig, einseitig or leer. It
compares the numbers, not the prose: how someone labels a tier is taste,
what it costs is not.

Claude decides from that table, and the rules are the point of the whole
arrangement:

- **einig** — take it, but fetch the source once yourself. Two models can read
  the same outdated page.
- **uneinig** — read the vendor's page and decide. Why, goes in the pull request.
- **einseitig** — one finding is not a confirmation. Treat it as unchecked and
  look it up.
- **leer** — change nothing, and leave `plansChecked` alone so the entry stays
  at the front of the queue.

Where nothing can be sourced, the field stays out and `plansChecked` stays
unset. A press release or a comparison site is not a source. Where a vendor no
longer publishes a price, say so in the entry rather than keeping the old
number alive.

Set `plansChecked` on every entry that was actually read, including the many
where nothing had moved. Leaving their date old sends the next run straight
back to the same page.

Twenty in one pull request is more than the ten a single agent may take
elsewhere, and that is deliberate: every value in it was read twice, and the
comparison table makes the review scannable in a way twenty prose diffs are
not.

The pull request carries one more line per fact sheet:

```
BILANZ 2026-08-27 Hetzner gemini=richtig zai=daneben
```

Nobody needs those today. In two months they answer a question no comparison
table can: which model actually reads a pricing page carefully.

## Two dates, and neither is called "last updated"

A fact sheet carries two freshness dates, and they mean different things. Merged
into one they would mean neither.

`plansChecked` is set by hand and says when someone read the vendor's pricing
page. The section above covers it.

The other one nobody sets. `build/stand.py` derives it from the git history:
walk the commits that touched `content/steckbrief.json`, compare each entry's
*parsed* value against the previous commit, and the newest commit where it
differs is that entry's date. Because the comparison runs on the value and not
on the text, reformatting the file moves no date, and a change to one fact
sheet moves only its own. `build.py` hangs the result on each entry as `stand`
and the drawer prints both:

    Eintrag geändert 21.08.2026 · Preis geprüft 14.08.2026

Do not add a `stand` field to the JSON. The point of deriving it is that no
one has to remember it, no one can forget it, and no agent can set it to
something flattering.

It needs the full history. The deploy checkout therefore carries
`fetch-depth: 0`; on a shallow clone `stand.py` returns nothing at all rather
than dating every untouched entry to the graft commit, and the page then shows
no date instead of a wrong one.

The same list is a queue. The price rotation is ordered by `plansChecked`;
what has gone longest without any attention is ordered by this:

```bash
python3 build/stand.py
```

## The coding-agent benchmark rots the same way

Harness sheets can carry an `aaAgent` block: the Artificial Analysis coding
agent measurements — index, average wall time and average cost per task —
one row per measured model configuration, styled like the model tiles.

```json
"aaAgent": { "url": "https://artificialanalysis.ai/agents/coding-agents",
  "checked": "2026-08-26",
  "rows": [ { "model": "…", "index": { "v": "0.68", "rank": "#1/9" },
             "time": { "v": "23.7 min", "rank": "#7/9" },
             "cost": { "v": "$8.17", "rank": "#8/9" } } ] }
```

The source is the AA coding-agents page; the index is a 0–1 composite of
three benchmarks, and rank 1 is best in all three columns. These numbers
move with every AA re-run, so they rotate like prices: read the page,
refresh values and ranks, and bump `checked` even when nothing moved. The
table also grows new agents and model configurations — when one appears
that this catalogue carries, add its row; when AA drops one, remove it.

## What counts as a declared gap

Item three of that list means two places, not one.

`content/arbeitsarten.json` marks wizard stations with a `luecke` field: a
tool the catalogue does not yet carry. Those are visible to readers. Closing
one means adding the fact sheet and assigning it, then removing the field.

The section below declares gaps in the data itself. Nobody sees them from
the outside, and they do not close on their own.

### `billing` is missing on most fact sheets that have prices

The field says how a thing is paid for: `["abo"]`, `["api"]`, or both. A
subscription buys a quota. An API key pays per use. Some vendors sell both,
and a coding subscription that travels into third-party tools is an `abo`
even though it arrives as a key.

Count what is left before you start:

```bash
python3 - <<'EOF'
import json
d = json.load(open("content/steckbrief.json"))
offen = [k for k, v in d.items() if v.get("plans") and "billing" not in v]
print(len(offen), "ohne billing:", ", ".join(sorted(offen)))
EOF
```

The price rotation above also fills this field whenever it visits an entry,
so the backlog shrinks on its own. Taking it as a topic of its own only
makes sense while that backlog is large.

Take at most ten per pull request and keep them in one block, so the review
stays readable. For every entry name the vendor page you read. Where the
page does not say, leave the field out and list which ones you skipped. A
guessed billing type is a guessed fact.

Whenever a run touches **marketing topics** — a new fact sheet, a wizard
station, a gap to fill — check Corey Haines' collection first and take
from there: https://github.com/coreyhaines31/marketingskills (cro and
customer-research already came from it). For skills in general, beyond
the catalogue: https://www.skills.sh.

## On demand

Beyond the schedule, the agents take orders three ways: a mention in an
issue or comment, the focus field of a manual run (workflow_dispatch), and
a Telegram message routed through telegram/ into the Kimi run
(repository_dispatch). An ordered task overrides the topic list — but stays
one topic per pull request.

Each agent listens for its own name, and only from the repository owner:

| Mention | Reaches | Runs |
|---|---|---|
| `@claude` | Claude | zuruf.yml |
| `@gemini` | Gemini | pflege-gemini.yml |
| `@zai` | GLM by way of Z.AI | pflege-zai.yml |

Naming two in one issue starts two runs, which is occasionally what you
want and usually not. Whoever is addressed answers in the thread when it is
done — an issue left unanswered is indistinguishable from a broken agent,
and that mistake has already cost four days here.

Kimi has no mention of its own: it takes orders through Telegram.

## "As of August 2026"

That line is a maintenance promise, not a timestamp. It is the reason this
repository has a weekly job. Do not change it to a later date unless the
whole catalogue has actually been reviewed.
