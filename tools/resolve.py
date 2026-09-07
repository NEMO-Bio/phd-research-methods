#!/usr/bin/env python3
"""Resolve paper titles to DOIs via Crossref, print DOI + matched title + year + journal + OA status."""
import json, os, sys, urllib.parse, urllib.request, difflib

def _contact_email():
    """Crossref, Unpaywall and OpenAlex all ask for a contact address in the polite pool.

    LIT_EMAIL wins. Otherwise fall back to the machine's git identity, which is what a
    researcher running this from a checkout almost always has set.
    """
    e = os.environ.get("LIT_EMAIL")
    if e:
        return e
    try:
        import subprocess as _sp
        e = _sp.run(["git", "config", "--get", "user.email"],
                    capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        e = ""
    if not e:
        sys.exit("set LIT_EMAIL to your email address (the OA APIs ask for a contact "
                 "in their polite pool), or configure git user.email")
    return e


EMAIL = _contact_email()
UA = {"User-Agent": f"lit-resolver/1.0 (mailto:{EMAIL})"}


def jget(url, timeout=45):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        return {"__err__": f"{type(e).__name__}: {e}"}


def norm(s):
    return " ".join("".join(c.lower() if c.isalnum() or c.isspace() else " " for c in s).split())


if len(sys.argv) < 2:
    sys.exit("usage: resolve.py titles.txt   (one paper title per line, # comments allowed)")

for raw in open(sys.argv[1]):
    q = raw.strip()
    if not q or q.startswith("#"):
        continue
    url = ("https://api.crossref.org/works?rows=5&select=DOI,title,issued,container-title,author"
           "&query.bibliographic=" + urllib.parse.quote(q) + f"&mailto={EMAIL}")
    d = jget(url)
    items = (d.get("message") or {}).get("items") or []
    if not items:
        print(f"NONE\t{q}\t{d.get('__err__','')}")
        continue
    best, bs = None, -1
    for it in items:
        t = (it.get("title") or [""])[0]
        s = difflib.SequenceMatcher(None, norm(q), norm(t)).ratio()
        if s > bs:
            best, bs = it, s
    t = (best.get("title") or [""])[0]
    yr = ((best.get("issued") or {}).get("date-parts") or [[None]])[0][0]
    jr = (best.get("container-title") or [""])[0]
    a = (best.get("author") or [{}])[0].get("family", "")
    tag = "OK " if bs > 0.72 else "LOW"
    print(f"{tag}\t{bs:.2f}\t{best['DOI']}\t{a}\t{yr}\t{jr[:38]}\t{t[:88]}")
