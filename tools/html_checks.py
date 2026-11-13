"""Shared HTML and quiz checks. Standard library only (Python 3.8+)."""
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Markup(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.quiz_scripts = []
        self._quiz = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "script" and attrs.get("type", "").lower() == "application/json":
            self._quiz = []

    def handle_data(self, data):
        if self._quiz is not None:
            self._quiz.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._quiz is not None:
            self.quiz_scripts.append("".join(self._quiz))
            self._quiz = None

    @property
    def ids(self):
        return [attrs["id"] for _, attrs in self.tags if "id" in attrs]


def quiz_errors(data):
    if not isinstance(data, list) or not data:
        return ["quiz must be a non-empty array"]
    errors = []
    for i, item in enumerate(data, 1):
        prefix = "Q{} ".format(i)
        if not isinstance(item, dict):
            errors.append(prefix + "must be an object")
            continue
        if not isinstance(item.get("q"), str) or not item["q"].strip():
            errors.append(prefix + "missing question text")
        options = item.get("options")
        if not isinstance(options, list) or len(options) < 2 or any(
            not isinstance(opt, str) or not opt.strip() for opt in options
        ):
            errors.append(prefix + "options must contain at least two non-empty strings")
        answer = item.get("answer")
        if type(answer) is not int or not isinstance(options, list) or not 0 <= answer < len(options):
            errors.append(prefix + "answer index invalid")
        if not isinstance(item.get("explain"), str) or not item["explain"].strip():
            errors.append(prefix + "missing explanation")
    return errors


def local_target(page, root, url):
    parts = urlsplit(url)
    path = unquote(parts.path)
    if not path:
        return page.resolve()
    target = ((root / path.lstrip("/")) if path.startswith("/") else (page.parent / path)).resolve()
    # Do not follow authoring mistakes outside the course tree.
    target.relative_to(root.resolve())
    return target / "index.html" if target.is_dir() else target


def check_common(page: Path, root: Path, report, warn=None, allowed_hosts=None):
    """report/warn accept one message; return parsed markup for caller-specific checks."""
    markup = Markup(page.read_text(encoding="utf-8"))
    for ident, count in Counter(markup.ids).items():
        if count > 1:
            report("duplicate id: " + ident)
    if not any(tag == "meta" and attrs.get("name") == "viewport" for tag, attrs in markup.tags):
        report("missing viewport meta")
    if not any(tag == "link" and "icon" in attrs.get("rel", "").split() for tag, attrs in markup.tags):
        report("missing favicon")

    id_cache = {page.resolve(): set(markup.ids)}
    for tag, attrs in markup.tags:
        for attr in ("href", "src"):
            if attr not in attrs or attrs[attr] is None:
                continue
            url = attrs[attr]
            try:
                parts = urlsplit(url)
                if parts.scheme in ("http", "https") or parts.netloc:
                    if attr == "src" or tag != "a":
                        report("external resource ({}): {}".format(attr, url))
                    elif allowed_hosts and warn and not any(
                        (parts.hostname or "").lower() == host or (parts.hostname or "").lower().endswith("." + host)
                        for host in allowed_hosts
                    ):
                        warn("external link outside whitelist: " + url)
                    continue
                if parts.scheme in ("mailto", "tel", "data"):
                    continue
                if parts.scheme:
                    report("unsupported URL scheme: " + url)
                    continue
                target = local_target(page, root, url)
            except (ValueError, OSError):
                report("invalid local link: " + url)
                continue
            if not target.is_file():
                report("dead link {}={}".format(attr, url))
            elif parts.fragment and target.suffix.lower() in (".html", ".svg"):
                if target not in id_cache:
                    id_cache[target] = set(Markup(target.read_text(encoding="utf-8")).ids)
                fragment = unquote(parts.fragment)
                if fragment not in id_cache[target]:
                    report("missing anchor: " + url)

    relative = page.relative_to(root)
    counterpart = root.joinpath(*relative.parts[1:]) if relative.parts[0] == "en" else root / "en" / relative
    switches = [attrs for tag, attrs in markup.tags
                if tag == "a" and "lang-switch" in attrs.get("class", "").split()]
    if len(switches) != 1:
        report("expected exactly one language switch")
    else:
        try:
            url = switches[0].get("href", "")
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or local_target(page, root, url) != counterpart.resolve():
                report("language switch must link to its counterpart")
        except (ValueError, OSError):
            report("invalid language switch link")

    if "lessons" in relative.parts and len(markup.quiz_scripts) != 1:
        report("lesson must contain exactly one quiz JSON script")
    for raw in markup.quiz_scripts:
        try:
            errors = quiz_errors(json.loads(raw))
        except ValueError as exc:
            errors = ["quiz JSON parse failed: " + str(exc)]
        for error in errors:
            report(error)
    return markup
