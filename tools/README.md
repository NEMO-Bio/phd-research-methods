# tools: the literature fetcher and the essay build

Copied from `~/.claude/skills/research-essay/scripts/` so this project reproduces on its own.

## Literature

- **`resolve.py titles.txt`**: one paper title per line. Prints the Crossref DOI with a match score,
  first author, year and venue. Use it instead of guessing DOIs.
- **`fetch.py jobs.tsv outdir`**: jobs are `outname<TAB>id<TAB>verify_phrase`, where `id` is `doi:…`,
  `pmc:PMC…`, `arxiv:…`, `biorxiv:10.1101/…` or `url:…`. Tries, in order: EuropePMC by DOI, Unpaywall,
  OpenAlex, Semantic Scholar, CORE, the EuropePMC full-text list, and bioRxiv direct. **Every download is
  verified** by extracting page 1 with `pdftotext` and matching the phrase, and rejected files are
  deleted. That check has caught a wrong-paper PMCID returned by a DOI lookup, so do not remove it.
- **`pmcget.py PMCID out.pdf`**: PMC's PDF viewer answers with a proof-of-work challenge instead of the
  file. This solves it (sha256 over challenge+nonce until the hash starts with N zeros, answer returned
  as the `cloudpmc-viewer-pow` cookie) and returns the PDF. `fetch.py` calls it automatically.

Set `LIT_EMAIL` to override the contact address sent to Crossref, Unpaywall and OpenAlex.

Rungs the scripts do not cover: author copies, institutional repositories, the Internet Archive, and
your own institutional access. Try those by hand before an item goes to `literature/NEEDED.md`, and
record in `literature/README.md` how anything unusual was obtained.

```bash
python3 tools/resolve.py titles.txt
python3 tools/fetch.py jobs.tsv literature/
```

## The essay

- **`renumber.py src/`** (or `renumber.py essay.html`): rewrites every `<sup class="c">` citation number
  from the order of the reference list. Run it before every build.
- **`build.py src/ [out.html]`**: concatenates `src/part*.html` and `src/refs.html`, inlines
  `figures/*.svg` at each `<!--FIG:name … -->` placeholder with theme-aware colours and namespaced ids,
  numbers the figures, then reports dangling anchors, uncited references and missing PDFs.
- **`check.py essay.html`**: the quality gate on the finished file: citation numbering, anchors,
  duplicate ids, literature links, SVG labels outside their viewBox, external resources, the theme
  blocks, tag balance, em dashes, and a structure summary. Exit status 1 on a hard failure.

```bash
python3 tools/renumber.py src/ && python3 tools/build.py src/ && python3 tools/check.py <project>.html
```
