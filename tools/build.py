"""Profile README cards in the portfolio's quiet-luxury register.

Ivory paper, warm ink, Instrument Serif headings with an italic second clause,
Geist body, Geist Mono meta labels, one deep green for "live". Fonts are the
portfolio's own woff2 files, embedded so GitHub's <img> rendering matches.
Text is measured with the real font metrics so wrapping is exact.
"""
import base64
import html
import os
import sys

from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# --- tokens (src/styles/tokens.css) -----------------------------------------
CANVAS = "#f4f1ea"
CARD = "#ebe6dc"
INK = "#151412"
BODY = "rgba(21,20,18,0.86)"
CHARCOAL = "rgba(21,20,18,0.74)"
MUTE = "#4f4a43"
ASH = "#5d584f"
HAIR = "rgba(21,20,18,0.12)"
GREEN = "#1f6b4a"
# .ink band
I_CANVAS = "#121110"
I_CARD = "#1b1a17"
I_INK = "#f3f1ec"
I_BODY = "rgba(243,241,236,0.86)"
I_MUTE = "#b4b0a8"
I_HAIR = "rgba(243,241,236,0.12)"
I_GREEN = "#3ddc97"

FONTS = {
    "serif": ("Instrument Serif", "normal", "serif.woff2"),
    "serif-i": ("Instrument Serif", "italic", "serif-italic.woff2"),
    "sans": ("Geist", "normal", "sans.woff2"),
    "mono": ("Geist Mono", "normal", "mono.woff2"),
}
_metrics = {}


def _font(key):
    if key not in _metrics:
        f = TTFont(os.path.join(HERE, "fonts", FONTS[key][2]))
        _metrics[key] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    return _metrics[key]


def width(text, key, size, tracking=0.0):
    cmap, hmtx, upm = _font(key)
    total = 0
    for ch in text:
        g = cmap.get(ord(ch)) or cmap.get(ord("n"))
        total += hmtx[g][0]
    return total / upm * size + tracking * size * max(len(text) - 1, 0)


def wrap(text, key, size, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if width(trial, key, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def font_css(keys):
    out = []
    for k in keys:
        fam, style, fn = FONTS[k]
        data = base64.b64encode(open(os.path.join(HERE, "fonts", fn), "rb").read()).decode()
        weight = "100 900" if k == "sans" else "400"
        out.append(
            f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
        )
    return "".join(out)


BASE_CSS = """
.serif{font-family:'Instrument Serif',Georgia,serif}
.it{font-family:'Instrument Serif',Georgia,serif;font-style:italic}
.sans{font-family:'Geist',system-ui,sans-serif}
.mono{font-family:'Geist Mono',ui-monospace,monospace;letter-spacing:.06em}
.pulse{animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
@media (prefers-reduced-motion:reduce){.pulse{animation:none}}
"""


def esc(s):
    return html.escape(s, quote=True)


def text(x, y, s, cls, size, fill, extra="", delay=None, anchor=None):
    # delay is accepted for call-site readability but unused: text never animates, so it
    # is always readable, even where a renderer freezes CSS animation at frame zero.
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" font-size="{size}" fill="{fill}"{a}{extra}>{esc(s)}</text>'


def svg(w, h, body, keys, title, bg=CANVAS, grain=True, radius=14, border=HAIR):
    grain_def = (
        '<filter id="g" x="0" y="0" width="100%" height="100%">'
        '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>'
        '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .07 0"/></filter>'
        if grain
        else ""
    )
    grain_rect = f'<rect width="{w}" height="{h}" filter="url(#g)" clip-path="url(#c)"/>' if grain else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title>"
        f"<defs><style>{font_css(keys)}{BASE_CSS}</style>"
        f'<clipPath id="c"><rect width="{w}" height="{h}" rx="{radius}"/></clipPath>{grain_def}</defs>'
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{radius}" fill="{bg}" stroke="{border}"/>'
        f"{grain_rect}{body}</svg>"
    )


def dot(x, y, r=4, fill=GREEN, pulse=False):
    cls = ' class="pulse"' if pulse else ""
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"{cls}/>'


def eyebrow(x, y, label, fill=MUTE, green=GREEN, delay=None):
    return dot(x + 4, y - 4, 3.5, green) + text(x + 16, y, label.upper(), "mono", 13, fill, delay=delay)


def heading(x, y, plain, italic, size, ink=INK, soft=ASH, delay=None):
    w = width(plain + " ", "serif", size)
    return text(x, y, plain, "serif", size, ink, delay=delay) + text(x + w, y, italic, "it", size, soft, delay=delay)


# --- header ----------------------------------------------------------------------
def header():
    W, H = 1200, 470
    b = []
    b.append(text(56, 70, "Matthew Klette", "sans", 22, INK, ' font-weight="500"'))
    right = "MBK CONSULTING GROUP · SOUTH AFRICA"
    rw = width(right, "mono", 13, 0.06)
    b.append(dot(1144 - rw - 16, 65, 4, GREEN, pulse=True))
    b.append(text(1144, 70, right, "mono", 13, MUTE, anchor="end"))
    cols = [
        ("01 · Analytics engineering", "Numbers that", "agree."),
        ("02 · Frontend builds", "Sites you can", "step inside."),
        ("03 · Open source", "Code that", "proves itself."),
    ]
    colw = (1200 - 112) / 3
    for i, (eb, l1, l2) in enumerate(cols):
        x = 56 + i * colw
        if i:
            b.append(f'<line x1="{x-24:.1f}" y1="168" x2="{x-24:.1f}" y2="340" stroke="{HAIR}"/>')
        d = 0.1 + i * 0.12
        b.append(text(x, 190, eb.upper(), "mono", 13, MUTE, delay=d))
        b.append(text(x, 262, l1, "serif", 62, INK, delay=d + 0.05))
        b.append(text(x, 326, l2, "it", 62, ASH, delay=d + 0.1))
    b.append(f'<line x1="56" y1="392" x2="1144" y2="392" stroke="{HAIR}"/>')
    b.append(text(56, 428, "sGTM · GA4 · Meta CAPI · Consent Mode v2 · BigQuery · Go · Python · React · three.js", "mono", 14, CHARCOAL))
    return svg(W, H, "".join(b), ["serif", "serif-i", "sans", "mono"],
               "Matthew Klette. Numbers that agree. Sites you can step inside. Code that proves itself.")


# --- open source -----------------------------------------------------------------
OSS = [
    ("patch-audit", "Code review tool",
     "Reviews a patch before a person does. It flags skipped tests, removed assertions, secrets and risky code, then applies the patch to a throwaway clone and runs the tests before and after.",
     "Standard library only, about 90% test coverage, and CI runs it on its own pull requests.",
     "Go / GitHub Actions"),
    ("inference-queue", "Backend service",
     "A self-hostable service for batch LLM inference and eval runs: a Postgres queue with leases, retries and dead-letter, a Redis result cache, per-key rate limits, idempotent submits and signed webhooks.",
     "Integration tests run against real Postgres, including a worker crash mid-lease.",
     "Go / PostgreSQL / Redis / Prometheus / Docker"),
    ("Full-stack casebook", "Debugging casebook",
     "A team shift board and seven failure cases, from a stale cache and a renamed API field to a lost update and a duplicate payroll export, each traced from the browser to the database.",
     "Every case has a seed commit and a fix commit, with a test that fails on one and passes on the other.",
     "FastAPI / SQLAlchemy / React / TypeScript / Playwright"),
    ("UI task bench", "Frontend tasks",
     "Frontend tasks written from mockups and diagrams: a checkout form, an SVG chart, a canvas colour picker and a virtual list bug, each with a rubric, a starter, a reference and a verifier.",
     "One command proves every verifier passes the reference and fails the starter on each rubric line.",
     "React / TypeScript / SVG / Canvas / Vitest"),
    ("couch-tv", "Upstream contribution",
     "The first working Hisense VIDAA support for an open-source Google TV home screen: modern-firmware auth, PIN pairing and a native app tile, then a standalone home that needs no computer.",
     "Two pull requests merged by the maintainer, tested on a real TV.",
     "Python / MQTT / Reverse engineering"),
]


def open_source():
    W = 1200
    x0, body_x, body_w = 56, 470, 674
    b = [eyebrow(x0, 74, "Open source")]
    b.append(heading(x0, 136, "Code you can read,", "with tests that say so.", 50, delay=0.05))
    lede = "Public repositories and upstream work. Each one has a test suite, and the README says what it proves."
    b.append(text(x0, 182, lede, "sans", 17, CHARCOAL))
    y = 226
    for i, (name, kind, desc, proof, stack) in enumerate(OSS):
        b.append(f'<line x1="{x0}" y1="{y}" x2="{W-56}" y2="{y}" stroke="{HAIR}"/>')
        top = y + 46
        d = 0.15 + i * 0.08
        b.append(text(x0, top, f"/{i+1:02d}", "mono", 13, MUTE, delay=d))
        b.append(text(x0 + 60, top + 2, name, "serif", 32, INK, delay=d))
        b.append(text(x0 + 60, top + 30, kind.upper(), "mono", 12, MUTE, delay=d))
        ly = top - 2
        for line in wrap(desc, "sans", 15.5, body_w):
            b.append(text(body_x, ly, line, "sans", 15.5, CHARCOAL, delay=d))
            ly += 25
        ly += 8
        plines = wrap(proof, "sans", 15.5, body_w - 18)
        b.append(dot(body_x + 3, ly - 5, 3.5))
        for j, line in enumerate(plines):
            b.append(text(body_x + 16, ly, line, "sans", 15.5, INK, delay=d))
            ly += 25
        ly += 10
        b.append(text(body_x, ly, stack.upper(), "mono", 12, MUTE, delay=d))
        y = max(ly, top + 40) + 34
    b.append(f'<line x1="{x0}" y1="{y}" x2="{W-56}" y2="{y}" stroke="{HAIR}"/>')
    H = y + 44
    return svg(W, H, "".join(b), ["serif", "serif-i", "sans", "mono"],
               "Open source: patch-audit, inference-queue, full-stack casebook, UI task bench, couch-tv")


# --- build cards ------------------------------------------------------------------
BUILDS = [
    ("goldenhour", "Golden Hour", "Motion", "/03 · Oct 2026",
     "A 76-second portfolio intro where every sound and every frame is code.", "Web Audio / GSAP / Canvas"),
    ("aubade", "Aubade", "Concept site", "/01 · Oct 2026",
     "A lamp that matches the daylight outside your window, minute by minute. The product is fictional; the frontend is real.",
     "Next.js / three.js / GSAP / Lenis"),
    ("nishiki", "Nishiki", "Field guide", "/02 · Oct 2026",
     "Eight koi varieties drawn live in code, with a judging vocabulary, an ID game and a pond you can feed.",
     "Vite / React / TypeScript / Canvas 2D"),
    ("heartbeat", "Heartbeat", "Tribute", "/06 · Oct 2026",
     "A farewell to the last petrol Jaguar sports car, read through eight gears with scroll as the throttle.",
     "Vite / React / GSAP / Lenis"),
]


def build_card(slug, title, kind, meta, desc, stack):
    W, H = 600, 590
    img_h = 336
    shot = base64.b64encode(open(os.path.join(HERE, "shots", f"{slug}.jpg"), "rb").read()).decode()
    b = [
        f'<image href="data:image/jpeg;base64,{shot}" x="0" y="0" width="{W}" height="{img_h}" preserveAspectRatio="xMidYMin slice" clip-path="url(#c)"/>',
        f'<rect x="0" y="0" width="{W}" height="{img_h}" fill="none"/>',
        f'<line x1="0" y1="{img_h}" x2="{W}" y2="{img_h}" stroke="{HAIR}"/>',
    ]
    y = img_h + 46
    pw = width(kind, "sans", 13) + 24
    b.append(f'<rect x="28" y="{y-19}" width="{pw:.1f}" height="27" rx="13.5" fill="{CANVAS}" stroke="{HAIR}"/>')
    b.append(text(40, y, kind, "sans", 13, BODY))
    b.append(text(W - 28, y, meta.upper(), "mono", 12, MUTE, anchor="end"))
    y += 52
    b.append(text(28, y, title, "serif", 36, INK))
    y += 34
    for line in wrap(desc, "sans", 15, W - 56)[:3]:
        b.append(text(28, y, line, "sans", 15, CHARCOAL))
        y += 24
    b.append(text(28, H - 30, stack.upper(), "mono", 12, MUTE))
    b.append(dot(W - 92, H - 34, 3.5, GREEN, pulse=True))
    b.append(text(W - 28, H - 30, "LIVE", "mono", 12, GREEN, anchor="end"))
    return svg(W, H, "".join(b), ["serif", "sans", "mono"], f"{title}: {desc}", bg=CARD)


def builds_head():
    W, H = 1200, 196
    b = [eyebrow(56, 74, "Frontend builds")]
    b.append(heading(56, 136, "Every build is a real site.", "Open any of them.", 50, delay=0.05))
    b.append(text(56, 172, "Concept sites, scroll stories and motion pieces I designed and built. Each card opens the live site.", "sans", 17, CHARCOAL))
    return svg(W, H, "".join(b), ["serif", "serif-i", "sans", "mono"], "Frontend builds: every build is a real site.")


# --- what I do (ink band) -----------------------------------------------------------
WHAT = [
    ("01 · Measurement", "0 → 59", "of 180 web tags now wait for consent",
     ["Server-side GTM, client + server", "Meta CAPI + Google Ads from the server", "Deduped against the pixel by event ID", "Consent Mode v2 · OneTrust · CCPA"]),
    ("02 · Shipping", "27 → 50", "server-side data streams",
     ["57 of 60 server releases in 2026", "74 of 80 web releases in 2026", "Every release, June to October 2026", "Server-side GTM audit, May 2026"]),
    ("03 · AI engineering", "13", "Claude Code skills written",
     ["4 n8n automations in production", "Claude drafts, people approve in Teams", "A second brain that runs itself", "Sound and motion built in code"]),
]


def what_i_do():
    W, H = 1200, 520
    b = [eyebrow(56, 74, "What I do · Contract MarTech engineer for a US apparel brand since 2024", I_MUTE, I_GREEN)]
    colw = (W - 112) / 3
    for i, (eb, big, label, items) in enumerate(WHAT):
        x = 56 + i * colw
        d = 0.1 + i * 0.12
        if i:
            b.append(f'<line x1="{x-24:.1f}" y1="124" x2="{x-24:.1f}" y2="460" stroke="{I_HAIR}"/>')
        b.append(text(x, 140, eb.upper(), "mono", 13, I_MUTE, delay=d))
        b.append(text(x, 222, big, "serif", 72, I_INK, delay=d + 0.05))
        b.append(text(x, 258, label, "it", 22, I_MUTE, delay=d + 0.1))
        y = 312
        for it in items:
            b.append(f'<line x1="{x}" y1="{y-26}" x2="{x+colw-48:.1f}" y2="{y-26}" stroke="{I_HAIR}"/>')
            b.append(text(x, y - 4, it, "sans", 15, I_BODY, delay=d + 0.15))
            y += 40
    return svg(W, H, "".join(b), ["serif", "serif-i", "sans", "mono"],
               "What I do: measurement, shipping releases and AI engineering", bg=I_CANVAS, border=I_HAIR)


# --- stack --------------------------------------------------------------------------
STACK = [
    ("Measurement", "Server-side & web GTM / GA4 / Meta CAPI & Pixel / Google Ads / Consent Mode v2 / OneTrust"),
    ("Data", "BigQuery SQL / Looker Studio / PostgreSQL / Redis / Firebase"),
    ("AI & automation", "Claude API / Claude Code skills & hooks / MCP integrations / n8n / Model cascades & evals"),
    ("Backend", "Go / Python (FastAPI) / SQLAlchemy / Docker / Prometheus"),
    ("Frontend & motion", "TypeScript / React / Next.js / three.js & WebGL2 / GSAP & Lenis / Canvas 2D / Web Audio"),
    ("Mobile & more", "Kotlin (Android) / Capacitor (iOS) / C# / Vitest / Playwright / Blender & ffmpeg"),
]


def stack():
    W = 1200
    b = [eyebrow(56, 74, "Stack")]
    b.append(heading(56, 136, "The working toolkit,", "grouped by job.", 50, delay=0.05))
    y = 178
    for i, (area, tools) in enumerate(STACK):
        b.append(f'<line x1="56" y1="{y}" x2="{W-56}" y2="{y}" stroke="{HAIR}"/>')
        ty = y + 44
        b.append(text(56, ty, f"/{i+1:02d}", "mono", 13, MUTE))
        b.append(text(116, ty + 2, area, "serif", 28, INK))
        lines = wrap(tools, "sans", 17, 1144 - 470)
        ly = ty
        for line in lines:
            b.append(text(470, ly, line, "sans", 17, CHARCOAL))
            ly += 28
        y = max(ly, ty + 10) + 18
    b.append(f'<line x1="56" y1="{y}" x2="{W-56}" y2="{y}" stroke="{HAIR}"/>')
    return svg(W, y + 40, "".join(b), ["serif", "serif-i", "sans", "mono"], "Stack: " + "; ".join(f"{a}: {t}" for a, t in STACK))


def write(name, content):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(content)
    print(f"{name:24s} {len(content)//1024:4d} KB")


write("header.svg", header())
write("open-source.svg", open_source())
write("builds.svg", builds_head())
for s, t, k, m, d, st in BUILDS:
    write(f"build-{s}.svg", build_card(s, t, k, m, d, st))
write("what-i-do.svg", what_i_do())
write("stack.svg", stack())
