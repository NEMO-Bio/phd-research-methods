"""Generate the structural figures and counts used in the essay.

The values here are design choices in the proposed system, not empirical effect sizes.
Keeping them in code makes the structure inspectable and prevents hand-counting errors.
"""

from pathlib import Path
from html import escape


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"

MODALITIES = {
    "听": ["原话可定位", "笔记经对照", "脱稿可复述", "能提出区分性问题"],
    "说": ["素材有出处", "图表可重跑", "不用幻灯片也能讲", "问答能校准边界"],
    "读": ["全文已取得", "方法与图表已检查", "六问可回答", "能给替代解释"],
    "写": ["引文可回链", "数字来自代码", "论证可重建", "反馈已闭环"],
}

GATES = ["溯源", "复现", "理解", "答辩"]

STAGES = [
    ("1 标准化", "把工作做得可追溯", "四周后能重跑自己的结果"),
    ("2 独立执行", "独立推进一个子问题", "能提出计划、执行并解释偏差"),
    ("3 系统化", "形成领域地图与方法栈", "能把多项工作组织成研究主线"),
    ("4 原创", "提出可区分的新机制", "能设计让竞争解释分胜负的检验"),
    ("5 迁移与领导", "把个人能力变成团队能力", "能带人、教学并形成独立议程"),
]

CAPABILITIES = ["问题感", "论证与建模", "证据与方法", "执行与留痕", "表达与协作", "元认知"]


def ai_loop_svg() -> str:
    steps = [
        ("问题", "人定义目标与证据标准", "#e8f1ff"),
        ("AI 扩展", "检索、解释、候选、代码", "#f7e8f6"),
        ("核验与工作", "全文、推导、实验、重跑", "#e9f8f2"),
        ("输出与答辩", "写作、讲授、现场问答", "#fff4de"),
        ("反馈与留痕", "纠错、决策、版本、下一问", "#feeae4"),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 420">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#7d8995"/></marker></defs>',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;fill:#182230}.h{font-size:25px;font-weight:700}.t{font-size:18px;font-weight:700}.s{font-size:14px;fill:#536273}.a{stroke:#7d8995;stroke-width:2;fill:none;marker-end:url(#arrow)}</style>',
        '<rect width="1200" height="420" rx="24" fill="#fbfaf7"/>',
        '<text class="h" x="48" y="50">AI 原生研究循环</text>',
        '<text class="s" x="48" y="78">速度发生在中间，所有权覆盖全程。循环的输出必须成为下一轮问题的输入。</text>',
    ]
    for idx, (title, subtitle, color) in enumerate(steps):
        x = 42 + idx * 232
        parts.append(f'<rect x="{x}" y="145" width="196" height="118" rx="18" fill="{color}" stroke="#cbd4dc"/>')
        parts.append(f'<text class="t" x="{x + 98}" y="187" text-anchor="middle">{escape(title)}</text>')
        parts.append(f'<text class="s" x="{x + 98}" y="220" text-anchor="middle">{escape(subtitle)}</text>')
        if idx < len(steps) - 1:
            parts.append(f'<path class="a" d="M{x + 198} 204 H{x + 225}"/>')
    parts.append('<path class="a" d="M1068 278 C1068 360 140 360 140 280"/>')
    parts.append('<rect x="373" y="305" width="454" height="48" rx="24" fill="#20201e"/>')
    parts.append('<text x="600" y="336" text-anchor="middle" style="font:700 15px -apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Microsoft YaHei,sans-serif;fill:#ffffff">人的责任：规定 · 证据 · 复现 · 解释 · 答辩</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def four_skills_svg() -> str:
    nodes = [
        (600, 120, "听", "现场 → 问题模型", "#dcebf0", "#168c82"),
        (930, 295, "说", "内部模型 → 共同理解", "#f9dcd6", "#e9775f"),
        (600, 470, "写", "过程 → 可积累对象", "#eee4f0", "#744889"),
        (270, 295, "读", "论文 → 证据机器", "#e8e7f5", "#536cc5"),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 590">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#7d8995"/></marker></defs>',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;fill:#182230}.h{font-size:25px;font-weight:700}.t{font-size:24px;font-weight:750}.s{font-size:15px;fill:#536273}.a{stroke:#7d8995;stroke-width:2;fill:none;marker-end:url(#arrow)}</style>',
        '<rect width="1200" height="590" rx="24" fill="#fbfaf7"/>',
        '<text class="h" x="48" y="50">听说读写不是四个筒仓</text>',
        '<text class="s" x="48" y="78">任何一次高质量输入都应经过理解、输出、反馈与再归档，回到中心研究问题。</text>',
        '<circle cx="600" cy="295" r="95" fill="#20201e"/>',
        '<text x="600" y="289" text-anchor="middle" style="font:750 22px -apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Microsoft YaHei,sans-serif;fill:#fff">真实研究问题</text>',
        '<text x="600" y="320" text-anchor="middle" style="font:14px -apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Microsoft YaHei,sans-serif;fill:#ddd">实验 · 推导 · 分析</text>',
        '<path class="a" d="M680 205 C775 150 890 175 924 226"/><path class="a" d="M930 365 C885 425 775 448 684 415"/><path class="a" d="M516 415 C420 450 310 420 273 364"/><path class="a" d="M272 226 C312 171 430 150 520 205"/>',
    ]
    for x, y, title, subtitle, fill, stroke in nodes:
        parts.append(f'<rect x="{x - 132}" y="{y - 51}" width="264" height="102" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        parts.append(f'<text class="t" x="{x}" y="{y - 7}" text-anchor="middle">{title}</text>')
        parts.append(f'<text class="s" x="{x}" y="{y + 25}" text-anchor="middle">{escape(subtitle)}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def dual_output_svg() -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 430">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#7d8995"/></marker></defs>',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;fill:#182230}.h{font-size:25px;font-weight:700}.t{font-size:20px;font-weight:750}.s{font-size:15px;fill:#536273}.a{stroke:#7d8995;stroke-width:2;fill:none;marker-end:url(#arrow)}</style>',
        '<rect width="1200" height="430" rx="24" fill="#fbfaf7"/>',
        '<text class="h" x="48" y="50">每次活动同时生产两类输出</text>',
        '<rect x="58" y="150" width="250" height="120" rx="18" fill="#20201e"/>',
        '<text x="183" y="202" text-anchor="middle" style="font:750 20px -apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Microsoft YaHei,sans-serif;fill:#fff">一次真实科研活动</text>',
        '<text x="183" y="235" text-anchor="middle" style="font:14px -apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Microsoft YaHei,sans-serif;fill:#ddd">读文献 · 做实验 · 组会 · 写作</text>',
        '<path class="a" d="M310 185 H430"/><path class="a" d="M310 235 H430"/>',
        '<rect x="440" y="105" width="315" height="125" rx="18" fill="#e9f8f2" stroke="#168c82" stroke-width="2"/>',
        '<text class="t" x="598" y="150" text-anchor="middle">项目产出</text><text class="s" x="598" y="184" text-anchor="middle">数据 · 代码 · 论文 · 决策 · 里程碑</text>',
        '<rect x="440" y="245" width="315" height="125" rx="18" fill="#e8e7f5" stroke="#536cc5" stroke-width="2"/>',
        '<text class="t" x="598" y="290" text-anchor="middle">研究者产出</text><text class="s" x="598" y="324" text-anchor="middle">判断规则 · 方法直觉 · 表达 · 元认知</text>',
        '<path class="a" d="M760 168 H880"/><path class="a" d="M760 307 H880"/>',
        '<rect x="890" y="150" width="252" height="120" rx="18" fill="#fff4de" stroke="#e4aa45" stroke-width="2"/>',
        '<text class="t" x="1016" y="199" text-anchor="middle">长期独立性</text><text class="s" x="1016" y="232" text-anchor="middle">能在新问题上再次做到</text>',
        '<text class="s" x="48" y="405">只检查“这周做出了什么”，会漏掉能力成长；只谈成长而没有真实交付，又会失去研究对象。</text>',
        '</svg>',
    ]
    return "\n".join(parts)


def ownership_svg() -> str:
    width, height = 1200, 620
    left, top = 150, 125
    cell_w, cell_h = 245, 92
    colors = ["#e8f1ff", "#e9f8f2", "#fff4de", "#f7eafa"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;fill:#182230}.h{font-size:25px;font-weight:700}.m{font-size:23px;font-weight:700}.g{font-size:19px;font-weight:650}.c{font-size:16px}.n{font-size:14px;fill:#536273}</style>',
        '<rect width="1200" height="620" rx="24" fill="#fbfaf7"/>',
        '<text class="h" x="50" y="48">四种科研行为 × 四道所有权门</text>',
        '<text class="n" x="50" y="78">16 个检查点是本体系的结构计数，不是经验效应量。AI 可以参与每格，人必须对通过结果负责。</text>',
    ]
    for j, gate in enumerate(GATES):
        x = left + j * cell_w + cell_w / 2
        parts.append(f'<text class="g" x="{x}" y="112" text-anchor="middle">{escape(gate)}</text>')
    for i, (modality, checks) in enumerate(MODALITIES.items()):
        y = top + i * cell_h
        parts.append(f'<text class="m" x="82" y="{y + 55}" text-anchor="middle">{modality}</text>')
        for j, check in enumerate(checks):
            x = left + j * cell_w
            parts.append(f'<rect x="{x + 6}" y="{y + 7}" width="{cell_w - 12}" height="{cell_h - 14}" rx="14" fill="{colors[i]}" stroke="#cfd7df"/>')
            parts.append(f'<text class="c" x="{x + cell_w / 2}" y="{y + 54}" text-anchor="middle">{escape(check)}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def roadmap_svg() -> str:
    width, height = 1200, 535
    x0, y0, box_w, gap = 40, 150, 208, 28
    colors = ["#edf4ff", "#e8f7f1", "#fff3da", "#f7e8f6", "#feeae4"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;fill:#182230}.h{font-size:25px;font-weight:700}.t{font-size:19px;font-weight:700}.b{font-size:15px}.s{font-size:14px;fill:#536273}.arrow{stroke:#8090a0;stroke-width:2;fill:none}</style>',
        '<rect width="1200" height="535" rx="24" fill="#fbfaf7"/>',
        '<text class="h" x="40" y="48">五年不是五张日历，而是五次“毕业测试”</text>',
        '<text class="s" x="40" y="78">阶段可快可慢。只有行为证据达到标准才进入下一阶段。</text>',
    ]
    for idx, (name, focus, test) in enumerate(STAGES):
        x = x0 + idx * (box_w + gap)
        if idx:
            parts.append(f'<path class="arrow" d="M{x - gap + 4} 264 H{x - 7}"/>')
            parts.append(f'<path d="M{x - 13} 258 L{x - 6} 264 L{x - 13} 270" fill="none" stroke="#8090a0" stroke-width="2"/>')
        parts.append(f'<rect x="{x}" y="{y0}" width="{box_w}" height="258" rx="18" fill="{colors[idx]}" stroke="#ccd5df"/>')
        parts.append(f'<text class="t" x="{x + 18}" y="{y0 + 37}">{escape(name)}</text>')
        parts.append(f'<text class="s" x="{x + 18}" y="{y0 + 66}">训练焦点</text>')
        parts.append(f'<foreignObject x="{x + 18}" y="{y0 + 76}" width="{box_w - 36}" height="54"><div xmlns="http://www.w3.org/1999/xhtml" style="font:15px -apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Microsoft YaHei,sans-serif;color:#182230;line-height:1.45">{escape(focus)}</div></foreignObject>')
        parts.append(f'<text class="s" x="{x + 18}" y="{y0 + 151}">毕业测试</text>')
        parts.append(f'<foreignObject x="{x + 18}" y="{y0 + 162}" width="{box_w - 36}" height="78"><div xmlns="http://www.w3.org/1999/xhtml" style="font:15px -apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Microsoft YaHei,sans-serif;color:#182230;line-height:1.45">{escape(test)}</div></foreignObject>')
    parts.append(f'<text class="s" x="40" y="472">贯穿全部阶段的 6 项能力：{" / ".join(CAPABILITIES)}</text>')
    parts.append(f'<text class="s" x="40" y="500">进展矩阵共有 {len(STAGES) * len(CAPABILITIES)} 个“阶段 × 能力”证据格，季度复盘只更新有作品或行为证据的格子。</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    (FIGURES / "ai-native-loop.svg").write_text(ai_loop_svg(), encoding="utf-8")
    (FIGURES / "four-skills-cycle.svg").write_text(four_skills_svg(), encoding="utf-8")
    (FIGURES / "dual-output.svg").write_text(dual_output_svg(), encoding="utf-8")
    (FIGURES / "ownership-matrix.svg").write_text(ownership_svg(), encoding="utf-8")
    (FIGURES / "five-year-roadmap.svg").write_text(roadmap_svg(), encoding="utf-8")
    summary = [
        f"modalities={len(MODALITIES)}",
        f"ownership_gates={len(GATES)}",
        f"ownership_checkpoints={len(MODALITIES) * len(GATES)}",
        f"development_stages={len(STAGES)}",
        f"capabilities={len(CAPABILITIES)}",
        f"stage_capability_cells={len(STAGES) * len(CAPABILITIES)}",
        "note=All counts describe the proposed framework structure; none is an empirical effect size.",
    ]
    (ROOT / "analysis" / "framework-summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
