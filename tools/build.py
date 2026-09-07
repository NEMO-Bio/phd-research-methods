#!/usr/bin/env python3
"""Assemble a standalone essay HTML from src/*.html, inlining the figure SVGs.

    python3 build.py [srcdir] [outfile]

Defaults: srcdir = ./src, outfile = <parent-of-srcdir>/<parent-dir-name>.html.
Parts are part*.html in numeric order, then refs.html last if present.

Figure placeholders look like

    <!--FIG:fig-name
    caption text, may contain markup and span lines
    -->

and are replaced by a numbered <figure class="figbox"> holding ../figures/fig-name.svg,
inlined with its ink and grid colours rewritten to CSS variables so the plot follows the
page theme, and with its internal ids namespaced so several SVGs can share the document.

After writing, reports unresolved placeholders, dangling anchors, uncited references and
linked PDFs that are not on disk. Any of those means the build failed.
"""
import os
import re
import sys

# matplotlib writes these literal colours; map them onto the page's palette.
# The six mark colours stay literal so figures keep their identity in both themes.
COLOUR_MAP = {
    "#20201e": "currentColor",      # ink: text, titles, median lines
    "#877f77": "var(--gray)",       # gray: axes, ticks
    "#ede7e0": "var(--gridc)",      # grid
    "#b8aea5": "var(--leader)",
}

FIG_RE = re.compile(r"<!--FIG:([A-Za-z0-9_-]+)\s*\n(.*?)-->", re.S)


def part_order(name):
    m = re.search(r"part(\d+)", name)
    return (0, int(m.group(1)) if m else 0, name)


def parts_of(srcdir):
    files = [f for f in os.listdir(srcdir) if f.startswith("part") and f.endswith(".html")]
    files.sort(key=part_order)
    if os.path.exists(os.path.join(srcdir, "refs.html")):
        files.append("refs.html")
    return files


def load_svg(figdir, name, tag):
    p = os.path.join(figdir, name + ".svg")
    with open(p) as f:
        s = f.read()
    s = s[s.index("<svg"):]                       # drop the xml/doctype preamble
    s = re.sub(r'\s(width|height)="[^"]*pt"', "", s, count=2)
    for k, v in COLOUR_MAP.items():
        s = re.sub(k, v, s, flags=re.I)

    # Inline SVG styles share the document cascade. Several generated figures use
    # short class names such as .m, .h and .n, which can silently restyle prose
    # classes with the same names. Prefix every SVG class and its style selector
    # before inlining so figure typography cannot leak into the essay.
    def scope_style(m):
        body = re.sub(r'(?<![\w-])\.([A-Za-z_][\w-]*)',
                      lambda x: f'.{tag}-{x.group(1)}', m.group(2))
        return m.group(1) + body + m.group(3)

    s = re.sub(r'(<style\b[^>]*>)(.*?)(</style>)', scope_style, s, flags=re.S)
    s = re.sub(r'\bclass="([^"]+)"',
               lambda m: 'class="' + ' '.join(f'{tag}-{c}' for c in m.group(1).split()) + '"', s)
    s = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{tag}-{m.group(1)}"', s)
    s = re.sub(r'\b(xlink:href|href)="#([^"]+)"',
               lambda m: f'{m.group(1)}="#{tag}-{m.group(2)}"', s)
    s = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{tag}-{m.group(1)})', s)
    s = s.replace('<svg ', '<svg role="img" ', 1)
    return s


def main():
    srcdir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "src")
    root = os.path.dirname(srcdir)
    figdir = os.path.join(root, "figures")
    out = (os.path.abspath(sys.argv[2]) if len(sys.argv) > 2
           else os.path.join(root, os.path.basename(root) + ".html"))

    files = parts_of(srcdir)
    if not files:
        sys.exit(f"no part*.html in {srcdir}")
    html = "".join(open(os.path.join(srcdir, p)).read() for p in files)

    counter = [0]

    def sub_fig(m):
        name, caption = m.group(1), m.group(2).strip()
        counter[0] += 1
        n = counter[0]
        svg = load_svg(figdir, name, "f" + str(n))
        return (f'<figure class="figbox" id="{name}">\n{svg}\n'
                f'<figcaption><b>Figure {n}.</b> {caption}</figcaption>\n</figure>')

    html = FIG_RE.sub(sub_fig, html)
    with open(out, "w") as f:
        f.write(html)
    print(f"wrote {out}  ({os.path.getsize(out)/1024:.0f} kB, {len(files)} parts, "
          f"{counter[0]} figures inlined)")

    bad = False
    left = html.count("<!--FIG:")
    if left:
        print(f"  UNRESOLVED figure placeholders: {left}")
        bad = True
    ids = set(re.findall(r'<h2 id="([^"]+)"', html)) | set(re.findall(r'<figure[^>]*id="([^"]+)"', html))
    refids = set(re.findall(r'<li id="([^"]+)"', html))
    hrefs = set(re.findall(r'<a[^>]*\shref="#([^"]+)"', html))
    missing = hrefs - ids - refids
    if missing:
        print("  DANGLING anchors:", sorted(missing))
        bad = True
    unused = refids - hrefs
    if unused:
        print("  uncited references:", sorted(unused))
    pdfs = re.findall(r'href="literature/([^"]+)"', html)
    absent = sorted({p for p in pdfs if not os.path.exists(os.path.join(root, "literature", p))})
    if absent:
        print("  MISSING files under literature/:", *absent, sep="\n    ")
        bad = True
    else:
        print(f"  all {len(set(pdfs))} linked literature files present")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
