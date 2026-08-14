---
target: site/index.html
total_score: 25
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 4
timestamp: 2026-08-12T18-14-59Z
slug: output-site-index-html
---
# Critique — AGENT // SYSTEM (output/site/index.html)

Method: dual-agent (A: agent_b1afdbc8 · B: agent_fc376ec0)

## Design Health Score — 25/40 (Acceptable)

| # | Heuristic | Score | Key issue |
|---|-----------|-------|-----------|
| 1 | Visibility of system status | 3 | Boot/progress/active loop clear; no external-link feedback |
| 2 | Match real world | 3 | Strong beginner metaphors |
| 3 | User control & freedom | 2 | Escape+scrim ok; no focus-trap, Back doesn't close |
| 4 | Consistency & standards | 3 | Two overlapping overlay systems |
| 5 | Error prevention | 3 | MCP security warning well placed |
| 6 | Recognition over recall | 2 | Nav dots unlabeled (hover-only) |
| 7 | Flexibility & efficiency | 1 | No search/filter/index over 50+ entries |
| 8 | Aesthetic & minimal | 3 | Disciplined; modal stacks up to 6 blocks |
| 9 | Error recovery | 3 | Clean graceful degradation |
| 10 | Help & docs | 2 | Good tips/insights, no glossary vs "no jargon" promise |

## Design specificity
Largely authored-for-this-product: field-guide/system-dossier concept sustained (boot copy, BAUSTEIN stamps, mono voice, 7-color module identity hero->card->drawer->modal->3D). Two interchangeable zones: three near-identical card grids; dark+neon+mono genre crowded.
Deterministic scan (B, FULL parser mode): 22 findings (DE) / 21 (EN). Earlier "0 findings" was degraded regex mode (parser modules missing).

## Overall impression
Genuinely authored, cinematic field guide; peaks at hero 3D + loop, sustains 7-color system. Slips in back half (hosting/hardware dry reference; no search). Biggest levers: findability + a11y floor (contrast, heading order, focus).

## What's working
1. Concept-to-pixel consistency (boot, BAUSTEIN stamps, mono voice, 7-color identity to 3D nodes).
2. Hero 3D is load-bearing (7 nodes = 7 modules, projected clickable labels = sitemap) with fallback craft.
3. Honest progressive enhancement (cursor/GSAP/WebGL/icons degrade cleanly).

## Priority issues
- [P1] Contrast & micro-type below AA (A+B, 7x): --muted #6E7691 ~4.3-4.47:1 on 10-11px labels. Fix: lighten --muted to >=4.5:1 or bump size/weight. -> /impeccable colorize
- [P1] 50+ tools, no search/filter/index. Fix: cmd-K palette over STECKBRIEF or per-drawer filter + starter pin. -> /impeccable onboard
- [P1] Nested overlays, no focus-trap/history (drawer z140 + modal z160; Back no-op; Tab leaks). Fix: focus-trap + pushState or collapse modal into drawer. -> /impeccable distill
- [P1] Heading hierarchy h2->h4 skips h3 (loop detail, oc-tab) + remaining "Schritt 1/Step 1" kicker over h4 (B caught). Fix: insert h3 / remove kicker. -> /impeccable harden
- [P2] Three near-identical card grids erase section hierarchy. Fix: distinct surface per section + chapter breaks. -> /impeccable shape
- [P2] Boot unskippable + mobile loses nav (<760px nav-dots gone). Fix: click-to-skip + sessionStorage; mobile section menu. -> /impeccable harden
- [P2] .oc card no padding, first child flush (B). Fix: add padding. -> /impeccable layout
- [P3] Mono labels tiny/wide-tracked, long all-caps boot lines, 1.2% scanline (B; mostly borderline/FP). -> /impeccable typeset

## Persona red flags
- Jordan (first-timer): chip walls (16/19) no "start here"; hero "no jargon" vs drawers MoE/PagedAttention/ROCm/VRAM-math.
- Sam (a11y): nav-dots no aria-label + hover-only label; #hero-canvas no role/aria-label; global cursor:none strips OS cursor for low-vision desktop; muted labels fail AA; heading skips break AT outline.
- Casey (mobile): <760px nav-dots removed no replacement; .oc-tab squeeze/wrap on 375px; loop tap targets shrink; 500-particle 3D spins on mobile.

## Minor / false positives
- .nlabel +34px offset collides with h1 on short viewports.
- _EXT SVG defined twice; nav-dot href="#sec-modules" misleading (preventDefault + drawer).
- .stat-row filler.
- FPs (B): tight-leading 1.18x (display text), clipped-overflow (decorative fixed bg + closed .oc card by design), repeating-stripes (1.2% white scanline). Detector under-reported kicker (1/3 DE, 0/3 EN).

## Questions
1. Beginner hero vs practitioner drawers — who is it really for?
2. Two overlay systems — does the modal earn its layer, or add disorientation a master->detail transition removes?
3. A field guide you can't search — is findability the biggest gap?
