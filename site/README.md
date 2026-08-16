# Build outputs

`index.html` and `index.de.html` are **generated and not in git**. Run
`python3 build/build.py` from the repository root and they appear here:
English as `index.html`, German as `index.de.html`. Editing them is undone by
the next build.

`.htaccess` is committed. It disables the inherited rewrite rules of the
parent domain and is uploaded along with the pages.

Both pages are self-contained and open by double-click. An internet
connection is needed for the CDN libraries (GSAP) and the vendor logos;
without one the content stays fully readable and the animations degrade
quietly.

Content and build instructions: see the repository README and `build/`.

The two `test_*.js` files drive the scroll sequence through Playwright; they
were written while building the loop diagram and are kept as a record.
