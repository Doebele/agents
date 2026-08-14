# AGENT // SYSTEM — Interactive Field Guide to the AI Agent Landscape

A self-contained, interactive **dark-mode website** about AI agents — its own style,
structure, copy, and visuals. Seven building blocks, the agent loop, open vs. closed
models, five rules. Status: August 2026.

## Languages / Sprachen

The site ships in **two complete, self-contained versions** with a switch in the top
nav (DE ↔ EN):

| File | Language |
|---|---|
| `index.html` | Deutsch (default) |
| `index.en.html` | English |

Both open standalone (double-click). Each translates everything — hero, sections,
loop, modules, all 86 product fact-sheets — and links to the other via the nav switch.

## Open

```bash
open index.html            # German  (open index.en.html for English)
python3 -m http.server 8765 # or serve locally -> http://localhost:8765
```

Internet needed for the CDN libraries (Three.js, GSAP, Google Fonts). Without internet
the page still loads — content stays visible, 3D/animation degrade gracefully.

## Fact-sheets (Steckbriefe)

Every mentioned **model, tool, MCP server, skill, and design tool** is deep-clickable.
Open a module deep-dive (drawer), tap any product chip — or pick a model in the
Open/Closed comparison — and a **fact-sheet** opens with:

- short description (verified facts)
- category & vendor, open/closed
- **official links**: website, docs, download/code
- **video tutorials** (search)
- **practical tip**

**86 fact-sheets**, all links researched and verified (no invented URLs). Where no
canonical link existed, the field is omitted rather than guessed.

> Note: **Kimi Code** (Moonshot AI) is listed as a harness under Block 02 (alongside
> Claude Code, OpenAI Codex, ZCode, and others) and has its own fact-sheet.

## Style & tech

- **Look:** dark "terminal meets editorial", near-black with neon cyan and ember
  orange; each block has its own neon accent.
- **Type:** Fira Sans (display + text) + Fira Code (data/labels).
- **3D (Three.js):** particle field, glowing core, seven orbiting, labeled, clickable
  nodes; mouse parallax; pauses off-screen.
- **Animation (GSAP + ScrollTrigger):** boot sequence, scroll reveals, progress bar,
  animated loop.
- **Interaction:** Think→Act→Observe loop, module drawer, fact-sheet modal,
  open/closed toggle, custom cursor, grain/scanline.
- **Robustness:** GSAP and Three.js are optional; `prefers-reduced-motion` respected.

## Polish (Impeccable)

A craft pass removed the typical AI-design tells: gradient text, side-tab borders,
generic display font, cursor layout-thrash, em-dash saturation, and eyebrow scaffolding.
The mechanical detector now passes with 0 findings.

## Sections

1. Hero — kinetic title + 3D system
2. Thesis — "A chatbot answers. An agent acts."
3. The loop — interactive Think/Act/Observe cycle
4. Seven blocks — clickable modules with deep-dives **+ per-product fact-sheets**
5. Open or closed? — toggleable comparison (models clickable)
6. Open weights: host or run locally — hosting providers (pricing model, free tier, source link; Hostinger, Together AI, Fireworks, Groq, RunPod, Lambda, Vast.ai, Hetzner, Modal, Replicate, OpenRouter) + hardware by OS (macOS / Windows+Linux, entry → pro), with a note for the Mac mini M4 Pro 64 GB
7. Five rules
8. Closing — "Less, but better." (Dieter Rams)

All facts, product names, and versions reflect August 2026; the copy is original.
Source files in the project were read only, never modified.
