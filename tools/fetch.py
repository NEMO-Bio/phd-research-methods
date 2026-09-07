#!/usr/bin/env python3
"""Fetch open-access full texts by DOI / PMID / arXiv id, verify, and name them.

Usage:  python3 fetch.py jobs.tsv
jobs.tsv columns (tab separated):  outname <TAB> id <TAB> verify_phrase
  id can be:  doi:10.xxxx/yyy | pmc:PMC1234567 | arxiv:2301.01234 | biorxiv:10.1101/... | url:https://...
verify_phrase is a distinctive lowercase phrase expected on page 1-2 (spaces collapsed).
"""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pmcget

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
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "application/pdf,text/html,*/*"}


def get(url, timeout=90, headers=None, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers or UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), r.geturl(), r.headers.get("Content-Type", "")
        except Exception as e:
            last = e
            code = getattr(e, "code", None)
            if code in (400, 401, 403, 404, 410):
                break
            time.sleep(2 + 3 * i)
    raise last


def jget(url, timeout=45):
    try:
        b, _, _ = get(url, timeout)
        return json.loads(b.decode("utf-8", "replace"))
    except Exception:
        return None


DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−­"), "-")


def norm(s):
    s = s.translate(DASHES)
    s = s.replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"[^a-z0-9 ]+", " ", re.sub(r"\s+", " ", s.lower()))


def pmc_urls(pid):
    pid = pid if str(pid).upper().startswith("PMC") else "PMC" + str(pid)
    return [f"pmc://{pid}",
            f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pid}&blobtype=pdf",
            f"https://europepmc.org/articles/{pid}?pdf=render"]


def verify(path, phrase):
    if not os.path.exists(path) or os.path.getsize(path) < 20000:
        return False, "too small"
    with open(path, "rb") as f:
        if f.read(5)[:4] != b"%PDF":
            return False, "not a pdf"
    if not phrase:
        return True, "no phrase check"
    try:
        txt = subprocess.run(["pdftotext", "-f", "1", "-l", "3", path, "-"],
                             capture_output=True, timeout=90).stdout.decode("utf-8", "replace")
    except Exception as e:
        return False, f"pdftotext failed {e}"
    return (norm(phrase) in norm(txt)), "phrase " + ("found" if norm(phrase) in norm(txt) else "MISSING")


def candidates(ident):
    """Yield candidate PDF urls for an identifier."""
    kind, _, val = ident.partition(":")
    if kind == "url":
        yield ident[4:]
        return
    if kind == "arxiv":
        yield f"https://arxiv.org/pdf/{val}"
        return
    if kind == "pmc":
        yield from pmc_urls(val)
        return
    if kind == "doi":
        doi = val
        # 0. EuropePMC by DOI first (most reliable for PMC-deposited works)
        ep = jget("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%22"
                  + urllib.parse.quote(doi) + "%22&format=json&resultType=core")
        try:
            for res in ep["resultList"]["result"][:3]:
                if res.get("pmcid"):
                    yield from pmc_urls(res["pmcid"])
        except Exception:
            pass
        # 1. Unpaywall
        up = jget(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={EMAIL}")
        if up:
            locs = []
            if up.get("best_oa_location"):
                locs.append(up["best_oa_location"])
            locs += up.get("oa_locations") or []
            for L in locs:
                for k in ("url_for_pdf", "url"):
                    u = L.get(k)
                    if u:
                        yield u
        # 2. OpenAlex
        oa = jget(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}?mailto={EMAIL}")
        if oa:
            for L in ([oa.get("best_oa_location")] + (oa.get("locations") or [])):
                if L and L.get("pdf_url"):
                    yield L["pdf_url"]
            ids = oa.get("ids") or {}
            if ids.get("pmid"):
                pmid = ids["pmid"].rsplit("/", 1)[-1]
                conv = jget("https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
                            f"?ids={pmid}&format=json&tool=lit&email={EMAIL}")
                try:
                    yield from pmc_urls(conv["records"][0]["pmcid"])
                except Exception:
                    pass
        # 2b. Semantic Scholar open-access PDF
        s2 = jget("https://api.semanticscholar.org/graph/v1/paper/DOI:"
                  + urllib.parse.quote(doi) + "?fields=openAccessPdf,externalIds")
        try:
            if s2 and s2.get("openAccessPdf", {}).get("url"):
                yield s2["openAccessPdf"]["url"]
            ax = (s2 or {}).get("externalIds", {}).get("ArXiv")
            if ax:
                yield f"https://arxiv.org/pdf/{ax}"
        except Exception:
            pass
        # 2c. CORE aggregator
        try:
            c = jget("https://core.ac.uk/search-api/works?q=doi:%22"
                     + urllib.parse.quote(doi) + "%22&limit=3")
            for w in (c or {}).get("results", [])[:3]:
                if w.get("downloadUrl"):
                    yield w["downloadUrl"]
        except Exception:
            pass
        # 3. EuropePMC full-text url list
        try:
            for res in ep["resultList"]["result"][:3]:
                for ft in (res.get("fullTextUrlList") or {}).get("fullTextUrl", []):
                    if ft.get("documentStyle") == "pdf":
                        yield ft["url"]
        except Exception:
            pass
        # 4. bioRxiv / medRxiv direct
        if doi.startswith("10.1101/"):
            yield f"https://www.biorxiv.org/content/{doi}v1.full.pdf"
            yield f"https://www.medrxiv.org/content/{doi}v1.full.pdf"


def fetch_one(outname, ident, phrase):
    path = os.path.join(OUT, outname)
    if os.path.exists(path) and os.path.getsize(path) > 20000:
        ok, why = verify(path, phrase)
        if ok:
            return "EXISTS", path, ""
    seen = set()
    last = ""
    for u in candidates(ident):
        if not u or u in seen:
            continue
        m = re.search(r"ncbi\.nlm\.nih\.gov/pmc/articles/(PMC)?(\d+)", u)
        if m:
            u = "pmc://PMC" + m.group(2)
        if u in seen:
            continue
        seen.add(u)
        try:
            if u.startswith("pmc://"):
                body = pmcget.get_pmc_pdf(u[6:]) or b""
                final, ctype = u, "application/pdf"
                time.sleep(1)
            else:
                body, final, ctype = get(u)
        except Exception as e:
            last = f"{u} -> {type(e).__name__}"
            continue
        if body[:4] != b"%PDF":
            # maybe a landing page with a meta citation_pdf_url
            try:
                html = body.decode("utf-8", "replace")
                m = re.search(r'name="citation_pdf_url"\s+content="([^"]+)"', html)
                if m:
                    try:
                        body, final, ctype = get(m.group(1))
                    except Exception as e:
                        last = f"{m.group(1)} -> {type(e).__name__}"
                        continue
            except Exception:
                pass
        if body[:4] != b"%PDF":
            last = f"{u} -> not pdf ({ctype[:40]})"
            continue
        with open(path, "wb") as f:
            f.write(body)
        ok, why = verify(path, phrase)
        if ok:
            return "OK", path, u
        os.remove(path)
        last = f"{u} -> {why}"
    return "FAIL", path, last


def main():
    jobs = []
    if len(sys.argv) < 2:
        sys.exit("usage: fetch.py jobs.tsv [outdir]   "
                 "(each line: outname<TAB>id<TAB>verify_phrase)")
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            while len(parts) < 3:
                parts.append("")
            jobs.append(parts[:3])
    for outname, ident, phrase in jobs:
        status, path, note = fetch_one(outname.strip(), ident.strip(), phrase.strip())
        print(f"{status}\t{outname}\t{note}", flush=True)


if __name__ == "__main__":
    main()
