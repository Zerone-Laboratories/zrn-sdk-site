/* How the shell draws: the frame's layers, captured on the S9, come apart as the page scrolls down and
   fold back as it scrolls up. Layer 01 (Start) is in front and each later layer further back; Start is
   built from its tiles (gen/layers.json), each flat in its place on layer 01. The geometry is gen/layers.py's: each quad is projected here and drawn with a
   matrix3d that maps the element onto it. */
(function () {
  var ex = document.querySelector(".explode");
  if (!ex || !window.matchMedia || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var M = JSON.parse(ex.dataset.meta), A = M.aspect, n = M.layers.length;
  document.documentElement.classList.add("explode-on");
  var stage = ex.querySelector(".stage"), stack = ex.querySelector(".stack"), hint = ex.querySelector(".hint");

  function el(tag, cls, parent) { var e = document.createElement(tag); e.className = cls; parent.appendChild(e); return e; }
  function img(src, cls) { var e = el("img", cls, stack); e.src = src; e.alt = ""; e.decoding = "async"; return e; }
  /* painted back to front: the last layer first, 01 and its tiles last, then the frame as seen */
  var panes = [], tiles = [];
  for (var i = n - 1; i >= 0; i--) {
    panes[i] = img("/img/layers/" + M.layers[i].key + ".webp", "q pane");
    if (i === 0) M.tiles.forEach(function (tm, k) { tiles[k] = img("/img/layers/tile-" + (k < 10 ? "0" : "") + k + ".webp", "q ttile"); });
  }
  var flat = img("/img/layers/flat.webp", "q pane");
  var tags = M.layers.map(function (l, i) {
    var p = el("p", "ltag " + (i % 2 ? "above" : "below"), stack);
    p.innerHTML = "<b>" + (i < 9 ? "0" : "") + (i + 1) + "</b><span class=nm> " + l.name + "</span><small>" + l.code.replace("\n", "<br>") + "</small>";
    return p;
  });

  var R = Math.PI / 180;
  function point(i, x, y, z, t) {
    var th = M.turn * t * R, ph = M.tilt * t * R;
    var X = x * Math.cos(th) + z * Math.sin(th), Z = x * Math.sin(th) - z * Math.cos(th);
    var Y = y * Math.cos(ph) - Z * Math.sin(ph); Z = y * Math.sin(ph) + Z * Math.cos(ph);
    X += i * M.step[0] * t; Y += i * M.step[1] * t; Z += i * M.step[2] * t;
    var s = M.eye / (M.eye + Z);
    return [X * s, Y * s];
  }
  function pane(i, t) {
    var hw = A / 2;
    return [point(i, -hw, -0.5, 0, t), point(i, hw, -0.5, 0, t), point(i, hw, 0.5, 0, t), point(i, -hw, 0.5, 0, t)];
  }
  /* the tiles sit flat on layer 01, where they are in the capture */
  function amount() { return 0; }
  /* a tile on layer 01 (amount() is 0, so it lies flat where it was captured) */
  function tile(tm, t) {
    var turn = 26 * tm.turn * amount(tm, t) * R, r = tm.rect, edge = -A / 2;
    var x0 = r[0] * A - A / 2, y0 = r[1] - 0.5, x1 = r[2] * A - A / 2, y1 = r[3] - 0.5;
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]].map(function (c) {
      var d = c[0] - edge;
      return point(0, edge + d * Math.cos(turn), c[1], d * Math.sin(turn), t);
    });
  }
  /* the CSS transform that puts a 100 x 100 box onto a quad */
  function quad(e, q, s, ox, oy) {
    var x = q.map(function (p) { return ox + s * p[0]; }), y = q.map(function (p) { return oy + s * p[1]; });
    var dx1 = x[1] - x[2], dx2 = x[3] - x[2], dx3 = x[0] - x[1] + x[2] - x[3];
    var dy1 = y[1] - y[2], dy2 = y[3] - y[2], dy3 = y[0] - y[1] + y[2] - y[3];
    var det = dx1 * dy2 - dx2 * dy1, g = (dx3 * dy2 - dx2 * dy3) / det, h = (dx1 * dy3 - dx3 * dy1) / det;
    var a = x[1] - x[0] + g * x[1], b = x[3] - x[0] + h * x[3], c = y[1] - y[0] + g * y[1], d = y[3] - y[0] + h * y[3];
    e.style.transform = "matrix3d(" + [a / 100, c / 100, 0, g / 100, b / 100, d / 100, 0, h / 100, 0, 0, 1, 0, x[0], y[0], 0, 1].join(",") + ")";
  }
  function fit(t, x0, y0, x1, y1) {
    var xs = [], ys = [];
    for (var i = 0; i < n; i++) pane(i, t).forEach(function (p) { xs.push(p[0]); ys.push(p[1]); });
    var mx = Math.min.apply(0, xs), Mx = Math.max.apply(0, xs), my = Math.min.apply(0, ys), My = Math.max.apply(0, ys);
    var s = Math.min((x1 - x0) / (Mx - mx), (y1 - y0) / (My - my));
    return [s, (x0 + x1) / 2 - s * (Mx + mx) / 2, (y0 + y1) / 2 - s * (My + my) / 2];
  }
  function ease(x) { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); }

  var queued = false;
  function draw() {
    queued = false;
    var r = ex.getBoundingClientRect(), vh = window.innerHeight, run = r.height - vh;
    var p = run > 0 ? Math.min(1, Math.max(0, -r.top / run)) : 0;
    var t = ease((p - 0.06) / 0.66);
    var w = stage.clientWidth, h = stage.clientHeight, phone = w < 700;
    var fh = Math.min(h * 0.72, w * 0.8 / A);
    var f0 = [fh, w / 2, h / 2];
    var side = phone ? 8 : 130, f1 = fit(1, phone ? 8 : 16, h * (phone ? 0.2 : 0.13), w - side, h * (phone ? 0.8 : 0.85));
    var s = f0[0] + (f1[0] - f0[0]) * t, ox = f0[1] + (f1[1] - f0[1]) * t, oy = f0[2] + (f1[2] - f0[2]) * t;
    var glass = Math.min(1, t * 3);
    for (var i = 0; i < n; i++) {
      quad(panes[i], pane(i, t), s, ox, oy);
      panes[i].style.opacity = M.layers[i].shown ? 1 : Math.min(1, Math.max(0, (t - 0.3) / 0.3));
      panes[i].style.setProperty("--g", glass);
    }
    var order = M.tiles.map(function (tm, k) { return [amount(tm, t), k]; }).sort(function (a, b) { return a[0] - b[0]; });
    order.forEach(function (o, z) {
      var k = o[1];
      quad(tiles[k], tile(M.tiles[k], t), s, ox, oy);
      tiles[k].style.opacity = Math.min(1, Math.max(0, (t - 0.3) / 0.3));
      tiles[k].style.zIndex = 1 + z;  /* (a tile further out is over one still in place) */
    });
    quad(flat, pane(0, t), s, ox, oy);
    flat.style.opacity = Math.max(0, 1 - t / 0.2);
    flat.style.zIndex = 100;
    var la = Math.min(1, Math.max(0, (t - 0.85) / 0.15));
    var cs = [];
    for (i = 0; i < n; i++) cs.push(pane(i, t).map(function (q) { return [ox + s * q[0], oy + s * q[1]]; }));
    var top = Math.min.apply(0, cs.map(function (c) { return c[0][1]; })) - 22;
    var bottom = Math.max.apply(0, cs.map(function (c) { return c[3][1]; })) + 22;
    /* labels alternate above and below: names only where every other pane is far enough apart, else numbers */
    var gapx = Infinity;
    for (i = 2; i < n; i++) gapx = Math.min(gapx, cs[i][0][0] - cs[i - 2][0][0]);
    var nums = phone || gapx < 100;
    if (nums !== stack.classList.contains("nums")) stack.classList.toggle("nums", nums);
    tags.forEach(function (g, i) {
      var c = cs[i], below = i % 2 === 0, a = below ? c[3] : c[0], b = below ? c[2] : c[1];
      var ax = a[0] + (b[0] - a[0]) * 0.2, ay = a[1] + (b[1] - a[1]) * 0.2;
      g.style.left = ax + "px";
      g.style.top = (below ? bottom : top) + "px";
      g.style.setProperty("--lead", Math.max(0, below ? bottom - ay - 4 : ay - top - 4) + "px");
      g.style.opacity = la;
    });
    hint.style.opacity = Math.max(0, 1 - t * 4);
  }
  function queue() { if (!queued) { queued = true; requestAnimationFrame(draw); } }
  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", queue);
  draw();
})();
