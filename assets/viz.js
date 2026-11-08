/* ============================================================
   Business 课程库 · 可视化工具 viz.js
   零依赖的 SVG 图表与交互模拟工具集,供各课程共用。
   命名空间:window.Viz
   ============================================================ */
(function () {
  "use strict";

  var Viz = {};

  var SVG_NS = "http://www.w3.org/2000/svg";

  /* ---- 基础:创建 SVG 元素 ---------------------------------- */
  Viz.svgEl = function (tag, attrs) {
    var e = document.createElementNS(SVG_NS, tag);
    if (attrs) {
      for (var k in attrs) {
        if (k === "text") e.textContent = attrs[k];
        else e.setAttribute(k, attrs[k]);
      }
    }
    return e;
  };

  /* ---- 线性比例尺 -------------------------------------------- */
  Viz.scale = function (d0, d1, r0, r1) {
    var f = function (x) { return r0 + (x - d0) / (d1 - d0) * (r1 - r0); };
    f.invert = function (y) { return d0 + (y - r0) / (r1 - r0) * (d1 - d0); };
    return f;
  };

  /* ---- 创建带坐标系的画布 -------------------------------------
     opts: { w, h, margin:{t,r,b,l}, xDomain:[a,b], yDomain:[a,b],
             xLabel, yLabel, xTicks, yTicks, xFormat, yFormat }
     返回 { svg, gx(x), gy(y), fx(px), fy(py), plot }             */
  Viz.axes = function (container, opts) {
    var w = opts.w || 640, h = opts.h || 420;
    var m = Object.assign({ t: 18, r: 18, b: 46, l: 56 }, opts.margin);
    var svg = Viz.svgEl("svg", {
      viewBox: "0 0 " + w + " " + h,
      role: "img", style: "width:100%;height:auto;display:block"
    });
    var iw = w - m.l - m.r, ih = h - m.t - m.b;
    var xd = opts.xDomain || [0, 10], yd = opts.yDomain || [0, 10];
    var x = Viz.scale(xd[0], xd[1], m.l, m.l + iw);
    var y = Viz.scale(yd[0], yd[1], m.t + ih, m.t); // y 轴向下为正,翻转

    // 网格与刻度
    var gridColor = "#ece6da", tickLen = 5;
    (opts.yTicks || 5).toString;
    var ny = opts.yTicks || 5, nx = opts.xTicks || 5;
    for (var i = 0; i <= ny; i++) {
      var vy = yd[0] + (yd[1] - yd[0]) * i / ny;
      svg.appendChild(Viz.svgEl("line", {
        x1: m.l, x2: m.l + iw, y1: y(vy), y2: y(vy),
        stroke: gridColor, "stroke-width": 1
      }));
      var lbl = Viz.svgEl("text", {
        x: m.l - 8, y: y(vy) + 4, "text-anchor": "end",
        "font-size": 11, fill: "#a8a29e"
      });
      lbl.textContent = (opts.yFormat || Math.round)(vy);
      svg.appendChild(lbl);
    }
    for (var j = 0; j <= nx; j++) {
      var vx = xd[0] + (xd[1] - xd[0]) * j / nx;
      svg.appendChild(Viz.svgEl("line", {
        x1: x(vx), x2: x(vx), y1: m.t, y2: m.t + ih,
        stroke: gridColor, "stroke-width": 1
      }));
      var lblx = Viz.svgEl("text", {
        x: x(vx), y: m.t + ih + 18, "text-anchor": "middle",
        "font-size": 11, fill: "#a8a29e"
      });
      lblx.textContent = (opts.xFormat || Math.round)(vx);
      svg.appendChild(lblx);
    }
    // 轴
    svg.appendChild(Viz.svgEl("line", { x1: m.l, x2: m.l, y1: m.t, y2: m.t + ih, stroke: "#c9c1b2", "stroke-width": 1.5 }));
    svg.appendChild(Viz.svgEl("line", { x1: m.l, x2: m.l + iw, y1: m.t + ih, y2: m.t + ih, stroke: "#c9c1b2", "stroke-width": 1.5 }));
    // 轴标签
    if (opts.xLabel) {
      var lx = Viz.svgEl("text", { x: m.l + iw / 2, y: h - 6, "text-anchor": "middle", "font-size": 12.5, fill: "#57534e", "font-weight": 700 });
      lx.textContent = opts.xLabel; svg.appendChild(lx);
    }
    if (opts.yLabel) {
      var ly = Viz.svgEl("text", { x: 14, y: m.t + ih / 2, "text-anchor": "middle", "font-size": 12.5, fill: "#57534e", "font-weight": 700, transform: "rotate(-90 14 " + (m.t + ih / 2) + ")" });
      ly.textContent = opts.yLabel; svg.appendChild(ly);
    }
    container.appendChild(svg);

    return {
      svg: svg, x: x, y: y,
      iw: iw, ih: ih, m: m,
      plot: function (draw) { draw(svg, x, y, m, iw, ih); return this; }
    };
  };

  /* ---- 折线 -------------------------------------------------- */
  Viz.line = function (g, pts, opts) {
    opts = opts || {};
    var d = pts.map(function (p, i) {
      return (i === 0 ? "M" : "L") + p[0].toFixed(1) + " " + p[1].toFixed(1);
    }).join(" ");
    var path = Viz.svgEl("path", Object.assign({
      d: d, fill: "none", stroke: opts.color || "#b45309",
      "stroke-width": opts.width || 3,
      "stroke-linecap": "round", "stroke-linejoin": "round"
    }, opts.dash ? { "stroke-dasharray": opts.dash } : {}));
    if (opts.animate) {
      var len = path.getTotalLength ? 0 : 0; // path 未挂载前无法测长,用估算
      path.style.strokeDasharray = opts.dash || "1000";
      path.style.strokeDashoffset = opts.dash ? path.style.strokeDasharray : "1000";
      path.style.animation = "draw 1.4s ease-out forwards";
    }
    g.appendChild(path);
    return path;
  };

  /* ---- 点与标注 ---------------------------------------------- */
  Viz.dot = function (g, cx, cy, opts) {
    opts = opts || {};
    var c = Viz.svgEl("circle", {
      cx: cx, cy: cy, r: opts.r || 6,
      fill: opts.fill || "#b45309", stroke: "#fff", "stroke-width": 2
    });
    if (opts.pulse) {
      c.appendChild(Viz.svgEl("animate", {
        attributeName: "r", values: (opts.r || 6) + ";" + ((opts.r || 6) + 5) + ";" + (opts.r || 6),
        dur: "2s", repeatCount: "indefinite"
      }));
    }
    g.appendChild(c);
    return c;
  };

  Viz.label = function (g, x, y, text, opts) {
    opts = opts || {};
    var t = Viz.svgEl("text", {
      x: x, y: y, "font-size": opts.size || 12.5,
      fill: opts.color || "#57534e", "font-weight": opts.weight || 700,
      "text-anchor": opts.anchor || "start"
    });
    t.textContent = text;
    g.appendChild(t);
    return t;
  };

  Viz.area = function (g, pts, color, opacity) {
    // pts: 数据点路径(闭合区域),画半透明填充
    var d = pts.map(function (p, i) {
      return (i === 0 ? "M" : "L") + p[0].toFixed(1) + " " + p[1].toFixed(1);
    }).join(" ") + " Z";
    var p = Viz.svgEl("path", { d: d, fill: color, opacity: opacity == null ? 0.18 : opacity, stroke: "none" });
    g.appendChild(p);
    return p;
  };

  /* ---- 柱状图 -------------------------------------------------- */
  Viz.bars = function (container, data, opts) {
    opts = opts || {};
    var w = opts.w || 640, h = opts.h || 360;
    var m = Object.assign({ t: 14, r: 14, b: 40, l: 46 }, opts.margin);
    var svg = Viz.svgEl("svg", { viewBox: "0 0 " + w + " " + h, role: "img", style: "width:100%;height:auto;display:block" });
    var max = opts.max || Math.max.apply(null, data.map(function (d) { return d.value; })) * 1.15;
    var iw = w - m.l - m.r, ih = h - m.t - m.b;
    var bw = iw / data.length * 0.62;
    data.forEach(function (d, i) {
      var bh = d.value / max * ih;
      var bx = m.l + iw / data.length * (i + 0.5) - bw / 2;
      var by = m.t + ih - bh;
      var rect = Viz.svgEl("rect", {
        x: bx, y: by, width: bw, height: bh, rx: 6,
        fill: d.color || opts.color || "var(--accent)"
      });
      if (opts.animate !== false) {
        rect.style.transformOrigin = bx + "px " + (m.t + ih) + "px";
        rect.style.transformBox = "fill-box";
        rect.appendChild(Viz.svgEl("animate", {
          attributeName: "opacity", from: "0", to: "1", dur: "0.5s",
          begin: (i * 0.12) + "s", fill: "freeze"
        }));
      }
      svg.appendChild(rect);
      var val = Viz.svgEl("text", { x: bx + bw / 2, y: by - 6, "text-anchor": "middle", "font-size": 12, "font-weight": 800, fill: "#1c1917" });
      val.textContent = (opts.valueFormat || Math.round)(d.value);
      svg.appendChild(val);
      var lbl = Viz.svgEl("text", { x: bx + bw / 2, y: m.t + ih + 17, "text-anchor": "middle", "font-size": 11.5, fill: "#78716c" });
      lbl.textContent = d.label;
      svg.appendChild(lbl);
    });
    svg.appendChild(Viz.svgEl("line", { x1: m.l, x2: m.l + iw, y1: m.t + ih, y2: m.t + ih, stroke: "#c9c1b2", "stroke-width": 1.5 }));
    container.appendChild(svg);
    return svg;
  };

  /* ---- 滑块助手 ------------------------------------------------
     Viz.slider(container, {label, min, max, step, value, format})
     返回 { el, get(), set(v), onChange(cb) }                        */
  Viz.slider = function (container, opts) {
    var wrap = document.createElement("label");
    var name = document.createElement("span");
    name.textContent = opts.label || "";
    var input = document.createElement("input");
    input.type = "range";
    input.min = opts.min; input.max = opts.max;
    input.step = opts.step || 1; input.value = opts.value;
    var out = document.createElement("output");
    var cbs = [];
    function fmt(v) { return opts.format ? opts.format(v) : v; }
    function update() {
      out.textContent = fmt(parseFloat(input.value));
      var pct = (input.value - opts.min) / (opts.max - opts.min) * 100;
      input.style.setProperty("--fill", pct + "%");
      cbs.forEach(function (cb) { cb(parseFloat(input.value)); });
    }
    input.addEventListener("input", update);
    wrap.appendChild(name); wrap.appendChild(input); wrap.appendChild(out);
    container.appendChild(wrap);
    update();
    return {
      el: wrap,
      get: function () { return parseFloat(input.value); },
      set: function (v) { input.value = v; update(); },
      onChange: function (cb) { cbs.push(cb); }
    };
  };

  /* ---- 数字滚动动画 -------------------------------------------- */
  Viz.countUp = function (el, target, opts) {
    opts = opts || {};
    var dur = opts.dur || 900;
    var start = null;
    var from = opts.from || 0;
    function frame(t) {
      if (!start) start = t;
      var p = Math.min(1, (t - start) / dur);
      var eased = 1 - Math.pow(1 - p, 3);
      var v = from + (target - from) * eased;
      el.textContent = (opts.format || function (x) { return Math.round(x).toLocaleString(); })(v);
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  };

  /* ---- 滚动渐显 ------------------------------------------------ */
  Viz.reveal = function () {
    var els = document.querySelectorAll("[data-reveal]");
    if (!("IntersectionObserver" in window)) {
      els.forEach(function (e) { e.classList.add("visible"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("visible"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    els.forEach(function (e) { io.observe(e); });
  };

  /* ---- SVG 拖拽(鼠标 + 触摸)---------------------------------- */
  Viz.draggable = function (svg, targetEl, onMove) {
    var dragging = false;
    function pt(evt) {
      var r = svg.getBoundingClientRect();
      var cx = (evt.touches ? evt.touches[0].clientX : evt.clientX) - r.left;
      var cy = (evt.touches ? evt.touches[0].clientY : evt.clientY) - r.top;
      // viewBox 缩放换算
      var vb = svg.viewBox.baseVal;
      return { x: cx / r.width * vb.width, y: cy / r.height * vb.height };
    }
    function start(evt) { dragging = true; evt.preventDefault(); }
    function move(evt) {
      if (!dragging) return;
      var p = pt(evt);
      onMove(p);
      if (evt.cancelable) evt.preventDefault();
    }
    function end() { dragging = false; }
    targetEl.style.cursor = "grab";
    targetEl.style.touchAction = "none";
    targetEl.addEventListener("mousedown", start);
    targetEl.addEventListener("touchstart", start, { passive: false });
    svg.addEventListener("mousemove", move);
    svg.addEventListener("touchmove", move, { passive: false });
    window.addEventListener("mouseup", end);
    window.addEventListener("touchend", end);
  };

  document.addEventListener("DOMContentLoaded", Viz.reveal);

  window.Viz = Viz;
})();
