# Build outputs

The files in this folder are **generated**. Do not edit them — the next build
overwrites the change.

| File | Language |
|---|---|
| `index.html` | English (default) |
| `index.de.html` | German |
| `.htaccess` | disables the inherited rewrite rules of the parent domain |

Both pages are self-contained and open by double-click. An internet
connection is needed for the CDN libraries (GSAP) and the vendor logos;
without one the content stays fully readable and the animations degrade
quietly.

Content and build instructions: see the repository README and `build/`.

The two `test_*.js` files drive the scroll sequence through Playwright; they
were written while building the loop diagram and are kept as a record.
