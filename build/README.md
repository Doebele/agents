# Build

The two pages in `site/` are **build outputs**. Editing them directly loses
the change on the next build.

```bash
python3 build/build.py            # builds site/index.html and site/index.de.html
python3 build/build.py --check    # builds only, reports differences
```

## Where things live

| File | Content |
|---|---|
| `content/steckbrief.json` | the 109 fact sheets |
| `content/modules.json` | the seven building blocks, with their chips and groups |
| `content/glossary.json` | glossary terms |
| `content/arbeitsarten.json` | kinds of work, wizard steps, prerequisites, tutorial |
| `content/rules.json`, `oc.json`, `hardware.json`, `providers.json`, `loop.json` | the remaining data blocks |
| `content/ui.json` | the translated lines of the page |
| `build/template.html` | scaffold, CSS and logic — everything both languages share |

## Two languages

Translated values sit **side by side** as `{"de": …, "en": …}`. A missing
translation is therefore visible in its neighbouring key, and the check
catches it as well. Anything identical in both languages — names, links,
colours, icons — appears once.

English is the default file (`index.html`); German hangs off the DE switch
(`index.de.html`).

## What the check catches

It runs before anything is written and stops the build rather than shipping:

- a missing or empty translation in any field
- a chip with no fact sheet behind it
- a fact sheet no chip reaches
- a template marker with no content, and the reverse

Counter-tested: an emptied English blurb and a deleted fact sheet are both
reported instead of reaching the page.

## Deliberate simplifications

`content/ui.json` works **line by line**, not sentence by sentence, so an
entry may contain markup. That is intended: the line-wise mapping is provably
lossless — both language files had the same line count and differed only by
substitution, never by insertion. Splitting finer is worth it once a third
language arrives.

The keys `t001…t090` are sequential, not descriptive. New translated lines
take the next free number.

## Where this came from

`build/extract.py` derived the template and the content from the finished
pages once. It is no longer needed unless the split has to be redone.
`build/verify.py` compares a build output against a reference: data blocks for
structural equality, everything else byte for byte. That is how the build was
shown to reproduce the hand-maintained pages faithfully.
