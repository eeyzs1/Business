# Business 通识课程库

> 一个可以离线浏览、交互式的商业通识课程库。12 个主分支 · 48 节课 · 全部中文。
> **English edition**:[`en/index.html`](en/index.html) — 每页导航栏右侧都有 中/EN 切换按钮。
> **入口:双击打开 [index.html](index.html)**,从任意分支开始。

本课程库遵循经过认知科学验证的学习方法(源自 `teach` 教学技能):

- **一课一概念**:每课 30-45 分钟,只攻一个界定清晰的概念;
- **交互优先**:价格曲线可以拖、复利可以拨、漏斗可以点——概念用动画和模拟器讲;
- **检索练习**:每课配即时反馈测验,答错有解析,重测巩固长期记忆;
- **真实案例**:每课一个真实公司案例,数字为示意量级;
- **教师在线**:每课页脚都提醒你:有疑问,回对话里问 AI 老师。

---

## 主分支全景(12 个)

Business 学科的标准主干,对应商学院课程体系。每个分支文件夹含 1 个导学页(`index.html`,含子分支全景与学习路径)和 4 节交互课(`lessons/`)。

| # | 主分支 | 一句话定位 | 核心子分支 | 入口 |
|---|--------|-----------|-----------|------|
| 01 | **经济学基础** Economics | 一切商业决策的底层操作系统:资源稀缺下的选择 | 微观经济学、宏观经济学、市场结构、经济政策 | [01-economics/](01-economics/index.html) |
| 02 | **会计学** Accounting | 企业的语言:读懂生意的体检报告 | 财务会计、管理会计、财务报表分析、审计与税务 | [02-accounting/](02-accounting/index.html) |
| 03 | **金融学** Finance | 钱的时间与价格:估值、投资与风险 | 货币时间价值、公司金融、投资学、金融市场与风险 | [03-finance/](03-finance/index.html) |
| 04 | **市场营销** Marketing | 创造顾客并留住顾客的科学 | 营销战略(STP)、营销组合(4P)、消费者行为、品牌与数字营销 | [04-marketing/](04-marketing/index.html) |
| 05 | **管理学** Management | 通过他人拿结果的学问 | 计划/组织/领导/控制、决策科学、组织行为学、领导力 | [05-management/](05-management/index.html) |
| 06 | **人力资源管理** Human Resources | 把人当成最重要的资产来经营 | 招聘选拔、绩效管理、薪酬激励、培训发展与组织文化 | [06-human-resources/](06-human-resources/index.html) |
| 07 | **运营与供应链** Operations & Supply Chain | 把承诺变成交付的引擎 | 流程与产能、质量管理、精益生产、供应链与项目管理 | [07-operations-supply-chain/](07-operations-supply-chain/index.html) |
| 08 | **战略管理** Strategy | 选择不做什么:构建长期竞争优势 | 行业分析(五力)、竞争战略、商业模式、公司战略 | [08-strategy/](08-strategy/index.html) |
| 09 | **创业学** Entrepreneurship | 从 0 到 1 的方法论 | 机会识别与验证、精益创业、商业计划、融资与股权 | [09-entrepreneurship/](09-entrepreneurship/index.html) |
| 10 | **商业分析** Business Analytics | 用数据讲商业故事并驱动决策 | 数据思维、描述统计与可视化、因果推断、商业智能 | [10-business-analytics/](10-business-analytics/index.html) |
| 11 | **国际商务** International Business | 跨越边境做生意 | 全球化与比较优势、国际贸易实务、跨国经营、跨文化管理 | [11-international-business/](11-international-business/index.html) |
| 12 | **商业伦理与法律** Business Law & Ethics | 商业的底线与护栏 | 公司法与合同、公司治理、商业伦理、ESG 与可持续 | [12-business-law-ethics/](12-business-law-ethics/index.html) |

## 推荐学习路径

**路径 A · 系统通识(推荐)**:01 经济学 → 02 会计 → 03 金融 → 04 营销 → 05 管理 → 08 战略 → 07 运营 → 06 HR → 10 分析 → 11 国际 → 12 伦理法律 → 09 创业(总复习)
先建立"钱从哪来、账怎么算"的底层,再看"怎么卖、怎么管",最后是综合应用。

**路径 B · 管理者速成**:05 管理学 → 08 战略 → 02 会计 → 06 HR → 07 运营 → 10 分析
先懂"通过他人拿结果",再补上决策所需的财务与数据语言。

**路径 C · 创业者速成**:09 创业 → 08 战略 → 04 营销 → 03 金融 → 07 运营 → 12 伦理法律
从验证想法开始,依次解决定位、获客、找钱、交付、合规。

> 每条路径都可以在任何时候切换——分支间的"前置/后续"关系在各自的导学页里标注。

## 目录结构

```
Business/
├── index.html               ← 浏览器入口(总览首页)
├── README.md                ← 本文件
├── MISSION.md               ← 学习使命(所有教学的锚点)
├── RESOURCES.md             ← 精选可信资源库
├── NOTES.md                 ← 你的学习偏好记录
├── STYLEGUIDE.md            ← 教材编写规范(教材生产合同)
├── tools/
│   ├── check.py             ← 自动化自检(链接/组件/quiz/pager 一键检查)
│   ├── check_en.py          ← 英文镜像自检
│   ├── audit_en.py          ← 中英逐页结构比对(答案索引/id/链接)
│   ├── html_checks.py       ← 共用的 HTML 链接与测验数据校验
│   ├── tests/              ← 零依赖的校验器回归测试
│   └── test_browser.py     ← 离线页面、手机布局与交互回归测试
├── assets/                  # 共享设计系统与组件
│   ├── course.css           # 统一样式(纸感·Tufte 风)
│   ├── quiz.js              # 测验组件(即时反馈 + 成绩自动保存)
│   ├── viz.js               # SVG 图表/滑块/拖拽工具箱
│   ├── progress.js          # 索引页学习进度徽章
│   └── favicon.svg          # 站点图标
├── 01-economics/ … 12-business-law-ethics/
│   ├── index.html           # 分支导学页(子分支全景+学习路径)
│   └── lessons/0001-….html  # 交互课程(每分支 4 课)
├── en/                      # 英文镜像(结构同上,共享 assets/,导航栏可中英切换)
└── learning-records/        # 学习记录(随学习进度产生)
```

## 如何继续学习

1. 打开任一课程,读完正文,玩交互模拟,做完测验;
2. **学习进度自动保存**:测验成绩记在本浏览器(localStorage),总览与分支导学页会显示"已学 n/4 课"和每课最好成绩;
3. 页脚的"问老师"提示:回到与 AI 的对话中,直接问课程里任何不清楚的概念;
4. 学完一课后,让 AI 老师出更多变式题、或结合你的行业深入讲解;
5. 重要领悟可以记入 `learning-records/`(问 AI 老师即可)。

> 维护提示:新增或修改课程后,运行 `python tools/check.py` 做全量自检(链接可达、组件齐全、quiz 规范、pager 链路等,零依赖;自动跳过英文镜像)。英文镜像用 `python tools/check_en.py` 校验,`python tools/audit_en.py` 可逐页比对中英结构(答案索引、id、链接)。

## 维护与验证

在仓库根目录运行以下检查,只需 Python 3.8+:

```sh
python tools/check.py
python tools/check_en.py
python tools/audit_en.py
python -m unittest discover -s tools/tests -v
```

静态校验覆盖跨页锚点、语言切换目标、测验数据结构、离线资源与页面组件。修改共享脚本、样式或交互课后,再用 Python 3.9+ 运行浏览器回归检查:

```sh
python -m pip install -r tools/requirements-dev.txt
python -m playwright install chromium
python tools/test_browser.py
```

浏览器检查会遍历 122 个本地页面,验证手机布局和滑块边界,并检查测验重测、成绩保存、英文文案、IRR、配对练习、拖拽坐标、键盘操作与打印。Windows 已安装 Chrome 时,也可在 PowerShell 中设置 `$env:BUSINESS_BROWSER_CHANNEL='chrome'` 后运行,无需下载 Chromium。开发测试依赖不影响课程离线浏览。提交到 GitHub 后,以上检查由 `.github/workflows/checks.yml` 自动执行。

中英文页面共用同一课程的最好成绩。成绩保存在当前浏览器的本地存储中,不会写入 `learning-records/`;清理浏览器数据、切换浏览器或网站来源会影响记录。双击文件时的跨页存储行为由浏览器决定。如果徽章无法跨页显示,可在仓库根目录启动本地服务,再打开 `http://127.0.0.1:8000/`:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

这个本地服务不需要互联网连接。供需图、定位图和极端值模拟器都可用滑块及方向键操作;测验成绩仅反映当次表现,建议隔几天再测以检验记忆。

## 方法论致谢

教材生产方法论来自开源教学技能 [mattpocock/skills · teach](https://www.skills.sh/mattpocock/skills/teach)(已安装到本地技能库),核心原则:知识来自可信来源、技能靠交互反馈获得、长期记忆靠检索练习与间隔重复。
