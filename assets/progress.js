/* ============================================================
   Business 课程库 · 学习进度展示 progress.js
   读取 quiz.js 写入的 localStorage 记录(键前缀 biz-quiz:):
   - 分支导学页:在 .lesson-list 的课程项后追加「✓ 最好成绩」徽章;
   - 总览首页:在 .branch-card 卡片尾部追加「已学 n/4 课」。
   无记录 / localStorage 不可用时静默不显示。零依赖,离线可用。
   ============================================================ */
(function () {
  "use strict";

  var KEY_PREFIX = "biz-quiz:";

  function storage() {
    try { return window.localStorage; } catch (e) { return null; }
  }
  function read(key) {
    var s = storage();
    if (!s) return null;
    try {
      var v = JSON.parse(s.getItem(key));
      return v && typeof v.best === "number" ? v : null;
    } catch (e) { return null; }
  }
  // pathname → biz-quiz:branch/lessons/file.html(与 quiz.js 的键保持一致)
  function keyFor(pathname) {
    var m = decodeURIComponent(pathname).match(/([^\/]+\/lessons\/[^\/]+\.html)$/i);
    return m ? KEY_PREFIX + m[1] : null;
  }
  function resolveUrl(href) {
    try { return new URL(href, location.href); } catch (e) { return null; }
  }

  function markLessonList() {
    document.querySelectorAll(".lesson-list a[href]").forEach(function (a) {
      var url = resolveUrl(a.getAttribute("href"));
      if (!url) return;
      var rec = read(keyFor(url.pathname));
      if (!rec) return;
      var b = document.createElement("span");
      b.className = "ll-done";
      b.textContent = "✓ " + rec.best + "/" + rec.total;
      a.appendChild(b);
    });
  }

  function markBranchCards() {
    var s = storage();
    if (!s) return;
    var keys = [];
    try { keys = Object.keys(s); } catch (e) { return; }
    document.querySelectorAll(".branch-card[href]").forEach(function (card) {
      var url = resolveUrl(card.getAttribute("href"));
      if (!url) return;
      // pathname 形如 /F:/Business/01-economics/index.html → 取分支目录名
      var segs = url.pathname.replace(/[^\/]*$/, "").split("/").filter(Boolean);
      var dir = segs[segs.length - 1];
      if (!dir || !/^\d\d-/.test(dir)) return;
      var done = 0;
      keys.forEach(function (k) {
        if (k.indexOf(KEY_PREFIX) !== 0) return;
        if (("/" + k.slice(KEY_PREFIX.length)).indexOf("/" + dir + "/lessons/") === -1) return;
        if (read(k)) done++;
      });
      if (!done) return;
      var chip = document.createElement("div");
      chip.className = "bc-progress";
      chip.textContent = "已学 " + done + "/4 课";
      card.appendChild(chip);
    });
  }

  function init() { markLessonList(); markBranchCards(); }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
