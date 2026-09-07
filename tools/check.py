#!/usr/bin/env python3
"""Quality gate for a finished standalone essay HTML.

    python3 check.py essay.html

Checks, in order of how often each has actually caught something:

  1. citation numbers agree with the order of the reference list
  2. dangling internal anchors, duplicate ids
  3. linked literature/ files that are not on disk
  4. <text> outside its <svg viewBox>, which is the clipped-label bug
  5. external resource references, which break the standalone guarantee
  6. the three theme blocks, <title>, viewport, description
  7. crude tag balance
  8. em dashes in prose (house style forbids them), semicolon density
  8b. svg typography: ASCII subscripts, groups with mixed text-anchor
  9. a size and structure summary against the calibration table

Exit status 1 if any hard check failed. Warnings do not fail the run.
"""
import os
import re
import sys

HARD, WARN = [], []


def hard(msg):
    HARD.append(msg)


def warn(msg):
    WARN.append(msg)


def strip_ref_list(html):
    """The document with the reference list removed (its own cross-links are not citations)."""
    i = html.find('<h2 id="refs"')
    return html if i < 0 else html[:i]


def prose_only(html):
    """Body prose only: style, script, svg and the reference list blanked out.

    Blanked regions keep their newlines, so reported line numbers still match the file.
    """
    blank = lambda m: "\n" * m.group(0).count("\n")
    for tag in ("style", "script", "svg"):
        html = re.sub(rf"<{tag}\b.*?</{tag}>", blank, html, flags=re.S)
    i = html.find('<h2 id="refs"')
    return html if i < 0 else html[:i]


def check_citations(html):
    order = re.findall(r'<li id="(r-[^"]+)"', html)
    num = {rid: i + 1 for i, rid in enumerate(order)}
    dupes = sorted({r for r in order if order.count(r) > 1})
    if dupes:
        hard(f"duplicate reference ids: {dupes}")
    # any link into the reference list counts as a citation; only sup.c numbers are checked
    seen = set(re.findall(r'<a[^>]*\shref="#(r-[^"]+)"', strip_ref_list(html)))
    wrong, unknown = [], set()
    for rid, shown in re.findall(r'<sup class="c">.*?<a href="#(r-[^"]+)">([^<]*)</a>', html, re.S):
        seen.add(rid)
        if rid not in num:
            unknown.add(rid)
        elif shown.strip() != str(num[rid]):
            wrong.append(f"{rid} shows {shown!r}, should be {num[rid]}")
    if unknown:
        hard(f"citations to unknown reference ids: {sorted(unknown)}")
    if wrong:
        hard("citation numbers out of order (run renumber.py): " + "; ".join(wrong[:8])
             + (f" … and {len(wrong)-8} more" if len(wrong) > 8 else ""))
    uncited = [r for r in order if r not in seen]
    if uncited:
        warn(f"uncited references: {uncited}")
    return len(order), len(seen)


def check_anchors(html):
    ids = re.findall(r'\sid="([^"]+)"', html)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        hard(f"duplicate ids: {dupes}")
    targets = set(ids)
    hrefs = set(re.findall(r'<a[^>]*\shref="#([^"]+)"', html))
    missing = sorted(hrefs - targets)
    if missing:
        hard(f"dangling anchors: {missing}")


def check_literature(html, root):
    linked = sorted(set(re.findall(r'href="literature/([^"#?]+)"', html)))
    lit = os.path.join(root, "literature")
    if linked and not os.path.isdir(lit):
        # checking a file away from its project, or a template not yet filled in
        warn(f"no literature/ directory beside this file, so {len(linked)} link(s) go nowhere")
        linked = []
    absent = [p for p in linked if not os.path.exists(os.path.join(lit, p))]
    if absent:
        hard("linked literature files missing on disk:\n    " + "\n    ".join(absent))
    needed = len(re.findall(r'class="pdf no"', html))
    if needed:
        warn(f"{needed} reference(s) still badged NEEDED; keep literature/NEEDED.md current")
    return len(linked)


def check_svg_text(html):
    """Flag <text> whose anchor sits outside the viewBox. Catches clipped labels."""
    bad = 0
    for m in re.finditer(r'<svg[^>]*viewBox="([-\d.\s]+)"(.*?)</svg>', html, re.S):
        try:
            x0, y0, w, h = [float(v) for v in m.group(1).split()]
        except ValueError:
            continue
        body = m.group(2)
        if "matplotlib" in body[:400]:      # generated plots place text by transform
            continue
        # text inside a transformed <g> is in another coordinate frame; skip it
        moved, depth = [], 0
        for t in re.finditer(r'<g\b([^>]*)>|</g>|<text\b([^>]*)>', body):
            tok = t.group(0)
            if tok.startswith("</g"):
                if moved:
                    moved.pop()
                continue
            if tok.startswith("<g"):
                moved.append("transform" in (t.group(1) or ""))
                continue
            attrs = t.group(2) or ""
            if any(moved) or "transform" in attrs:
                continue
            xs = re.search(r'\bx="(-?[\d.]+)"', attrs)
            ys = re.search(r'\by="(-?[\d.]+)"', attrs)
            if not xs or not ys:
                continue
            x, y = float(xs.group(1)), float(ys.group(1))
            if not (x0 - 1 <= x <= x0 + w + 1) or not (y0 - 1 <= y <= y0 + h + 1):
                bad += 1
                if bad <= 6:
                    warn(f"svg text anchored outside viewBox at x={x:g} y={y:g} "
                         f"(viewBox {x0:g} {y0:g} {w:g} {h:g})")
    if bad > 6:
        warn(f"… and {bad - 6} more svg labels outside their viewBox")


def check_svg_typography(html):
    """Two figure bugs a browser would show you and the source will not.

    ASCII subscripts render as literal underscores. And a group where some labels set
    text-anchor and their siblings do not is how a centred title ends up with a subtitle
    that starts at the title's midpoint and runs off the right edge.
    """
    ascii_subs = set()
    for t in re.finditer(r"<text\b[^>]*>(.*?)</text>", html, re.S):
        plain = re.sub(r"<[^>]+>", "", t.group(1))
        for m in re.finditer(r"\b([A-Za-z\u03b1-\u03c9])_([A-Za-z0-9]{1,4})\b", plain):
            ascii_subs.add(m.group(0))
    if ascii_subs:
        warn(f"ASCII subscripts in svg labels, use a <tspan dy> pair instead: "
             f"{sorted(ascii_subs)[:8]}")

    # the precise bug: two labels share an x, one is anchored and the other is not, so the
    # unanchored one starts where the anchored one is centred. Labels at different x are
    # simply placed differently and are none of our business.
    mixed = []
    for g in re.finditer(r"<g\b([^>]*)>(.*?)</g>", html, re.S):
        if "text-anchor" in (g.group(1) or ""):     # inherited from the group, fine
            continue
        inner = g.group(2)
        if "<g" in inner:                           # only look at leaf groups
            continue
        by_x = {}
        for t in re.finditer(r"<text\b([^>]*)>(.*?)</text>", inner, re.S):
            attrs = t.group(1)
            xm = re.search(r'\bx="(-?[\d.]+)"', attrs)
            if not xm:
                continue
            by_x.setdefault(xm.group(1), []).append(
                ("text-anchor" in attrs, re.sub(r"<[^>]+>", "", t.group(2)).strip()[:28]))
        for x, group in by_x.items():
            if len(group) > 1 and any(a for a, _ in group) and not all(a for a, _ in group):
                mixed.append(next(s for a, s in group if not a))
    if mixed:
        warn(f"{len(mixed)} svg label(s) share an x with an anchored sibling but set no "
             f"text-anchor, so they start where the sibling is centred: {mixed[:5]}")

    # Inline SVG class selectors participate in the page-wide cascade. A figure
    # class such as .m used to override the essay's inline-math class and enlarge
    # ordinary prose. Generated figure classes must carry their fN- namespace.
    unscoped = set()
    for svg in re.findall(r'<svg\b.*?</svg>', html, re.S):
        for style in re.findall(r'<style\b[^>]*>(.*?)</style>', svg, re.S):
            for cls in re.findall(r'(?<![\w-])\.([A-Za-z_][\w-]*)', style):
                if not re.match(r'f\d+-', cls):
                    unscoped.add(cls)
    if unscoped:
        hard(f"unscoped inline SVG CSS classes can leak into prose: {sorted(unscoped)}")


# <link rel=...> values that are metadata, not a resource the page loads
META_REL = {"canonical", "alternate", "author", "license", "me", "prev", "next"}


def check_standalone(html):
    ext = set()
    for m in re.finditer(r'<(script|link|img|iframe)\b([^>]*)>', html):
        tag, attrs = m.group(1), m.group(2)
        url = re.search(r'\b(?:src|href)="(https?://[^"]+)"', attrs)
        if not url:
            continue
        rel = re.search(r'\brel="([^"]*)"', attrs)
        if tag == "link" and rel and set(rel.group(1).split()) & META_REL:
            continue        # canonical URL, feed, licence: never fetched
        ext.add(url.group(1))
    if ext:
        hard(f"external resources break the standalone guarantee: {sorted(ext)[:5]}")
    if re.search(r'@import\s+url\(https?://', html):
        hard("@import of a remote stylesheet")


def check_head(html):
    if not re.search(r"<title>[^<]+</title>", html):
        hard("no <title>")
    if 'name="viewport"' not in html:
        hard("no viewport meta")
    if 'name="description"' not in html:
        warn("no description meta")
    if "prefers-color-scheme: dark" not in html:
        hard("no @media (prefers-color-scheme: dark) block")
    if '[data-theme="dark"]' not in html or '[data-theme="light"]' not in html:
        hard("theme toggle needs both :root[data-theme=\"dark\"] and [data-theme=\"light\"] blocks")
    if 'id="tt"' not in html:
        warn("no theme-toggle button")
    if "MathJax" in html or "katex" in html.lower():
        warn("MathJax/KaTeX present; house style uses .m spans and .eq blocks")


def check_balance(html):
    for tag in ("div", "figure", "table", "svg", "main", "nav", "blockquote", "script", "style"):
        o = len(re.findall(rf"<{tag}\b", html))
        c = len(re.findall(rf"</{tag}>", html))
        if o != c:
            hard(f"<{tag}> opened {o} times, closed {c}")


def check_prose(html):
    body = prose_only(html)
    lines = body.split("\n")
    dashes = [i + 1 for i, L in enumerate(lines)
              if ("—" in L or " -- " in L) and not L.lstrip().startswith("<!--")]
    if dashes:
        warn(f"em dashes on {len(dashes)} line(s) (house style forbids them): "
             f"{dashes[:12]}{' …' if len(dashes) > 12 else ''}")
    semis = len(re.findall(r"[a-z];\s+[a-z]", body))
    if semis > 12:
        warn(f"{semis} sentence-joining semicolons; house style keeps these rare")


def summary(html, refs, cited, linked):
    n = {
        "sections": len(re.findall(r'<h2 id="s', html)),
        "parts": len(re.findall(r'class="parthead"', html)),
        "figures": len(re.findall(r"<figure", html)),
        "tables": len(re.findall(r"<table", html)),
        "boxes": len(re.findall(r'class="box ', html)),
        "demos": len(re.findall(r"<canvas", html)),
        "equations": len(re.findall(r'class="eq"', html)),
        "citations": len(re.findall(r'<sup class="c">', html)),
    }
    print("  " + "  ".join(f"{k}={v}" for k, v in n.items()))
    print(f"  references={refs} (cited {cited})  literature links={linked}")
    if n["sections"] < 12:
        warn(f"{n['sections']} sections; finished essays run 21 to 27")
    if n["figures"] < 4:
        warn(f"{n['figures']} figures; finished essays run 5 to 10")


def main():
    path = os.path.abspath(sys.argv[1])
    root = os.path.dirname(path)
    html = open(path, encoding="utf-8").read()
    print(f"{path}  ({os.path.getsize(path)/1024:.0f} kB, {html.count(chr(10))+1} lines)")

    refs, cited = check_citations(html)
    check_anchors(html)
    linked = check_literature(html, root)
    check_svg_text(html)
    check_svg_typography(html)
    check_standalone(html)
    check_head(html)
    check_balance(html)
    check_prose(html)
    summary(html, refs, cited, linked)

    for m in WARN:
        print("  warn:  " + m)
    for m in HARD:
        print("  FAIL:  " + m)
    if HARD:
        print(f"\n{len(HARD)} hard failure(s), {len(WARN)} warning(s)")
        return 1
    print(f"\nclean ({len(WARN)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
