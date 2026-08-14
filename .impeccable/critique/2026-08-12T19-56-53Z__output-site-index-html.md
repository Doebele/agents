---
target: site/index.html
total_score: 29
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 2
timestamp: 2026-08-12T19-56-53Z
slug: output-site-index-html
---
# Critique Re-Run — AGENT // SYSTEM (output/site/index.html)

Method: dual-agent (A: agent_682d11a5 · B: agent_dea5d0d5). Re-run after fixes #1-#6.

## Design Health Score — 29/40 (Good) — up from 25/40

| # | Heuristic | Score | Key issue |
|---|-----------|-------|-----------|
| 1 | Visibility of system status | 3 | prog bar, boot, loop pulse, active states; 3D label flicker minor |
| 2 | Match real world | 3 | Baustein/Steckbrief/Harness=Motor, Denken/Handeln/Beobachten apt |
| 3 | User control & freedom | 3 | back btn, Escape, scrim, history.pushState, focus restore (was 2) |
| 4 | Consistency & standards | 3 | 7-color disciplined; clickable vs static cards share hover-lift (affordance ambiguity) |
| 5 | Error prevention | 3 | search empty-state, logo onerror, Three/GSAP fallbacks |
| 6 | Recognition over recall | 3 | labels, glossary, search (was 2) |
| 7 | Flexibility & efficiency | 3 | Cmd-K, full keyboard, arrow-nav search (was 1) |
| 8 | Aesthetic & minimalist | 2 | dense/maximalist; hosting spreadsheet vs Rams ethos (the cap) |
| 9 | Error recovery | 3 | graceful fallbacks everywhere |
| 10 | Help & docs | 3 | glossary, Praxis-Tipps, insights, rules (was 2) |

## Design specificity
Authored where it matters: mission-control/field-guide frame, 7-color system mapped 1:1 to building blocks and carried hero->card->drawer->steck->3D, clickable Three.js hero whose labels ARE the module nav, Fira Sans/Code. Generic in atmospheric skin (neon-on-black + grain/scan/vignette/cursor/boot = the Linear/Vercel/v0 uniform).

## Deterministic scan (B, FULL parser mode)
11 findings (DE) / 10 (EN). Categories: tight-leading, tiny-text, wide-tracking(2), all-caps-body(3), clipped-overflow-container(2), kicker-above-heading(DE only), repeating-stripes-gradient. Assessment: ALL are heuristic over-fires or intentional micro-type, NOT real defects — tight-leading is display text, clipped-overflow is decorative fixed bg layers + the closed .oc card, stripes is a 1.2%-opacity scanline; all-caps/wide-tracking/tiny-text are the deliberate tracked-caps mono-label system. No real defect remains (contrast, headings, side-tabs, gradient-text, cramped-padding, undersized all cleared).

## Overall
+4 (25->29). Structural + a11y fixes are real and verified: master->detail drawer (focus-trap, history, back), Cmd-K search over all 77 Steckbriefe, AAA contrast, heading order, aria labels, boot-skip, mobile nav, glossary, practitioner hero. No P0, no broken heuristic. Ceiling is now content density + catalog-without-guidance + card monotony + mobile nav legibility + Rams-vs-maximalism.

## What's working
1. Color-as-semantics followed through end-to-end (hero spheres -> card glow -> drawer accent -> chip hover).
2. Master->detail drawer is well-engineered a11y (focus trap, pushState/popstate, Escape/scrim/back, lastFocus restore, aria-hidden).
3. Steckbrief layer is real reference value (AA scores, pricing, tips, docs) + Cmd-K makes all 77 retrievable.

## Priority issues still remaining
- [P1] Hosting/hardware is a data dump that breaks pacing -> collapse to typed comparison/filtered list or move behind a toggle. -> /impeccable distill
- [P1] Catalog informs but never guides; no "start here" path for a practitioner -> add a short recommended "first stack" or 3-question wizard. -> /impeccable onboard
- [P2] Card-grid monotony + affordance ambiguity (clickable .mod/.it/.chip vs static .prov/.rule-card share hover-lift) -> differentiate static vs interactive cards. -> /impeccable layout
- [P2] Mobile nav-dots inscrutable (labels hover-gated, invisible on touch; aria-label ok for SR) -> show labels on pointer:coarse or compact labeled menu. -> /impeccable adapt
- [P3] Rams "Weniger, aber besser" vs maximalist skin (grain+scan+vignette+3D+cursor+boot+7 colors) -> trim 2 atmosphere layers or swap quote. -> /impeccable quieter

## Persona red flags (current)
- Jordan (first-timer): #sec-hosting hardware tiers + Steckbrief blurbs still expert register; glossary at bottom, unlinked from body terms.
- Casey (mobile): 7 nav-dots unlabeled on touch; nav row near overflow at <=380px.
- Sam (a11y): nav-dot href duplication (7 links same href, diff aria-labels); .nlabel clickable w/o role/name; #d-title swap w/o aria-live; cursor:none over selectable text.

## Minor
- Two 9px remnants: .nav-dots a::after (9px), .nlabel .idx (9px).
- card edges ~1.2:1, nearly vanish on #06070B (slight scannability hit).
- "stat-row" infinity/filler; search empty-state could seed the 7 modules.
- no theme-color/favicon (trivial).

## Questions
1. Preaches "Weniger, aber besser" while shipping 6+ atmosphere layers — which two die first if you mean it?
2. 77-entry catalog, Cmd-K, but no recommended path — why isn't the first answer "start here for your stack"?
3. The 7-color idea is the best concept, but on a phone it collapses to 7 identical unlabeled dots — is the best idea invisible on the most common device?
