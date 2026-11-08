# STYLEGUIDE · Business 课程库教材编写规范

本规范是全部教材的「合同」。任何一课、任何分支的页面都必须遵守。规范源自 `teach` 教学技能的方法论:知识(可信来源)→ 技能(交互练习+即时反馈)→ 长期记忆(检索练习)。

## 1. 目录结构与命名

```
F:\Business\
├── index.html              # 总览首页(HTML)
├── README.md               # 总览(Markdown,与 index.html 同步)
├── MISSION.md / RESOURCES.md / NOTES.md
├── STYLEGUIDE.md           # 本规范
├── tools\
│   └── check.py            # 自动化自检(交付前必跑,见第 8 节)
├── assets\                 # 共享组件(课程生成会话不得修改)
│   ├── course.css          # 设计系统
│   ├── quiz.js             # 测验组件(含成绩持久化)
│   ├── viz.js              # SVG 图表/滑块/拖拽工具
│   ├── progress.js         # 索引页学习进度徽章
│   └── favicon.svg         # 站点图标
├── 01-economics\
│   ├── index.html          # 分支导学页
│   └── lessons\
│       ├── 0001-supply-and-demand.html
│       ├── 0002-....html
│       └── 0004-....html
├── 02-accounting\ ...
└── 12-business-law-ethics\ ...
```

- 课程文件名:全小写 kebab-case,四位编号递增。
- **禁止**在课程生成会话中修改 `assets/` 与 `tools/` 下任何文件;禁止新建全局共享文件。分支专用的 JS/SVG 一律内联在页面里。

## 2. 页面骨架(每课必须)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{课题} · {分支中文名}</title>
<link rel="stylesheet" href="../../assets/course.css">
<link rel="icon" type="image/svg+xml" href="../../assets/favicon.svg">
</head>
<body class="branch-economics">  <!-- 用本分支的 branch-* 类 -->
<nav class="lesson-nav"><div class="inner">
  <a href="../../index.html">总览</a><span class="crumb-sep">/</span>
  <a href="../index.html">{分支中文名}</a><span class="crumb-sep">/</span>
  <span>{课题}</span>
  <span class="progress">第 2 课 · 共 4 课</span>
  <a class="lang-switch" href="{对应另一语言的同页路径}">EN/中文</a>
</div></nav>

<main class="container">
  <p class="hero-eyebrow">{分支中文名} · LESSON 2</p>
  <h1>{课题}</h1>
  <p class="lead">{为什么学这个:1-3 句,连接到"看懂商业世界"这个总使命}</p>

  <!-- 正文分节,h2 带 <span class="secno">1</span> 编号 -->

  <div class="concept">…定义卡…</div>
  <figure class="figure"><div class="figure-body">…SVG…</div>
    <figcaption class="figure-caption"><b>图 1</b> …说明…</figcaption></figure>
  <div class="sim">…交互模拟(至少 1 个)…</div>
  <div class="case">…真实公司案例…</div>
  <div class="glossary">…本课术语…</div>
  <div class="takeaway">…关键要点…</div>

  <div class="quiz"><script type="application/json">[…]</script></div>

  <section id="further">  <!-- 延伸阅读 -->
  <nav class="pager">…上一课 / 下一课…</nav>
  <footer class="lesson-footer">
    <div class="ask-teacher"><b>有疑问?</b>回到对话里直接问你的 AI 老师…</div>
  </footer>
</main>

<script src="../../assets/viz.js"></script>
<script src="../../assets/quiz.js"></script>
<script>/* 本课专属交互逻辑(可选) */</script>
</body></html>
```

路径规则:分支 `index.html` 与课程页的相对路径不同——分支首页用 `../assets/...`,课程页(在 `lessons/` 下)用 `../../assets/...`。
语言切换:每个页面(中文版与 `en/` 镜像)的顶部导航末尾必须带 `<a class="lang-switch">` 胶囊按钮,指向另一语言的对应页面(中文页显示 EN,英文页显示 中文);新增页面时两语言必须成对增补。

## 3. 内容要求(教学法)

1. **一课一概念**:每课只教一个界定清晰的概念,30-45 分钟可完成。正文 1200-2200 汉字,不要贪多——学习者的工作记忆很小。
2. **写作语言**:简体中文;专业术语首次出现时括注英文,如:毛利润(Gross Profit)。
3. **讲解顺序**:先"为什么"(这个概念解决什么商业问题)→ 再"是什么"(定义)→ 再"怎么用"(交互练习)→ 最后案例。
4. **交互优先**:每课至少 1 个交互元素——滑块模拟器(`.sim` + `Viz.slider`)、可拖拽图表(`Viz.draggable`)或分步动画 SVG。概念能用图就不用字,能交互就不用静态图。
5. **真实案例**:每课 1 个 `.case`,使用真实公司(苹果、丰田、可口可乐、Netflix、Zara、海底捞、茅台、微软等)。数字用"约/量级"表述并标注"示意",**禁止编造精确财务数字**。
6. **术语表**:每课 `.glossary` 收录本课 4-8 个术语,dl/dt/dd 结构。
7. **关键要点**:`.takeaway` 用 3 句以内总结本课最核心的一句话。
8. **上一步/下一步**:`.pager` 首课的"上一课"= `../index.html`(回到分支导学);末课的"下一课"= 下一分支的 `../../{下一分支}/index.html`(最后一个分支则指回 `../../index.html` 总览)。注意:课程页在 `lessons/` 下,跨分支链接必须用 `../../`。模板统一为 `<span class="pager-label">`(不要用 div):标签文案固定为「← 上一课」「下一课 →」,分支末课为「下一分支 →」,第 12 分支末课为「返回总览 →」;标题文本保留实际课名。
9. **教师提醒**:页脚固定保留 `.ask-teacher` 提醒学习者回到对话提问。

## 4. 测验规范(quiz)

- 每课 3-5 题,单选,JSON 格式见 `assets/quiz.js` 顶部注释。
- **选项等长**:同一题各选项字数尽量一致,严禁在长度或格式上泄漏答案。
- **答案位置轮换**:正确答案的下标在 A/B/C/D 间轮换,不得集中。
- 每题必带 `explain` 解析,答错时能从解析学到东西。
- 出题考**辨析与应用**(场景判断、概念区分),不出"哪一年""谁提出的"这类纯记忆题。

## 5. 引用与延伸阅读

- 每课"延伸阅读"2-3 项,优先真实经典书目,格式:`《书名》作者 · 出版社(建议读:第X章)`。书目不加链接。
- 网络来源只允许白名单:`zh.wikipedia.org` / `en.wikipedia.org` 的**常见词条**(只链你确信存在的词条名)、`investopedia.com` 首页。**严禁编造 URL**;不确定就写书名或"可搜索关键词:xxx"。
- 经典书目参考库(按分支选用,均为真实存在的教材):曼昆《经济学原理》、萨缪尔森《经济学》、《会计学:企业决策的基础》(Wild)、罗斯《公司理财》、博迪《投资学》、科特勒《营销管理》、罗宾斯《管理学》、德鲁克《管理的实践》、《组织行为学》(罗宾斯)、史蒂文森《运营管理》、波特《竞争战略》《竞争优势》、奥斯特瓦德《商业模式新生代》、埃里克·莱斯《精益创业》、彼得·蒂尔《从0到1》、霍夫曼《联盟》、《国际商务》(希尔)、查尔斯·惠伦《赤裸裸的统计学》、卡尔·纽波特…等。不确定真实性的书不要写。

## 6. 技术规范

- UTF-8、`lang="zh-CN"`、语义化标签,页面在浏览器直接打开即用,**零外部依赖**(无 CDN、无网络字体、无图片外链;图形一律内联 SVG 或 CSS)。
- HTML 属性值用双引号;JSON 内中文引号正常使用,但不要在 JSON 字符串里出现未转义的双引号(用中文引号「」代替)。
- 交互组件优先复用 `Viz.*` API(见 `assets/viz.js`):`Viz.axes`(坐标系)、`Viz.line/dot/label/area`、`Viz.bars`、`Viz.slider`(拖动回调按帧合并,`set()` 保持同步)、`Viz.countUp`、`Viz.draggable`、`Viz.reveal`。滚动渐显给元素加 `data-reveal` 即可。
- 代码放在 `</body>` 前;确保无 JS 报错(所有 DOM 查询在脚本运行时已存在)。
- 样式兜底:凡使用 `color-mix()` 的声明,前一行必须放等价的实色/rgba 兜底值(不支持 color-mix 的浏览器取前一行)。
- 学习进度:`quiz.js` 自动把每课最好成绩存入 localStorage(键 `biz-quiz:{branch}/lessons/{file}.html`),索引页由 `progress.js` 渲染徽章——课程页无需任何额外代码。不要在课程页自行读写这些键。
- 打印友好:核心内容不得依赖 hover 才可见。

## 7. 分支导学页 index.html 规范

- `<body class="branch-xxx">`,引入 `../assets/course.css`、`<link rel="icon" ... href="../assets/favicon.svg">`。
- 结构:hero(分支名+一句话定位)→ **子分支全景**(表格:子分支名/核心问题/本分支状态[已覆盖·第X课/进阶待学])→ 学习路径(为什么按这个顺序)→ `.lesson-list` 课程列表(带一句副标题)→ 与其他分支的关系(前置/后续)→ 页脚。
- 分支首页也要有 `.ask-teacher` 页脚。
- 页尾引入 `<script src="../assets/progress.js"></script>`(自动在课程列表渲染学习进度徽章)。

## 8. 交付前自查清单

- [ ] **运行 `python tools/check.py` 全绿**(零依赖,自动覆盖下面的大部分项:路径/死链/组件/quiz/pager/id/配色/favicon)
- [ ] 每课 ≥1 交互、1 案例、1 术语表、1 takeaway、1 quiz
- [ ] quiz 选项等长、答案位置轮换、每题有解析
- [ ] 案例公司真实,数字标注"约/示意"
- [ ] 延伸阅读书目真实存在
