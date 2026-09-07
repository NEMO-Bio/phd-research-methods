#!/usr/bin/env python3
"""Renumber citations to match the order of the reference list.

    python3 renumber.py src/          # parts mode: order from src/refs.html
    python3 renumber.py essay.html    # single-file mode: order from the file itself

Citations are written by hand as

    <sup class="c"><a href="#r-foo">41</a></sup>

and the number has to equal the position of <li id="r-foo"> in the reference list. Keeping
that by hand breaks the moment a reference is inserted, so this rewrites every citation
from the list. While drafting, write the number as ? and let this fill it in.

Run before build.py. Reports duplicate reference ids, citations to unknown ids, and
references nothing cites.
"""
import os
import re
import sys

CIT = re.compile(r'(<sup class="c">)(.*?)(</sup>)', re.S)
LINK = re.compile(r'<a href="#(r-[^"]+)">([^<]*)</a>')


def part_order(name):
    m = re.search(r"part(\d+)", name)
    return (0, int(m.group(1)) if m else 0, name)


def main():
    target = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "src")
    if os.path.isdir(target):
        refs = open(os.path.join(target, "refs.html")).read()
        files = [os.path.join(target, f) for f in sorted(
            (f for f in os.listdir(target) if f.startswith("part") and f.endswith(".html")),
            key=part_order)]
        files.append(os.path.join(target, "refs.html"))
    else:
        refs = open(target).read()
        files = [target]

    order = re.findall(r'<li id="(r-[^"]+)"', refs)
    num = {rid: i + 1 for i, rid in enumerate(order)}
    dupes = sorted({r for r in order if order.count(r) > 1})
    if dupes:
        print("  DUPLICATE reference ids:", dupes)

    changed, bad, seen = 0, set(), set()
    for path in files:
        s = open(path).read()

        def fix_sup(m):
            head, body, tail = m.groups()

            def fix_link(lm):
                nonlocal changed
                rid, old = lm.group(1), lm.group(2)
                seen.add(rid)
                if rid not in num:
                    bad.add(rid)
                    return lm.group(0)
                new = str(num[rid])
                if new != old:
                    changed += 1
                return f'<a href="#{rid}">{new}</a>'

            return head + LINK.sub(fix_link, body) + tail

        out = CIT.sub(fix_sup, s)
        if out != s:
            open(path, "w").write(out)

    if bad:
        print("  citations to unknown reference ids:", sorted(bad))
    uncited = [r for r in order if r not in seen]
    if uncited:
        print("  uncited references:", uncited)
    print(f"renumbered {changed} citation(s) against {len(order)} references "
          f"in {len(files)} file(s)")
    return 1 if bad or dupes else 0


if __name__ == "__main__":
    sys.exit(main())
