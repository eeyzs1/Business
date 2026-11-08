# Business Fundamentals Curriculum

> *English edition — open [en/index.html](en/index.html) to browse the English site. Chinese edition: [README.md](README.md).*
>
> An offline, interactive library of business fundamentals. 12 branches · 48 lessons · English mirror of the Chinese edition.
> **Language toggle**: every page’s top nav has a language pill linking to its counterpart page (labeled EN on Chinese pages, Chinese on English pages).
> **Entry point: double-click [en/index.html](en/index.html)** and start from any branch.

This curriculum follows learning methods grounded in cognitive science (derived from the `teach` skill):

- **One concept per lesson**: each lesson takes 30–45 minutes and tackles exactly one clearly defined concept;
- **Interaction first**: you can drag the supply curve, dial the compound-interest curve, click through the funnel — concepts are taught with animations and simulators;
- **Retrieval practice**: every lesson has an instant-feedback quiz; wrong answers come with explanations, and retakes strengthen long-term memory;
- **Real cases**: every lesson includes one real-company case, with figures at illustrative magnitudes;
- **Teacher on call**: every lesson footer reminds you — if in doubt, go back to the conversation and ask your AI teacher.

---

## The Twelve Branches

The standard backbone of the business discipline, mapped to the business-school canon. Each branch folder contains 1 guide page (`index.html`, with the sub-branch map and learning path) and 4 interactive lessons (`lessons/`).

| # | Branch | One-line positioning | Core sub-branches | Entry |
|---|--------|----------------------|-------------------|-------|
| 01 | **Economics** | The operating system beneath every business decision: choosing under scarcity | Microeconomics, macroeconomics, market structure, economic policy | [01-economics/](en/01-economics/index.html) |
| 02 | **Accounting** | The language of business: learn to read a company’s health report | Financial accounting, managerial accounting, statement analysis, audit & tax | [02-accounting/](en/02-accounting/index.html) |
| 03 | **Finance** | The time and the price of money: valuation, investment, and risk | Time value of money, corporate finance, investments, financial markets & risk | [03-finance/](en/03-finance/index.html) |
| 04 | **Marketing** | The science of creating and keeping customers | Marketing strategy (STP), the marketing mix (4Ps), consumer behavior, brand & digital marketing | [04-marketing/](en/04-marketing/index.html) |
| 05 | **Management** | Getting results through others | Planning/organizing/leading/controlling, decision science, organizational behavior, leadership | [05-management/](en/05-management/index.html) |
| 06 | **Human Resources** | Managing people as your most important asset | Recruiting & selection, performance management, compensation & incentives, training & development, organizational culture | [06-human-resources/](en/06-human-resources/index.html) |
| 07 | **Operations & Supply Chain** | The engine that turns promises into deliveries | Process & capacity, quality management, lean production, supply chain & project management | [07-operations-supply-chain/](en/07-operations-supply-chain/index.html) |
| 08 | **Strategy** | Deciding what not to do: building long-term competitive advantage | Industry analysis (Five Forces), competitive strategy, business models, corporate strategy | [08-strategy/](en/08-strategy/index.html) |
| 09 | **Entrepreneurship** | A methodology for going from zero to one | Opportunity recognition & validation, lean startup, business planning, funding & equity | [09-entrepreneurship/](en/09-entrepreneurship/index.html) |
| 10 | **Business Analytics** | Telling business stories with data and driving decisions | Data thinking, descriptive statistics & visualization, causal inference, business intelligence | [10-business-analytics/](en/10-business-analytics/index.html) |
| 11 | **International Business** | Doing business across borders | Globalization & comparative advantage, trade practice, multinational operations, cross-cultural management | [11-international-business/](en/11-international-business/index.html) |
| 12 | **Business Law & Ethics** | The floor and the guardrails of business | Company law & contracts, corporate governance, business ethics, ESG & sustainability | [12-business-law-ethics/](en/12-business-law-ethics/index.html) |

## Recommended Learning Paths

**Path A · Systematic Survey (recommended)**: 01 Economics → 02 Accounting → 03 Finance → 04 Marketing → 05 Management → 08 Strategy → 07 Operations → 06 HR → 10 Analytics → 11 International → 12 Law & Ethics → 09 Entrepreneurship (final review)
First build the foundations of “where money comes from and how the books are kept,” then move on to “how to sell and how to manage,” and finish with integrated application.

**Path B · Fast Track for Managers**: 05 Management → 08 Strategy → 02 Accounting → 06 HR → 07 Operations → 10 Analytics
First learn to get results through others, then add the financial and data literacy that decisions require.

**Path C · Fast Track for Founders**: 09 Entrepreneurship → 08 Strategy → 04 Marketing → 03 Finance → 07 Operations → 12 Law & Ethics
Start by validating the idea, then solve positioning, customer acquisition, funding, delivery, and compliance in turn.

> You can switch between paths at any time — the prerequisite/follow-up relations between branches are marked on each branch guide page.

## Directory Structure

```
Business/
├── index.html               ← browser entry (Chinese overview)
├── README.md                ← Chinese README (this file's source)
├── README.en.md             ← this file (English edition)
├── MISSION.md / MISSION.en.md        ← learning mission (the anchor for all teaching)
├── RESOURCES.md / RESOURCES.en.md    ← curated trusted-resource library
├── NOTES.md / NOTES.en.md            ← learner preference record
├── STYLEGUIDE.md / STYLEGUIDE.en.md ← authoring standards (the production contract)
├── tools/
│   ├── check.py             ← automated self-check for the Chinese pages
│   ├── check_en.py          ← self-check for the en/ mirror
│   └── audit_en.py          ← page-by-page zh↔en structural comparison
├── assets/                  # shared design system & components (used by both languages)
│   ├── course.css           # unified styling (paper feel · Tufte style)
│   ├── quiz.js              # quiz component (instant feedback + scores auto-saved)
│   ├── viz.js               # SVG chart/slider/drag toolbox
│   ├── progress.js          # learning-progress badges for index pages
│   └── favicon.svg          # site icon
├── en/                      # English mirror of the site
│   ├── index.html           ← English overview (entry point)
│   ├── 01-economics/ … 12-business-law-ethics/
│   │   ├── index.html       # branch guide (English)
│   │   └── lessons/0001-….html
├── 01-economics/ … 12-business-law-ethics/   # Chinese edition
│   ├── index.html           # branch guide page (sub-branch map + learning path)
│   └── lessons/0001-….html  # interactive lessons (4 per branch)
└── learning-records/        # learning records (created as you progress)
```

Note: the English pages live one directory deeper, so they reference the shared assets with one more `../` (e.g. `../../../assets/course.css` inside a lesson page).

## How to Keep Learning

1. Open any lesson, read the body, play with the interactive simulation, and take the quiz;
2. **Progress is saved automatically**: quiz scores are stored in this browser (localStorage); the overview and branch guide pages show “n/4 lessons done” and your best score per lesson;
3. The “ask your teacher” footer: return to the conversation with your AI teacher and ask about anything in the lesson that is unclear;
4. After finishing a lesson, ask the AI teacher for more variation drills, or a deeper walkthrough applied to your industry;
5. Record important insights in `learning-records/` (just ask the AI teacher).

> Maintenance note: after adding or editing lessons in the Chinese edition, run `python tools/check.py` for a full self-check (live links, complete components, quiz standards, pager chain; zero dependencies; it skips the en/ mirror automatically). Validate the English mirror with `python tools/check_en.py`, and compare the two editions page by page with `python tools/audit_en.py` (quiz answer indices, ids, links).

## Methodology Acknowledgment

The materials-production methodology comes from the open-source teaching skill [mattpocock/skills · teach](https://www.skills.sh/mattpocock/skills/teach) (installed in the local skill library). Core principles: knowledge comes from trusted sources; skills come from interactive feedback; long-term memory comes from retrieval practice and spaced repetition.
