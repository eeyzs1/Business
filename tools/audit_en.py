#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Structural audit: compare each en/ page against its Chinese source.
Verifies the translation changed ONLY text: same body class, same id set,
same quiz answer indices and option counts, same pager hrefs, same asset
references (after path-depth normalization), same h2/concept/figure counts.
"""
import json
import re
import sys
from pathlib import Path
from html_checks import quiz_errors

ROOT = Path(__file__).resolve().parent.parent
ERRS, CHECKS = 0, 0


def err(msg):
    global ERRS
    ERRS += 1
    print(f"  ERR  {msg}")


def norm_url(u):
    return re.sub(r"^(\.\./)+", "", u)


def get(text, pattern):
    m = re.search(pattern, text)
    return m.group(1) if m else None


def quiz_data(text):
    out = []
    for q in re.findall(r'<script type="application/json">(.*?)</script>', text, re.S):
        try:
            data = json.loads(q)
        except ValueError:
            out.append(("PARSE_FAIL", None))
            continue
        if quiz_errors(data):
            out.append(("SCHEMA_FAIL", None))
            continue
        out.append(([item.get("answer") for item in data],
                    [len(item.get("options", [])) for item in data]))
    return out


def audit_pair(zh: Path, en: Path):
    global CHECKS
    CHECKS += 1
    rel = en.relative_to(ROOT).as_posix()
    z = zh.read_text(encoding="utf-8")
    e = en.read_text(encoding="utf-8")

    zb, eb = get(z, r'<body class="([^"]+)"'), get(e, r'<body class="([^"]+)"')
    if zb != eb:
        err(f"{rel}: body class {zb!r} -> {eb!r}")

    zids, eids = set(re.findall(r'id="([^"]+)"', z)), set(re.findall(r'id="([^"]+)"', e))
    if zids != eids:
        err(f"{rel}: id set differs; only-zh={sorted(zids-eids)[:5]} only-en={sorted(eids-zids)[:5]}")

    zq, eq = quiz_data(z), quiz_data(e)
    if zq != eq:
        err(f"{rel}: quiz answers/option-counts differ {zq} -> {eq}")

    zassets = sorted(norm_url(u) for u in re.findall(r'(?:href|src)="([^"]+)"', z) if "assets/" in u)
    eassets = sorted(norm_url(u) for u in re.findall(r'(?:href|src)="([^"]+)"', e) if "assets/" in u)
    if zassets != eassets:
        err(f"{rel}: asset refs differ {zassets} -> {eassets}")

    zpager = re.findall(r'<a (?:class="next" )?href="([^"]+)"><span class="pager-label">', z)
    epager = re.findall(r'<a (?:class="next" )?href="([^"]+)"><span class="pager-label">', e)
    if zpager != epager:
        err(f"{rel}: pager hrefs differ {zpager} -> {epager}")

    for tag in ("h2", "h3"):
        zn, enn = len(re.findall(f"<{tag}[ >]", z)), len(re.findall(f"<{tag}[ >]", e))
        if zn != enn:
            err(f"{rel}: <{tag}> count {zn} -> {enn}")
    zn = len(re.findall(r'class="concept', z)); enn = len(re.findall(r'class="concept', e))
    if zn != enn:
        err(f"{rel}: concept-card count {zn} -> {enn}")
    zn = len(re.findall(r'data-reveal', z)); enn = len(re.findall(r'data-reveal', e))
    if zn != enn:
        err(f"{rel}: data-reveal count {zn} -> {enn}")
    zn = len(re.findall(r'<table', z)); enn = len(re.findall(r'<table', e))
    if zn != enn:
        err(f"{rel}: table count {zn} -> {enn}")


def main():
    global ERRS, CHECKS
    ERRS = CHECKS = 0
    pairs = [(ROOT / "index.html", ROOT / "en" / "index.html")]
    for br in sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"^\d\d-", p.name)):
        pairs.append((br / "index.html", ROOT / "en" / br.name / "index.html"))
        for lp in sorted((br / "lessons").glob("*.html")):
            pairs.append((lp, ROOT / "en" / br.name / "lessons" / lp.name))
    print(f"Comparing {len(pairs)} page pairs (zh -> en) ...")
    for zh, en in pairs:
        if not zh.is_file():
            err(f"{zh.as_posix()}: MISSING")
            continue
        if not en.exists():
            err(f"{en.as_posix()}: MISSING")
            continue
        audit_pair(zh, en)
    print(f"pages {len(pairs)} | structural ERR {ERRS}")
    return 1 if ERRS else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
