#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Business 课程库 · 一致性自检工具

用法(零第三方依赖,Python 3.8+):
    python tools/check.py            # 全量检查
    python tools/check.py 01-economics  # 只检查指定分支

对应 STYLEGUIDE.md 第 8 节"交付前自查清单"的自动化实现:
  · 内部链接可达(href/src)、页内锚点、重复 id
  · 每课必备组件(.sim/.case/.glossary/.takeaway/.quiz/.pager/.ask-teacher)
  · quiz 规范:JSON 合法、题数、选项数、答案下标、解析、选项等长、答案位置轮换
  · pager 链路:第 1 课→分支导学,课间互链,末课→下一分支/总览,统一文案
  · JS id 引用存在(仅检查字面量调用,动态拼接前缀自动跳过)
  · 分支配色 class 与目录匹配、引入路径深度、favicon、索引页 progress.js
  · 零外部资源依赖(脚本/样式/图片不得外链)

输出:ERR = 必须修复(进程退出码 1);WARN = 建议关注;INFO = 仅提示。
"""
import json
import re
import sys
from pathlib import Path
from html_checks import check_common, quiz_errors

ROOT = Path(__file__).resolve().parent.parent

BRANCH_CLASS = {
    "01-economics": "branch-economics", "02-accounting": "branch-accounting",
    "03-finance": "branch-finance", "04-marketing": "branch-marketing",
    "05-management": "branch-management", "06-human-resources": "branch-hr",
    "07-operations-supply-chain": "branch-operations", "08-strategy": "branch-strategy",
    "09-entrepreneurship": "branch-entrepreneurship", "10-business-analytics": "branch-analytics",
    "11-international-business": "branch-international", "12-business-law-ethics": "branch-law-ethics",
}
# 延伸阅读白名单(STYLEGUIDE §5)
LINK_WHITELIST = ("zh.wikipedia.org", "en.wikipedia.org", "investopedia.com", "www.skills.sh")

ERRS, WARNS, INFOS = 0, 0, 0


def err(rel, msg):
    global ERRS
    ERRS += 1
    print(f"  ERR  {rel}: {msg}")


def warn(rel, msg):
    global WARNS
    WARNS += 1
    print(f"  WARN {rel}: {msg}")


def info(rel, msg):
    global INFOS
    INFOS += 1
    print(f"  INFO {rel}: {msg}")


def check_page(page: Path):
    rel = str(page.relative_to(ROOT))
    text = page.read_text(encoding="utf-8")
    is_lesson = "lessons" in page.parts
    branch = next((p for p in page.parts if re.match(r"^\d\d-", p)), None)
    check_common(page, ROOT, lambda msg: err(rel, msg), lambda msg: warn(rel, msg), LINK_WHITELIST)

    # ---- 基础头 ----
    if 'lang="zh-CN"' not in text:
        err(rel, "缺少 lang=zh-CN")
    if 'name="viewport"' not in text:
        err(rel, "缺少 viewport meta")
    m = re.search(r"<title>(.*?)</title>", text)
    if not m or not m.group(1).strip():
        err(rel, "缺少 <title>")
    elif is_lesson and "·" not in m.group(1):
        warn(rel, f"课题 title 建议为「{{课题}} · {{分支中文名}}」格式:{m.group(1)!r}")
    if 'rel="icon"' not in text:
        err(rel, "缺少 favicon <link rel=\"icon\">")

    # ---- body 分支配色 ----
    mb = re.search(r'<body class="([^"]+)"', text)
    expect = BRANCH_CLASS.get(branch, "branch-home")
    if not mb:
        err(rel, "body 无 class")
    elif branch and expect not in mb.group(1).split():
        err(rel, f"body class={mb.group(1)!r} 应为 {expect}")
    elif not branch and "branch-home" not in mb.group(1).split():
        err(rel, f"根页 body class={mb.group(1)!r} 应为 branch-home")

    # ---- id 完整性 ----
    ids = re.findall(r'id="([^"]+)"', text)
    idset = set(ids)

    # ---- 引入路径 ----
    if is_lesson:
        for need in ("../../assets/viz.js", "../../assets/quiz.js", "../../assets/course.css"):
            if need not in text:
                err(rel, f"缺少引入 {need}")
    elif branch:
        if "../assets/course.css" not in text:
            err(rel, "分支页应引 ../assets/course.css")
        if "../assets/progress.js" not in text:
            err(rel, "分支页应引 ../assets/progress.js")
    else:
        if "assets/progress.js" not in text:
            err(rel, "总览页应引 assets/progress.js")

    # ---- 课程页组件 ----
    if is_lesson:
        for cls, name in (("sim", "交互模拟 .sim"), ("case", "案例 .case"),
                          ("glossary", "术语表 .glossary"), ("takeaway", "要点 .takeaway"),
                          ("quiz", "测验 .quiz"), ("ask-teacher", "页脚问老师"),
                          ("pager", "上下页导航")):
            if f'class="{cls}"' not in text and f'class="{cls} ' not in text:
                err(rel, f"缺少组件: {name}")
        if 'id="further"' not in text:
            warn(rel, "缺少延伸阅读 #further")
        if not re.search(r"Viz\.(slider|draggable)|addEventListener", text):
            warn(rel, "未见任何交互(Viz.slider/draggable/addEventListener)")

    # ---- JS id 引用(仅字面量;动态拼接如 "ms-" + i 自动跳过)----
    script_txt = "".join(re.findall(r"<script>(.*?)</script>", text, re.S))
    for ref in re.findall(r'getElementById\(\s*["\']([^"\']+)["\']\s*\)', script_txt):
        if ref not in idset:
            err(rel, f'JS 引用了不存在的 id: "{ref}"')

    # ---- quiz 规范 ----
    answers = []
    for q in re.findall(r'<script type="application/json">(.*?)</script>', text, re.S):
        try:
            data = json.loads(q)
        except ValueError as e:
            continue
        if quiz_errors(data):
            continue  # Shared checks already reported the schema errors.
        if not (3 <= len(data) <= 5):
            warn(rel, f"quiz 题数={len(data)}(规范 3-5)")
        for qi, item in enumerate(data):
            opts = [re.sub(r"<[^>]+>", "", o) for o in item.get("options", [])]
            if len(opts) != 4:
                warn(rel, f"Q{qi + 1} 选项数={len(opts)}(惯例 4)")
            ans = item.get("answer")
            if not isinstance(ans, int) or not (0 <= ans < len(opts)):
                err(rel, f"Q{qi + 1} answer 下标越界或缺失")
                continue
            answers.append(ans)
            if not item.get("explain", "").strip():
                err(rel, f"Q{qi + 1} 无解析")
            lens = [len(o) for o in opts]
            if max(lens) - min(lens) > 12 and max(lens) > 1.8 * min(lens):
                warn(rel, f"Q{qi + 1} 选项长度差异过大 {lens}(长度可能泄漏答案)")
    if len(answers) >= 3 and len(set(answers)) == 1:
        warn(rel, f"答案位置全在 {answers[0]}(规范要求轮换)")

    # ---- 正文体量(含组件文本,放宽上限)----
    if is_lesson:
        body = re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S)
        cjk = len(re.findall(r"[\u4e00-\u9fff]", re.sub(r"<[^>]+>", "", body)))
        if not (1200 <= cjk <= 2600):
            info(rel, f"正文汉字约 {cjk}(规范 1200-2200)")


def check_pager(page: Path, j: int, n: int, prev_name: str, next_href: str, is_last_branch: bool):
    """统一后的 pager 规范:span 结构 + 固定文案 + 正确链路"""
    rel = str(page.relative_to(ROOT))
    text = page.read_text(encoding="utf-8")
    m = re.search(r'(?s)<nav class="pager">(.*?)</nav>', text)
    if not m:
        err(rel, "缺少 <nav class=\"pager\">")
        return
    nav = m.group(1)
    if "<div class=\"pager-" in nav:
        err(rel, "pager 标签应使用 <span> 而非 <div>")
    links = re.findall(
        r'<a (?:class="next" )?href="([^"]+)"><span class="pager-label">([^<]*)</span>'
        r"<span class=\"pager-title\">([^<]*)</span>", nav)
    if len(links) != 2:
        err(rel, "pager 应恰好包含两个 <a>(上一课/下一课)")
        return
    (prev_href, prev_label, prev_title), (next_h, next_label, next_title) = links
    if prev_label != "← 上一课":
        err(rel, f"上一课标签应为「← 上一课」,现为 {prev_label!r}")
    if not prev_title.strip():
        err(rel, "上一课缺少标题")
    if j == 0:
        if prev_href != "../index.html":
            err(rel, f"第 1 课「上一课」应指向 ../index.html,现为 {prev_href!r}")
    elif prev_href != prev_name:
        err(rel, f"「上一课」应指向 {prev_name},现为 {prev_href!r}")
    if j == n - 1:
        want_label = "返回总览 →" if is_last_branch else "下一分支 →"
    else:
        want_label = "下一课 →"
    if next_label != want_label:
        err(rel, f"下一课标签应为「{want_label}」,现为 {next_label!r}")
    if not next_title.strip():
        err(rel, "下一课缺少标题")
    if next_h != next_href:
        err(rel, f"「下一课」应指向 {next_href},现为 {next_h!r}")


def main():
    global ERRS, WARNS, INFOS
    ERRS = WARNS = INFOS = 0
    only = sys.argv[1] if len(sys.argv) > 1 else None

    pages = [p for p in sorted(ROOT.rglob("*.html"))
             if "en" not in p.relative_to(ROOT).parts  # 英文镜像由 tools/check_en.py 校验
             if not only or any(only in part for part in p.parts)]
    if only and not pages:
        print(f"未找到与 {only!r} 匹配的页面")
        return 2

    print("=" * 68)
    print("Business 课程库自检")
    print("=" * 68)
    expected_indexes = [ROOT / "index.html"] + [ROOT / branch / "index.html" for branch in BRANCH_CLASS]
    for index in expected_indexes:
        if (not only or only in index.parent.name) and not index.is_file():
            err(index.relative_to(ROOT), "缺少必需的索引页")
    for page in pages:
        check_page(page)

    # pager 链路(按分支顺序串起全部课程;标签/指向始终按完整分支序计算)
    all_branches = sorted(BRANCH_CLASS)
    for bi, br in enumerate(all_branches):
        if only and only not in br:
            continue
        lessons = sorted((ROOT / br / "lessons").glob("*.html"))
        if len(lessons) != 4:
            err(br, f"课程数为 {len(lessons)}(应为 4)")
        for j, lp in enumerate(lessons):
            if j == 0:
                prev_name = "../index.html"
            else:
                prev_name = lessons[j - 1].name
            if j < len(lessons) - 1:
                next_href = lessons[j + 1].name
            elif bi + 1 < len(all_branches):
                next_href = f"../../{all_branches[bi + 1]}/index.html"
            else:
                next_href = "../../index.html"
            check_pager(lp, j, len(lessons), prev_name, next_href, bi + 1 == len(all_branches))

    print("=" * 68)
    print(f"页面 {len(pages)} | ERR {ERRS} | WARN {WARNS} | INFO {INFOS}")
    return 1 if ERRS else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
