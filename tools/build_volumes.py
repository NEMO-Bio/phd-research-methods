#!/usr/bin/env python3
"""Build the handbook as three linked, self-contained reading volumes."""
import os
import re
import sys

from build import FIG_RE, load_svg


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
FIGURES = os.path.join(ROOT, "figures")
REFERENCE_VOLUME = "03-execution-and-boundaries.html"

VOLUMES = [
    {
        "file": "index.html",
        "number": "第一册",
        "title": "基础框架",
        "subtitle": "Part I–II · 研究者、AI 与四项核心训练的统一模型",
        "sources": ["part1.html"],
        "include_intro": True,
        "toc": [
            ("part", "I 研究者如何被培养"),
            ("section", "s1", "1 五年积累目标"),
            ("section", "s2", "2 AI 改变了什么"),
            ("section", "s3", "3 个人主动发展与培养环境"),
            ("part", "II 统一模型"),
            ("section", "s4", "4 四类研究能力"),
            ("section", "s5", "5 AI 贯穿层"),
            ("section", "s6", "6 对研究结论负责"),
            ("section", "s7", "7 双重产出"),
        ],
    },
    {
        "file": "02-four-core-trainings.html",
        "number": "第二册",
        "title": "四项核心训练",
        "subtitle": "Part III · 听、说、读、写",
        "sources": ["part2.html", "part3.html"],
        "include_intro": False,
        "toc": [
            ("part", "III 四项核心训练"),
            ("subpart", "听：在现场重建问题"),
            ("section", "s8", "8 论证结构"),
            ("section", "s9", "9 Seminar 与 Journal Club"),
            ("subpart", "说：让研究成为共同对象"),
            ("section", "s10", "10 科研表达"),
            ("section", "s11", "11 未成形想法"),
            ("section", "s12", "12 研究汇报"),
            ("section", "s13", "13 English speaker"),
            ("subpart", "读：从领域到证据"),
            ("section", "s14", "14 领域雷达"),
            ("section", "s15", "15 阅读合同"),
            ("section", "s16", "16 逐图审证据"),
            ("section", "s17", "17 读后转化与 AI"),
            ("subpart", "写：从过程到论文"),
            ("section", "s18", "18 研究过程写作"),
            ("section", "s19", "19 方法论文证据门槛"),
            ("section", "s20", "20 投稿前检查"),
        ],
    },
    {
        "file": REFERENCE_VOLUME,
        "number": "第三册",
        "title": "执行与边界",
        "subtitle": "Part IV–V · 把方法放进日常，并持续校正它",
        "sources": ["part4.html", "part5.html"],
        "include_intro": False,
        "toc": [
            ("part", "IV 执行系统"),
            ("section", "s21", "21 多时间尺度"),
            ("section", "s22", "22 五年发展"),
            ("section", "s23", "23 评价仪表盘"),
            ("part", "V 边界与开始"),
            ("section", "s24", "24 何时不用 AI"),
            ("section", "s25", "25 证据边界"),
            ("section", "refs", "参考文献"),
        ],
    },
]

EXTRA_CSS = """
<style>
.toc .volume-list{list-style:none;padding:0;margin:0 0 1.25rem}.toc .volume-list a{display:block;padding:.45rem .55rem;margin:.25rem 0;border:1px solid var(--rule);border-radius:7px;font-weight:700;color:var(--muted);text-decoration:none}.toc .volume-list a:hover,.toc .volume-list a.current{color:var(--fg);border-color:var(--peri);background:var(--lavender)}.toc .toc-label{margin:1.3rem 0 .65rem}.pager{display:grid;grid-template-columns:1fr auto 1fr;gap:.8rem;align-items:center;border-top:1px solid var(--rule);margin:4.5rem 0 0;padding-top:1.2rem;font:700 .86rem/1.4 var(--sans)}.pager a{color:var(--fg);text-decoration:none}.pager a:last-child{text-align:right}.pager .pager-state{color:var(--muted);font-weight:500}.pager .disabled{visibility:hidden}
@media(max-width:650px){.pager{grid-template-columns:1fr 1fr}.pager .pager-state{display:none}}
</style>
"""


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def shell():
    source = read("part0.html")
    prefix = source[:source.index('<header class="cover">')]
    prefix = prefix.replace("</head>", EXTRA_CSS + "</head>")
    intro = source[source.index("<main>") + len("<main>"):]
    ref_source = read("refs.html")
    footer = ref_source[ref_source.rindex("</main>"):]
    footer = footer.replace('document.querySelectorAll(\'#toc a\')',
                            'document.querySelectorAll(\'#toc a[href^="#"]\')')
    return prefix, intro, footer


def cover(volume):
    if volume["include_intro"]:
        return """<header class="cover">
  <div class="eyebrow">AI 时代研究者训练手册 v1.4</div>
  <h1>博士研究的工作方法与准则</h1>
  <p class="sub">本手册借用语言学习中“听、说、读、写”的分类，归纳博士阶段最核心的四类研究能力：从讲授与交流中理解问题，把想法和证据说清，从文献中重建论证，以及用记录与论文积累可检验的成果。它适用于不同科研学习阶段，尤其面向 AI 已深度进入检索、分析和写作流程的研究生。</p>
  <p class="byline">作者：Tao Zhu (Westlake Uni.)</p>
</header>"""
    return f"""<header class="cover">
  <div class="eyebrow">博士研究的工作方法与准则</div>
  <h1>{volume["number"]}：{volume["title"]}</h1>
  <p class="sub">{volume["subtitle"]}</p>
  <p class="byline">三册手册中的一册 · 可从左侧切换，也可在文末前后翻阅</p>
</header>"""


def nav(volume_index):
    volume = VOLUMES[volume_index]
    volume_links = []
    for i, item in enumerate(VOLUMES):
        current = " current" if i == volume_index else ""
        volume_links.append(
            f'<li><a class="{current.strip()}" href="{item["file"]}">{item["number"]}：{item["title"]}</a></li>'
        )
    entries = []
    for item in volume["toc"]:
        if item[0] == "section":
            entries.append(f'<li><a href="#{item[1]}">{item[2]}</a></li>')
        else:
            entries.append(f'<li class="{item[0]}">{item[1]}</li>')
    return f"""<nav class="toc" id="toc" aria-label="手册目录">
  <div class="brand">AI-Native Research Methods</div>
  <h2>三册导航</h2>
  <ul class="volume-list">{''.join(volume_links)}</ul>
  <h2 class="toc-label">本册目录</h2>
  <ul class="section-list">{''.join(entries)}</ul>
</nav>"""


def pager(volume_index):
    previous = VOLUMES[volume_index - 1] if volume_index else None
    following = VOLUMES[volume_index + 1] if volume_index + 1 < len(VOLUMES) else None
    left = (f'<a href="{previous["file"]}">← {previous["number"]}</a>'
            if previous else '<span class="disabled">←</span>')
    right = (f'<a href="{following["file"]}">{following["number"]} →</a>'
             if following else '<span class="disabled">→</span>')
    return (f'<nav class="pager" aria-label="前后翻阅">{left}'
            f'<span class="pager-state">{VOLUMES[volume_index]["number"]} · '
            f'{VOLUMES[volume_index]["title"]}</span>{right}</nav>')


def inline_figures(html):
    count = 0

    def sub(match):
        nonlocal count
        count += 1
        name, caption = match.group(1), match.group(2).strip()
        svg = load_svg(FIGURES, name, f"f{count}")
        return f'<figure class="figbox" id="{name}">\n{svg}\n<figcaption>{caption}</figcaption>\n</figure>'

    return FIG_RE.sub(sub, html), count


def public_links(html):
    """Replace private local verification copies with public source links."""
    html = re.sub(
        r'(DOI: )([^<]+?)(\.)</span><a class="pdf" href="literature/[^"]+">PDF</a>',
        lambda m: f'{m.group(1)}{m.group(2)}{m.group(3)}</span>'
                  f'<a class="pdf" href="https://doi.org/{m.group(2)}" '
                  'target="_blank" rel="noopener">DOI</a>',
        html,
    )
    replacements = {
        'literature/MaherEtAl-2013-cognitive-apprenticeship-research-supervision.pdf':
            'https://jrp.icaap.org/index.php/jrp/article/view/354.html',
        'source-snapshots/howtogiveatalk-structure.html':
            'https://www.howtogiveatalk.com/blog/the-structure-of-an-effective-talk',
        'source-snapshots/howtogiveatalk-qa.html':
            'https://www.howtogiveatalk.com/blog/navigating-the-qa',
        'source-snapshots/pebble-ai-native-method.html':
            'https://pebble-biofusion.github.io/workshop/method',
    }
    for local, url in replacements.items():
        html = html.replace(f'href="{local}"',
                            f'href="{url}" target="_blank" rel="noopener"')
    return html


def reference_bank():
    """Read the verified source entries without copying the page shell."""
    source = read("refs.html")
    return {
        key: item
        for key, item in re.findall(r'<li id="(r-[^"]+)">(.*?)</li>', source, flags=re.S)
    }


def localize_references(content, bank, full_index=False):
    """Give each volume continuous citations and its own reference appendix."""
    keys = []
    for key in re.findall(r'href="#(r-[^"]+)"', content):
        if key not in keys:
            keys.append(key)
    missing = [key for key in keys if key not in bank]
    if missing:
        raise RuntimeError(f"unknown reference keys: {missing}")
    if full_index:
        keys = list(bank)
    numbers = {key: i + 1 for i, key in enumerate(keys)}
    content = re.sub(
        r'(<a href="#(r-[^"]+)">)\d+(</a>)',
        lambda m: f'{m.group(1)}{numbers[m.group(2)]}{m.group(3)}',
        content,
    )
    entries = ''.join(f'<li id="{key}">{bank[key]}</li>' for key in keys)
    heading = "完整参考文献索引" if full_index else "本册参考文献"
    appendix = (f'<section class="refs volume-refs"><h2 id="refs">{heading}</h2>'
                f'<ol>{entries}</ol></section>')
    return content + appendix


def validate(pages):
    expected = {item["file"] for item in VOLUMES}
    for name, html in pages.items():
        if "<!--FIG:" in html:
            raise RuntimeError(f"{name}: unresolved figure placeholder")
        targets = set(re.findall(r'<h2 id="([^"]+)"', html))
        targets |= set(re.findall(r'<figure[^>]*id="([^"]+)"', html))
        targets |= set(re.findall(r'<li id="(r-[^"]+)"', html))
        locals_ = re.findall(r'<a[^>]*href="#([^"]+)"', html)
        missing = sorted(set(locals_) - targets)
        if missing:
            raise RuntimeError(f"{name}: dangling local anchors {missing}")
        files = set(re.findall(r'<a[^>]*href="([^"#]+)#[^"]+"', html))
        if not files <= expected:
            raise RuntimeError(f"{name}: unexpected cross-volume links {sorted(files - expected)}")
        cited = set(re.findall(r'href="#(r-[^"]+)"', html))
        reference_ids = set(re.findall(r'<li id="(r-[^"]+)"', html))
        if name == REFERENCE_VOLUME:
            if not cited <= reference_ids:
                raise RuntimeError(f"{name}: citations missing from full reference index")
        elif cited != reference_ids:
            raise RuntimeError(
                f"{name}: citation/reference mismatch: "
                f"uncited={sorted(reference_ids - cited)}, missing={sorted(cited - reference_ids)}"
            )
    if sum(html.count("<figure") for html in pages.values()) != 1:
        raise RuntimeError("the three volumes should contain exactly one retained figure")
    if any("<caption" in html for html in pages.values()):
        raise RuntimeError("table captions must be outside table containers")
    if sum(html.count('class="table-note"') for html in pages.values()) != 4:
        raise RuntimeError("expected four table notes outside their tables")


def main():
    prefix, intro, footer = shell()
    pages = {}
    bank = reference_bank()
    for index, volume in enumerate(VOLUMES):
        pieces = []
        for name in volume["sources"]:
            piece = read(name)
            pieces.append(piece)
        content = "".join(pieces)
        content, count = inline_figures(content)
        content = localize_references(content, bank,
                                      full_index=volume["file"] == REFERENCE_VOLUME)
        content = public_links(content)
        title = f'博士研究的工作方法与准则｜{volume["number"]}：{volume["title"]}'
        page_prefix = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', prefix, count=1)
        html = page_prefix + cover(volume) + nav(index) + "<main>\n"
        if volume["include_intro"]:
            html += intro + "\n"
        html += content + pager(index) + "\n" + footer
        pages[volume["file"]] = html
        print(f"prepared {volume['file']} ({len(html) / 1024:.0f} kB, {count} figure(s))")

    validate(pages)
    for name, html in pages.items():
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(html)
    print(f"wrote {len(pages)} linked volumes")


if __name__ == "__main__":
    main()
