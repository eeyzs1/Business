# STYLEGUIDE · Authoring Standards for the Business Curriculum (English translation)

> *A faithful English translation of STYLEGUIDE.md — the production contract for the Chinese edition. The authoritative original is STYLEGUIDE.md. For the English mirror under `en/`, the same rules apply with `lang="en"`, English UI strings, and asset paths one level deeper (`../assets/` → root, `../../assets/` → branch index, `../../../assets/` → lesson pages).*

This guide is the “contract” for all teaching materials. Every lesson page and every branch page must comply. The methodology comes from the `teach` skill: knowledge (trusted sources) → skill (interactive practice + instant feedback) → long-term memory (retrieval practice).

## 1. Directory Structure and Naming

```
F:\Business\
├── index.html              # site overview (HTML)
├── README.md               # overview (Markdown, kept in sync with index.html)
├── MISSION.md / RESOURCES.md / NOTES.md
├── STYLEGUIDE.md           # this specification
├── tools\
│   └── check.py            # automated self-check (must run before delivery; see §8)
├── assets\                 # shared components (lesson-generation sessions must not modify)
│   ├── course.css          # design system
│   ├── quiz.js             # quiz component (with score persistence)
│   ├── viz.js              # SVG chart/slider/drag toolbox
│   ├── progress.js         # learning-progress badges for index pages
│   └── favicon.svg         # site icon
├── 01-economics\
│   ├── index.html          # branch guide page
│   └── lessons\
│       ├── 0001-supply-and-demand.html
│       ├── 0002-....html
│       └── 0004-....html
├── 02-accounting\ ...
└── 12-business-law-ethics\ ...
```

- Lesson filenames: all-lowercase kebab-case, four-digit ascending numbers.
- It is **forbidden** to modify anything under `assets/` or `tools/` during a lesson-generation session, and forbidden to create new globally shared files. Branch-specific JS/SVG must be inlined in the page.

## 2. Page Skeleton (required for every lesson)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{Lesson title} · {Branch name}</title>
<link rel="stylesheet" href="../../assets/course.css">
<link rel="icon" type="image/svg+xml" href="../../assets/favicon.svg">
</head>
<body class="branch-economics">  <!-- use this branch's branch-* class -->
<nav class="lesson-nav"><div class="inner">
  <a href="../../index.html">Overview</a><span class="crumb-sep">/</span>
  <a href="../index.html">{Branch name}</a><span class="crumb-sep">/</span>
  <span>{Lesson title}</span>
  <span class="progress">Lesson 2 of 4</span>
  <a class="lang-switch" href="{counterpart page in the other language}">EN</a>
</div></nav>

<main class="container">
  <p class="hero-eyebrow">{Branch name} · LESSON 2</p>
  <h1>{Lesson title}</h1>
  <p class="lead">{Why learn this: 1–3 sentences, connecting to the overall mission of “understanding the business world”}</p>

  <!-- Body sections; h2 carries a <span class="secno">1</span> number -->

  <div class="concept">…definition card…</div>
  <figure class="figure"><div class="figure-body">…SVG…</div>
    <figcaption class="figure-caption"><b>Figure 1</b> …caption…</figcaption></figure>
  <div class="sim">…interactive simulation (at least 1)…</div>
  <div class="case">…real-company case…</div>
  <div class="glossary">…this lesson’s terms…</div>
  <div class="takeaway">…key takeaway…</div>

  <div class="quiz"><script type="application/json">[…]</script></div>

  <section id="further">  <!-- further reading -->
  <nav class="pager">…previous / next lesson…</nav>
  <footer class="lesson-footer">
    <div class="ask-teacher"><b>Questions?</b>Return to the conversation and ask your AI teacher directly…</div>
  </footer>
</main>

<script src="../../assets/viz.js"></script>
<script src="../../assets/quiz.js"></script>
<script>/* lesson-specific interactive logic (optional) */</script>
</body></html>
```

Path rules: a branch `index.html` and a lesson page sit at different depths — the branch home uses `../assets/...`, lesson pages (under `lessons/`) use `../../assets/...`.
Language toggle: every page (Chinese edition and `en/` mirror alike) must end its top nav with a `<a class="lang-switch">` pill linking to the counterpart page in the other language (the pill is labeled EN on Chinese pages and with the Chinese word for “Chinese” on English pages); new pages must always be added in both languages.

## 3. Content Requirements (pedagogy)

1. **One concept per lesson**: each lesson teaches exactly one clearly defined concept, completable in 30–45 minutes. Body text of 1,200–2,200 Chinese characters (roughly 800–1,500 English words) — don’t overstuff; the learner’s working memory is small.
2. **Written language**: Simplified Chinese in the original edition (English mirror under `en/`); technical terms are annotated with the English term in parentheses at first mention (e.g. the Chinese term for gross profit followed by “(Gross Profit)”).
3. **Explanation order**: first “why” (what business problem the concept solves) → then “what” (the definition) → then “how” (interactive practice) → finally the case.
4. **Interaction first**: at least 1 interactive element per lesson — a slider simulator (`.sim` + `Viz.slider`), a draggable chart (`Viz.draggable`), or a step-by-step animated SVG. If a picture can carry it, don’t use words; if interaction can carry it, don’t use a static picture.
5. **Real case**: each lesson has 1 `.case` using a real company (Apple, Toyota, Coca-Cola, Netflix, Zara, Haidilao, Kweichow Moutai, Microsoft, etc.). Numbers phrased as “approximately / on the order of” and marked “illustrative”; **fabricating precise financial figures is forbidden**.
6. **Glossary**: each lesson’s `.glossary` collects 4–8 terms in a dl/dt/dd structure.
7. **Key takeaway**: `.takeaway` summarizes the single core sentence of the lesson in no more than 3 sentences.
8. **Previous/next pager**: in `.pager`, the first lesson’s “previous” link = `../index.html` (back to the branch guide); the last lesson’s “next” link = the next branch’s `../../{next-branch}/index.html` (for the final branch, back to the overview at `../../index.html`). Note: lesson pages live under `lessons/`, so cross-branch links must use `../../`. The template uses `<span class="pager-label">` (not div): the label text is fixed — the previous-lesson, next-lesson, next-branch, and back-to-overview labels are fixed strings (written in Chinese in the original edition’s templates; English in the en/ mirror); the title text keeps the actual lesson names.
9. **Teacher reminder**: every page footer keeps the `.ask-teacher` reminder telling learners to return to the conversation and ask.

## 4. Quiz Standards

- 3–5 questions per lesson, single choice, JSON format documented at the top of `assets/quiz.js`.
- **Options of equal length**: within a question, keep options similar in length; never leak the answer through length or formatting.
- **Rotate answer positions**: the correct answer’s index must rotate across A/B/C/D, never cluster.
- Every question must carry an `explain` explanation, so that a wrong answer still teaches something.
- Test **discrimination and application** (scenario judgment, concept distinction), never pure recall like “which year” or “who proposed it”.

## 5. Citations and Further Reading

- Each lesson lists 2–3 “further reading” items, prioritizing real classic books, in the format: “*Book Title* by Author · Publisher (suggested: Chapter X)”. Books are not hyperlinked.
- Web sources are limited to a whitelist: **common** articles on `zh.wikipedia.org` / `en.wikipedia.org` (only link article titles you are sure exist) and the `investopedia.com` home page. **Fabricating URLs is strictly forbidden**; when unsure, cite a book or write “search keywords: …”.
- Classic-book reference library (choose by branch; all are real books): Mankiw, *Principles of Economics*; Samuelson, *Economics*; Wild, *Accounting: The Basis for Business Decisions*; Ross et al., *Corporate Finance*; Bodie et al., *Investments*; Kotler, *Marketing Management*; Robbins, *Management*; Drucker, *The Practice of Management*; Robbins, *Organizational Behavior*; Stevenson, *Operations Management*; Porter, *Competitive Strategy* and *Competitive Advantage*; Osterwalder, *Business Model Generation*; Eric Ries, *The Lean Startup*; Peter Thiel, *Zero to One*; Hoffman, *The Alliance*; Hill, *International Business*; Charles Wheelan, *Naked Statistics*; Cal Newport… etc. Do not cite books whose existence you are unsure of.

## 6. Technical Standards

- UTF-8, `lang="zh-CN"` in the original edition (`lang="en"` in the en/ mirror), semantic tags, pages work by simply opening in a browser, **zero external dependencies** (no CDN, no web fonts, no remote images; graphics are inline SVG or CSS).
- HTML attribute values use double quotes; curly/full-width quotes are fine inside JSON, but never put an unescaped straight double quote inside a JSON string (use curly/full-width quotes instead).
- Interactive components should reuse the `Viz.*` API (see `assets/viz.js`): `Viz.axes` (coordinate system), `Viz.line/dot/label/area`, `Viz.bars`, `Viz.slider` (drag callbacks coalesced per frame; `set()` stays in sync), `Viz.countUp`, `Viz.draggable`, `Viz.reveal`. For scroll-reveal, just add `data-reveal` to the element.
- Scripts go before `</body>`; no JS errors allowed (every DOM query must exist by the time the script runs).
- Style fallbacks: any declaration using `color-mix()` must have an equivalent solid/rgba fallback on the previous line (browsers without color-mix support take the previous line).
- Learning progress: `quiz.js` automatically stores each lesson’s best score in localStorage (key `biz-quiz:{branch}/lessons/{file}.html`), and index pages get badges rendered by `progress.js` — lesson pages need no extra code. Do not read or write these keys from lesson pages.
- Print-friendly: core content must not depend on hover to be visible.

## 7. Branch Guide Page (index.html) Standards

- `<body class="branch-xxx">`; include `../assets/course.css` and `<link rel="icon" ... href="../assets/favicon.svg">`.
- Structure: hero (branch name + one-line positioning) → **sub-branch map** (table: sub-branch / core question / status in this branch [covered · Lesson X / advanced, for later]) → learning path (why this order) → `.lesson-list` lesson list (each with a one-line subtitle) → relations to other branches (prerequisites / follow-ups) → footer.
- The branch home also carries the `.ask-teacher` footer.
- Include `<script src="../assets/progress.js"></script>` at the end (it automatically renders progress badges on the lesson list).

## 8. Pre-Delivery Checklist

- [ ] **`python tools/check.py` all green** (zero dependencies; automatically covers most items below: paths/dead links/components/quiz/pager/ids/colors/favicon)
- [ ] Every lesson has ≥1 interactive element, 1 case, 1 glossary, 1 takeaway, 1 quiz
- [ ] Quiz options equal in length, answer positions rotated, every question has an explanation
- [ ] Case companies are real; figures marked “approximately / illustrative”
- [ ] Further-reading books really exist
