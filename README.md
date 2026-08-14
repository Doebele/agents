# AGENT // SYSTEM

An interactive field guide to the AI agent landscape — written for beginners,
bilingual, as of August 2026.

Two deliverables from one source:

| | |
|---|---|
| **Website** | `site/index.html` (English, default) · `site/index.de.html` (German) — a single file each, openable by double-click |
| **Deck** | `KI-Agenten-Landschaft.pptx` — 22 slides, 16:9 |

## What is in it

Seven building blocks that make up every AI agent, with **109 fact sheets** on
the models, tools and services behind them. Plus a wizard that assembles a
setup from the kind of work you do — including the prerequisites that have to
exist first, and a Markdown sheet you hand to your own agent to do the setup.

## Build

The two HTML files are **build outputs**. Editing them directly loses the
change on the next build.

```bash
python3 build/build.py            # builds both language files
python3 build/build.py --check    # builds only, reports differences
```

No dependencies beyond Python 3. Node was needed once, for `build/extract.py`.

## Layout

```
content/     the content — fact sheets, blocks, glossary, kinds of work
build/       template and build script
site/        the built pages
media/       images for the deck
DESIGN.md    the design system, with named rules
PRODUCT.md   purpose, audience, principles
```

## Bilingual by construction

Translated values sit **side by side** in `content/` as `{"de": …, "en": …}`.
Anything identical in both languages — names, links, colours — appears once.
A missing translation is therefore visible in its neighbouring key, and the
build check catches it as well.

## What the check catches

It runs before anything is written and stops the build rather than shipping:

- a missing or empty translation
- a chip with no fact sheet behind it
- a fact sheet no chip reaches
- a template marker with no content, and the reverse

## Principles

No invented facts. When a link is unknown it is omitted rather than guessed —
which is why concepts and capabilities carry no vendor links. Anything marked
as a suggestion is an opinion, not a finding, and the interface says so.

"As of August 2026" is a maintenance promise, not a timestamp.

## Building the deck

```bash
python3 build_pptx.py      # renders the PPTX from media/
python3 verify_pptx.py     # checks it against the acceptance criteria
```

## Deployment

`site/` is uploaded to shared hosting by the GitHub Action in
`.github/workflows/strato.yml`. It first verifies that `site/` still matches
`content/`, then uploads. Without FTP credentials in the repository secrets
the upload step is skipped and only the check runs.
