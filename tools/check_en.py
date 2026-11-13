#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the English mirror under en/ (plus *.en.md).
Checks: inventory mirror, lang=en, zero CJK (except the lang-switch label),
asset depth, link resolution, lesson components, quiz JSON, pager chain
(English labels), JS id refs. Companion to check.py (which covers the Chinese
pages and skips en/).
"""
import json
import re
import sys
from pathlib import Path
from html_checks import check_common, quiz_errors

ROOT = Path(__file__).resolve().parent.parent

BRANCHES = [
    "01-economics", "02-accounting", "03-finance", "04-marketing",
    "05-management", "06-human-resources", "07-operations-supply-chain",
    "08-strategy", "09-entrepreneurship", "10-business-analytics",
    "11-international-business", "12-business-law-ethics",
]
BRANCH_CLASS = {
    "01-economics": "branch-economics", "02-accounting": "branch-accounting",
    "03-finance": "branch-finance", "04-marketing": "branch-marketing",
    "05-management": "branch-management", "06-human-resources": "branch-hr",
    "07-operations-supply-chain": "branch-operations", "08-strategy": "branch-strategy",
    "09-entrepreneurship": "branch-entrepreneurship", "10-business-analytics": "branch-analytics",
    "11-international-business": "branch-international", "12-business-law-ethics": "branch-law-ethics",
}
CJK_STRICT = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff01-\uff5e\u300c\u300d]")

ERRS, WARNS = 0, 0


def err(rel, msg):
    global ERRS
    ERRS += 1
    print(f"  ERR  {rel}: {msg}")


def warn(rel, msg):
    global WARNS
    WARNS += 1
    print(f"  WARN {rel}: {msg}")


def check_html(page: Path):
    rel = page.relative_to(ROOT).as_posix()
    try:
        text = page.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        err(rel, f"not valid UTF-8: {e}")
        return
    parts = page.relative_to(ROOT / "en").parts
    is_lesson = len(parts) == 3 and parts[1] == "lessons"
    is_branch_index = len(parts) == 2 and parts[1] == "index.html"
    branch = parts[0] if len(parts) >= 2 and re.match(r"^\d\d-", parts[0]) else None
    markup = check_common(page, ROOT, lambda msg: err(rel, msg))

    if 'lang="en"' not in text:
        err(rel, "missing lang=en")
    if "zh-CN" in text:
        err(rel, "contains zh-CN")
    # the lang-switch button deliberately shows the target language in its own script
    cjk_scan = re.sub(r'(<a class="lang-switch"[^>]*>)中文(</a>)', r"\1\2", text)
    cjk = CJK_STRICT.findall(cjk_scan)
    if cjk:
        err(rel, f"{len(cjk)} CJK chars remain, e.g. {''.join(cjk[:8])!r}")

    m = re.search(r"<title>(.*?)</title>", text)
    if not m or not m.group(1).strip() or "·" not in m.group(1):
        warn(rel, f"title missing or lacks '·': {m.group(1) if m else None!r}")

    mb = re.search(r'<body class="([^"]+)"', text)
    if not mb:
        err(rel, "body has no class")
    else:
        expect = BRANCH_CLASS.get(branch, "branch-home") if branch else "branch-home"
        if expect not in mb.group(1).split():
            err(rel, f"body class={mb.group(1)!r} expected {expect}")

    ids = re.findall(r'id="([^"]+)"', text)
    idset = set(ids)
    for _, attrs in markup.tags:
        for attr in ("href", "src"):
            url = attrs.get(attr) or ""
            if "/assets/" in url and attr in ("href", "src"):
                depth_needed = "../../../" if is_lesson else ("../../" if is_branch_index else "../")
                if not url.startswith(depth_needed + "assets/"):
                    err(rel, f"asset path depth wrong: {url} (expected {depth_needed}assets/)")

    if is_lesson:
        for need in ("../../../assets/viz.js", "../../../assets/quiz.js", "../../../assets/course.css"):
            if need not in text:
                err(rel, f"missing include {need}")
        for cls, name in (("sim", ".sim"), ("case", ".case"), ("glossary", ".glossary"),
                          ("takeaway", ".takeaway"), ("quiz", ".quiz"),
                          ("ask-teacher", ".ask-teacher"), ("pager", ".pager")):
            if f'class="{cls}"' not in text and f'class="{cls} ' not in text:
                err(rel, f"missing component: {name}")
        if 'id="further"' not in text:
            warn(rel, "missing #further")
        if not re.search(r"Viz\.(slider|draggable)|addEventListener", text):
            warn(rel, "no interactivity found")
    elif is_branch_index:
        for need in ("../../assets/course.css", "../../assets/progress.js"):
            if need not in text:
                err(rel, f"missing include {need}")
    else:
        if "../assets/progress.js" not in text:
            err(rel, "root en/index.html missing ../assets/progress.js")

    script_txt = "".join(re.findall(r"<script>(.*?)</script>", text, re.S))
    for ref in re.findall(r'getElementById\(\s*["\']([^"\']+)["\']\s*\)', script_txt):
        if ref not in idset:
            err(rel, f'JS references missing id: "{ref}"')

    answers = []
    for q in re.findall(r'<script type="application/json">(.*?)</script>', text, re.S):
        try:
            data = json.loads(q)
        except ValueError as e:
            continue
        if quiz_errors(data):
            continue
        if not (3 <= len(data) <= 5):
            warn(rel, f"quiz count={len(data)} (spec 3-5)")
        for qi, item in enumerate(data):
            opts = [re.sub(r"<[^>]+>", "", o) for o in item.get("options", [])]
            if len(opts) != 4:
                warn(rel, f"Q{qi+1} options={len(opts)} (convention 4)")
            ans = item.get("answer")
            if not isinstance(ans, int) or not (0 <= ans < len(opts)):
                err(rel, f"Q{qi+1} answer index invalid")
                continue
            answers.append(ans)
            if not item.get("explain", "").strip():
                err(rel, f"Q{qi+1} missing explanation")
            lens = [len(o) for o in opts]
            if max(lens) - min(lens) > 25 and max(lens) > 1.6 * min(lens):
                warn(rel, f"Q{qi+1} option lengths vary widely {lens}")
    if len(answers) >= 3 and len(set(answers)) == 1:
        warn(rel, f"all answers at index {answers[0]} (should rotate)")


def check_pager(page: Path, j: int, n: int, prev_name: str, next_href: str, is_last_branch: bool):
    rel = page.relative_to(ROOT).as_posix()
    text = page.read_text(encoding="utf-8")
    m = re.search(r"(?s)<nav class=\"pager\">(.*?)</nav>", text)
    if not m:
        err(rel, "missing <nav class=\"pager\">")
        return
    nav = m.group(1)
    links = re.findall(
        r'<a (?:class="next" )?href="([^"]+)"><span class="pager-label">([^<]*)</span>'
        r"<span class=\"pager-title\">([^<]*)</span>", nav)
    if len(links) != 2:
        err(rel, f"pager should have exactly two links, found {len(links)}")
        return
    (prev_href, prev_label, prev_title), (next_h, next_label, next_title) = links
    if prev_label != "← Previous":
        err(rel, f"prev label should be '← Previous', got {prev_label!r}")
    if not prev_title.strip():
        err(rel, "prev title empty")
    if prev_href != prev_name:
        err(rel, f"prev should point to {prev_name}, got {prev_href!r}")
    if j == n - 1:
        want_label = "Return to Overview →" if is_last_branch else "Next Branch →"
    else:
        want_label = "Next →"
    if next_label != want_label:
        err(rel, f"next label should be {want_label!r}, got {next_label!r}")
    if not next_title.strip():
        err(rel, "next title empty")
    if next_h != next_href:
        err(rel, f"next should point to {next_href}, got {next_h!r}")


def main():
    global ERRS, WARNS
    ERRS = WARNS = 0
    print("=" * 68)
    print("en/ mirror validation")
    print("=" * 68)

    expected = {"index.html"}
    for br in BRANCHES:
        expected.add(f"{br}/index.html")
        src_lessons = sorted((ROOT / br / "lessons").glob("*.html"))
        for lp in src_lessons:
            expected.add(f"{br}/lessons/{lp.name}")
    actual = {p.relative_to(ROOT / "en").as_posix()
              for p in (ROOT / "en").rglob("*.html")} if (ROOT / "en").exists() else set()
    for missing in sorted(expected - actual):
        err(f"en/{missing}", "expected file missing")
    for extra in sorted(actual - expected):
        err(f"en/{extra}", "unexpected extra file")

    pages = [ROOT / "en" / rel for rel in sorted(expected & actual)]
    for page in pages:
        check_html(page)

    for bi, br in enumerate(BRANCHES):
        lessons = sorted((ROOT / "en" / br / "lessons").glob("*.html"))
        if len(lessons) != 4:
            err(f"en/{br}", f"lesson count {len(lessons)} (should be 4)")
        for j, lp in enumerate(lessons):
            prev_name = "../index.html" if j == 0 else lessons[j - 1].name
            if j < len(lessons) - 1:
                next_href = lessons[j + 1].name
            elif bi + 1 < len(BRANCHES):
                next_href = f"../../{BRANCHES[bi + 1]}/index.html"
            else:
                next_href = "../../index.html"
            check_pager(lp, j, len(lessons), prev_name, next_href, bi + 1 == len(BRANCHES))

    for md in ["README.en.md", "MISSION.en.md", "NOTES.en.md", "RESOURCES.en.md", "STYLEGUIDE.en.md"]:
        p = ROOT / md
        if not p.exists():
            err(md, "missing")
            continue
        t = p.read_text(encoding="utf-8")
        cjk = CJK_STRICT.findall(t)
        if cjk:
            err(md, f"{len(cjk)} CJK chars remain, e.g. {''.join(cjk[:8])!r}")

    print("=" * 68)
    print(f"en pages {len(actual)}/61 | md 5 | ERR {ERRS} | WARN {WARNS}")
    return 1 if ERRS else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
