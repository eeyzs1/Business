/* ============================================================
   Business 课程库 · 测验组件 quiz.js
   检索练习 + 即时反馈。用法:在页面放置
   <div class="quiz">
     <script type="application/json">
     [
       { "q": "题干",
         "options": ["选项A", "选项B", "选项C", "选项D"],
         "answer": 2,
         "explain": "解析文字,支持 <b>重点</b>" }
     ]
     </script>
   </div>
   并在页面底部引入本脚本。answer 为正确选项的下标(从 0 开始)。
   ============================================================ */
(function () {
  "use strict";

  /* ---- 学习进度持久化(localStorage,可选能力,不可用时静默降级)---- */
  var KEY_PREFIX = "biz-quiz:";

  function storage() {
    try { return window.localStorage; } catch (e) { return null; }
  }
  function quizKey() {
    // 取 pathname 末三段(branch/lessons/file.html),课程库整体移动/换盘也不丢进度
    var m = location.pathname.match(/([^\/]+\/lessons\/[^\/]+\.html)$/i);
    try {
      return KEY_PREFIX + decodeURIComponent(m ? m[1] : location.pathname);
    } catch (e) {
      return KEY_PREFIX + (m ? m[1] : location.pathname);
    }
  }
  function readRecord() {
    var s = storage();
    if (!s) return null;
    try {
      var v = JSON.parse(s.getItem(quizKey()));
      return v && typeof v.best === "number" ? v : null;
    } catch (e) { return null; }
  }
  function writeRecord(rec) {
    var s = storage();
    if (!s) return;
    try { s.setItem(quizKey(), JSON.stringify(rec)); } catch (e) { /* 隐私模式/配额:忽略 */ }
  }

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  function initQuiz(box) {
    var dataEl = box.querySelector('script[type="application/json"]');
    if (!dataEl) return;
    var questions;
    try {
      questions = JSON.parse(dataEl.textContent);
    } catch (e) {
      console.error("quiz 数据解析失败", e);
      return;
    }
    if (!questions.length) return;
    dataEl.remove();

    var total = questions.length;
    var idx = 0;
    var score = 0;
    var answered = false;

    var bar = el("div", "quiz-bar");
    var barFill = el("span");
    bar.appendChild(barFill);

    var qEl = el("div", "quiz-q");
    var optsEl = el("div", "quiz-opts");
    var explainEl = el("div", "quiz-explain");
    explainEl.style.display = "none";
    var metaEl = el("div", "quiz-meta");
    var scoreEl = el("span", "quiz-score");
    var historyEl = el("span", "quiz-history");
    var nextBtn = el("button", "quiz-next", "下一题 →");
    nextBtn.type = "button";

    var record = readRecord();

    box.appendChild(bar);
    box.appendChild(qEl);
    box.appendChild(optsEl);
    box.appendChild(explainEl);
    box.appendChild(metaEl);
    metaEl.appendChild(scoreEl);
    metaEl.appendChild(historyEl);
    metaEl.appendChild(nextBtn);

    nextBtn.addEventListener("click", function () {
      if (finished) {           // 结果页 → 重新开始
        idx = 0; score = 0; finished = false;
        box.insertBefore(bar, box.firstChild);
        renderQuestion();
        return;
      }
      if (answered) {           // 习题页 → 前进或出分
        if (idx < total - 1) { idx++; renderQuestion(); }
        else renderResult();
      }
    });

    var finished = false;

    function renderQuestion() {
      answered = false;
      var item = questions[idx];
      qEl.innerHTML = '<span class="quiz-qno">Q' + (idx + 1) + "/" + total + "</span>" + item.q;
      optsEl.innerHTML = "";
      explainEl.style.display = "none";
      nextBtn.disabled = true;
      nextBtn.textContent = "下一题 →";
      item.options.forEach(function (opt, i) {
        var b = el("button", "quiz-opt", opt);
        b.type = "button";
        b.addEventListener("click", function () { choose(i); });
        optsEl.appendChild(b);
      });
      scoreEl.textContent = "得分 " + score + " / " + total;
      historyEl.textContent = record ? "历史最好 " + record.best + " / " + record.total : "";
      barFill.style.width = (idx / total * 100) + "%";
    }

    function choose(i) {
      if (answered) return;
      answered = true;
      var item = questions[idx];
      var buttons = optsEl.querySelectorAll(".quiz-opt");
      buttons.forEach(function (b, j) {
        b.disabled = true;
        if (j === item.answer) b.classList.add("correct");
        else if (j === i) b.classList.add("wrong");
      });
      var correct = i === item.answer;
      if (correct) score++;
      explainEl.innerHTML =
        (correct ? "<b>✓ 回答正确。</b> " : "<b>✗ 再想想。</b> ") +
        (item.explain || "");
      explainEl.style.display = "block";
      scoreEl.textContent = "得分 " + score + " / " + total;
      nextBtn.disabled = false;
      nextBtn.textContent = idx === total - 1 ? "查看结果 →" : "下一题 →";
    }

    function renderResult() {
      finished = true;
      barFill.style.width = "100%";
      qEl.innerHTML = "";
      optsEl.innerHTML = "";
      explainEl.style.display = "none";
      var pct = Math.round(score / total * 100);
      var comment;
      if (pct === 100) comment = "满分!这些概念已经进入你的长期记忆库了。🎉";
      else if (pct >= 70) comment = "很不错!错题的解析值得再看一遍,过两天回来重测一次(间隔复习)。";
      else comment = "别灰心——错题正是学习发生的地方。读完解析后点「再试一次」,重新回忆一遍效果最好。";
      scoreEl.innerHTML =
        "最终成绩:<b>" + score + " / " + total + "</b>(" + pct + " 分)—— " + comment;
      nextBtn.disabled = false;
      nextBtn.textContent = "↻ 再试一次";
      record = {
        best: Math.max(record ? record.best : 0, score),
        last: score, total: total, at: Date.now()
      };
      writeRecord(record);
      historyEl.textContent = "历史最好 " + record.best + " / " + record.total;
      qEl.appendChild(el("p", "", "✍️ <b>检索练习</b>:关闭页面之前,试着不看解析,用自己的话把本课最核心的概念讲一遍——这比再看一遍课文更能巩固记忆。"));
      qEl.firstChild.style.cssText = "font-size:.92rem;color:var(--ink-soft);background:var(--paper-deep);border-radius:8px;padding:.7rem .95rem;";
    }

    renderQuestion();
  }

  function initAll() {
    document.querySelectorAll(".quiz").forEach(initQuiz);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }
})();
