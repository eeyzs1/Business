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
  var english = /^en(?:-|$)/i.test(document.documentElement.lang);
  var copy = english ? {
    next: "Next →", result: "See results →", retry: "↻ Try again",
    score: "Score ", best: "Best ", final: "Final score: ",
    correct: "✓ Correct.", wrong: "✗ Not quite.",
    full: "Great recall on this attempt! Come back in a few days to check what you retain. 🎉",
    good: "Well done! Revisit the explanations for missed questions, then try again in a few days.",
    practice: "Mistakes show what to practise. Review the explanations, then try recalling the ideas again.",
    recall: "✍️ <b>Retrieval practice</b>: before leaving, explain the key idea in your own words without looking at the lesson.",
    invalid: "This quiz could not be loaded. Please check its question data.",
    unsaved: "This attempt could not be saved in this browser.",
    progress: "Quiz progress"
  } : {
    next: "下一题 →", result: "查看结果 →", retry: "↻ 再试一次",
    score: "得分 ", best: "历史最好 ", final: "最终成绩:",
    correct: "✓ 回答正确。", wrong: "✗ 再想想。",
    full: "这次回忆得很准确!过几天再来测测,看看还能记住多少。🎉",
    good: "很不错!错题的解析值得再看一遍,过两天回来重测一次(间隔复习)。",
    practice: "错题提示了需要练习的地方。读完解析后点「再试一次」,重新回忆一遍。",
    recall: "✍️ <b>检索练习</b>:关闭页面之前,试着不看课文,用自己的话把本课最核心的概念讲一遍。",
    invalid: "测验暂时无法加载,请检查题目数据。",
    unsaved: "当前浏览器无法保存本次成绩。", progress: "测验进度"
  };

  function storage() {
    try { return window.localStorage; } catch (e) { return null; }
  }
  function quizKey() {
    // 取末三段,让中英页面共享键;实际保存范围仍由浏览器的来源/文件存储规则决定。
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
      return v && Number.isInteger(v.best) && Number.isInteger(v.total) &&
        v.total > 0 && v.best >= 0 && v.best <= v.total ? v : null;
    } catch (e) { return null; }
  }
  function writeRecord(rec) {
    var s = storage();
    if (!s) return false;
    try { s.setItem(quizKey(), JSON.stringify(rec)); return true; }
    catch (e) { return false; }
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
    } catch (e) { questions = null; }
    if (!Array.isArray(questions) || !questions.length || !questions.every(function (item) {
      return item && typeof item.q === "string" && item.q.trim() &&
        Array.isArray(item.options) && item.options.length >= 2 &&
        item.options.every(function (opt) { return typeof opt === "string" && opt.trim(); }) &&
        Number.isInteger(item.answer) && item.answer >= 0 && item.answer < item.options.length &&
        typeof item.explain === "string" && item.explain.trim();
    })) {
      var errorEl = el("p", "quiz-error");
      errorEl.textContent = copy.invalid;
      errorEl.setAttribute("role", "alert");
      box.appendChild(errorEl);
      return;
    }
    dataEl.remove();

    var total = questions.length;
    var idx = 0;
    var score = 0;
    var answered = false;

    var bar = el("div", "quiz-bar");
    bar.setAttribute("role", "progressbar");
    bar.setAttribute("aria-label", copy.progress);
    bar.setAttribute("aria-valuemin", "0");
    bar.setAttribute("aria-valuemax", String(total));
    var barFill = el("span");
    bar.appendChild(barFill);

    var qEl = el("div", "quiz-q");
    qEl.tabIndex = -1;
    var optsEl = el("div", "quiz-opts");
    var explainEl = el("div", "quiz-explain");
    explainEl.setAttribute("role", "status");
    explainEl.setAttribute("aria-live", "polite");
    explainEl.setAttribute("aria-atomic", "true");
    explainEl.style.display = "none";
    var metaEl = el("div", "quiz-meta");
    var scoreEl = el("span", "quiz-score");
    var historyEl = el("span", "quiz-history");
    var nextBtn = el("button", "quiz-next", copy.next);
    nextBtn.type = "button";

    var record = readRecord();
    if (record && record.total !== total) record = null;

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
        qEl.focus();
        return;
      }
      if (answered) {           // 习题页 → 前进或出分
        if (idx < total - 1) { idx++; renderQuestion(); }
        else renderResult();
        qEl.focus();
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
      nextBtn.textContent = copy.next;
      item.options.forEach(function (opt, i) {
        var b = el("button", "quiz-opt", opt);
        b.type = "button";
        b.addEventListener("click", function () { choose(i); });
        optsEl.appendChild(b);
      });
      scoreEl.textContent = copy.score + score + " / " + total;
      historyEl.textContent = record ? copy.best + record.best + " / " + record.total : "";
      barFill.style.width = (idx / total * 100) + "%";
      bar.setAttribute("aria-valuenow", String(idx));
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
        "<b>" + (correct ? copy.correct : copy.wrong) + "</b> " +
        (item.explain || "");
      explainEl.style.display = "block";
      scoreEl.textContent = copy.score + score + " / " + total;
      nextBtn.disabled = false;
      nextBtn.textContent = idx === total - 1 ? copy.result : copy.next;
      barFill.style.width = ((idx + 1) / total * 100) + "%";
      bar.setAttribute("aria-valuenow", String(idx + 1));
      nextBtn.focus();
    }

    function renderResult() {
      finished = true;
      barFill.style.width = "100%";
      qEl.innerHTML = "";
      optsEl.innerHTML = "";
      explainEl.style.display = "none";
      var pct = Math.round(score / total * 100);
      var comment;
      if (pct === 100) comment = copy.full;
      else if (pct >= 70) comment = copy.good;
      else comment = copy.practice;
      scoreEl.innerHTML =
        copy.final + "<b>" + score + " / " + total + "</b> (" + pct + "%) — " + comment;
      nextBtn.disabled = false;
      nextBtn.textContent = copy.retry;
      // Another tab may have saved a higher score while this attempt was open.
      var latest = readRecord();
      var best = latest && latest.total === total ? latest.best : 0;
      record = {
        best: Math.max(record ? record.best : 0, best, score),
        last: score, total: total, at: Date.now()
      };
      var saved = writeRecord(record);
      historyEl.textContent = saved ? copy.best + record.best + " / " + record.total : copy.unsaved;
      qEl.appendChild(el("p", "", copy.recall));
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
