#!/usr/bin/env python3
"""Fetch a free-to-read PMC PDF, solving the viewer's rate-limit proof-of-work if presented.

The PoW is NCBI's throttle on their PDF viewer: sha256(challenge + nonce) must start with
`difficulty` hex zeros; the answer goes back as the cloudpmc-viewer-pow cookie. Low volume,
one request per article, with a pause between articles.
"""
import hashlib, http.cookiejar, re, sys, time, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "application/pdf,text/html,*/*"}


def solve(challenge, difficulty):
    target = "0" * int(difficulty)
    n = 0
    while True:
        if hashlib.sha256((challenge + str(n)).encode()).hexdigest().startswith(target):
            return n
        n += 1


def get_pmc_pdf(pmcid, timeout=90):
    pmcid = pmcid if pmcid.upper().startswith("PMC") else "PMC" + pmcid
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = list(UA.items())
    url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/"
    for _ in range(3):
        with op.open(url, timeout=timeout) as r:
            body = r.read()
        if body[:4] == b"%PDF":
            return body
        html = body.decode("utf-8", "replace")
        m = re.search(r'POW_CHALLENGE\s*=\s*"([^"]+)"', html)
        d = re.search(r'POW_DIFFICULTY\s*=\s*"?(\d+)"?', html)
        c = re.search(r'POW_COOKIE_NAME\s*=\s*"([^"]+)"', html)
        if not m:
            return None
        nonce = solve(m.group(1), d.group(1) if d else 4)
        ck = http.cookiejar.Cookie(
            0, c.group(1) if c else "cloudpmc-viewer-pow",
            f"{m.group(1)},{nonce}", None, False,
            "pmc.ncbi.nlm.nih.gov", False, False, "/", True,
            True, None, False, None, None, {})
        cj.set_cookie(ck)
        time.sleep(1)
    return None


if __name__ == "__main__":
    b = get_pmc_pdf(sys.argv[1])
    if b:
        open(sys.argv[2], "wb").write(b)
        print("OK", len(b))
    else:
        print("FAIL")
