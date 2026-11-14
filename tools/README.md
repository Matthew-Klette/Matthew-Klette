Generates the SVG cards in `../cards` in the portfolio's type and palette.

    python3 -m venv .venv && .venv/bin/pip install fonttools brotli
    .venv/bin/python build.py ../cards

Fonts are Instrument Serif, Geist and Geist Mono (SIL Open Font License), embedded so
the cards render the same inside GitHub's image proxy. Text is measured with the real
font metrics, so wrapping is exact. Screenshots in `shots/` come from the live builds.
