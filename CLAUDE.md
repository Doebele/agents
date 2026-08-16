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

## The weekly run

A scheduled agent works through this file top to bottom. Its input, in order:

1. `linkcheck-report.md`, written by `build/linkcheck.py` just before the run —
   every link marked broken there gets re-checked by hand before anything
   changes; a 403 from a bot-walled site is not a dead link.
2. A rotation slice: at most 15 fact sheets per run, chosen deterministically —
   keys of `content/steckbrief.json` sorted alphabetically, slice of 15
   starting at `(ISO week × 15) mod total`. Over the year, every sheet comes
   up several times.
3. Anything explicitly ordered — an issue, a manual dispatch task, a Telegram
   message routed through `telegram/`.

Branch naming: `agent/<yyyy-mm-dd>-<short-topic>`. An ordered task is not
bound to the 15-sheet limit, but stays one topic per pull request. When the
run was triggered by an issue, comment the pull request link back on it.

## "As of August 2026"

That line is a maintenance promise, not a timestamp. It is the reason this
repository has a weekly job. Do not change it to a later date unless the
whole catalogue has actually been reviewed.
