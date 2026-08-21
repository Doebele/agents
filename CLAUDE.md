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

Three upkeep agents share the week — Claude on Mondays (pflege.yml), Gemini
on Thursdays (pflege-gemini.yml), Kimi on Saturdays (pflege-kimi.yml). Each
picks exactly one topic per run, working down the same short list: dead links
first, then stale prices, then declared gaps, then what is genuinely new.
`build/linkcheck.py` writes linkcheck-report.md before the Kimi run — a 403
from a bot-walled site is not a dead link.

Branch prefixes tell the proposals apart: `upkeep/<topic>`,
`upkeep-gemini/<topic>`, `upkeep-kimi/<topic>`.

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

Which ones to take, oldest first:

```bash
python3 - <<'EOF'
import json
d = json.load(open("content/steckbrief.json"))
reihe = sorted(((v.get("plansChecked", ""), k) for k, v in d.items() if v.get("plans")))
for stand, k in reihe[:15]:
    print(f"{stand or 'nie':>10}  {k}")
EOF
```

Ten per pull request at most, and read the vendor's own pricing page for each
one. A press release or a comparison site is not the source. Where a vendor
no longer publishes a price, say so in the entry rather than keeping the old
number alive.

Set `plansChecked` on every entry you looked at, including the ones where
nothing had moved. Those are the majority, and leaving their date old would
send the next run straight back to the same page.

This is item two of the weekly list, and it is the item most likely to be
worth doing. Do not skip it because nothing looks obviously broken. A stale
price never looks broken.

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
