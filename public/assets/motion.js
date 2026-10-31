// The SDK's animations, frame by frame, with the same formulas as the C code.
// Each curve below is a port of a named function; animations.html cites them.
// Nothing here uses CSS transitions: every value is computed from the clock, so
// the scrubber can show any instant.
(function () {
  'use strict';
  var clamp01 = function (v) { return v < 0 ? 0 : v > 1 ? 1 : v; };

  // libzrnui/src/core.c
  function easeOut(t) { t = clamp01(t); var u = 1 - t; return 1 - u * u * u; }
  function easeIn(t) { t = clamp01(t); return t * t * t; }
  function easeEmph(t) { // cubic Bezier (0.2, 0.8, 0.2, 1), 8 Newton steps
    t = clamp01(t);
    var x1 = 0.2, y1 = 0.8, x2 = 0.2, y2 = 1, s = t, u;
    for (var i = 0; i < 8; i++) {
      u = 1 - s;
      var x = 3 * u * u * s * x1 + 3 * u * s * s * x2 + s * s * s - t;
      var dx = 3 * u * u * x1 + 6 * u * s * (x2 - x1) + 3 * s * s * (1 - x2);
      if (Math.abs(dx) < 1e-5) break;
      s = clamp01(s - x / dx);
    }
    u = 1 - s;
    return 3 * u * u * s * y1 + 3 * u * s * s * y2 + s * s * s;
  }
  // ztmetro/core/zrnmetrocore.c, zt_shape
  function shape(c, w, t) {
    var k = w / 30;
    if (c === 'e') return (Math.exp(k * t) - 1) / (Math.exp(k) - 1);
    if (c === 'l') return 1 - (Math.exp(k * (1 - t)) - 1) / (Math.exp(k) - 1);
    if (c === 's') {
      var f0 = 1 / (1 + Math.exp(w / 2)), f1 = 1 / (1 + Math.exp(-w / 2));
      return (1 / (1 + Math.exp(-w * (t - 0.5))) - f0) / (f1 - f0);
    }
    return t;
  }

  // the eye: libzrnui/src/gfx.c and zrnmetrogpu.c, 34 degree field of view
  var H = 740, W = 360, EYE = (H / 2) / Math.tan(17 * Math.PI / 180);
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function el(tag, cls, parent, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    if (parent) parent.appendChild(n);
    return n;
  }
  function stage(host, cls, h) {
    var phone = el('div', 'phone ' + (cls || ''), host);
    var inner = el('div', 'screen', phone);
    h = h || H;
    inner.style.height = h + 'px';
    inner.style.perspective = EYE + 'px';
    function fit() {
      var k = phone.clientWidth / W;
      inner.style.transform = 'scale(' + k + ')';
      phone.style.height = h * k + 'px';
    }
    fit();
    addEventListener('resize', fit);
    return inner;
  }
  function row(parent, y, h, title, sub, cls) {
    var r = el('div', 'r ' + (cls || ''), parent);
    r.style.top = y + 'px';
    r.style.height = h + 'px';
    el('span', 'rt', r, title);
    if (sub) el('span', 'rs', r, sub);
    return r;
  }

  // ---- demos: each returns { ms, frame(ms), options? } --------------------

  function coolPage(host, dir) {
    var s = stage(host, 'cool');
    var mk = function (title, names) {
      var rows = [row(s, 8, 48, title, null, 'big')];
      var y = 66;
      names.forEach(function (n) { rows.push(row(s, y, 56, n, null, 'card')); y += 62; });
      return rows;
    };
    var a = mk('Settings', ['Wi-Fi', 'Bluetooth', 'Sounds', 'Display', 'Battery']);
    var b = mk('Wi-Fi', ['Home-5G', 'Cafe', 'Workshop', 'Hidden network']);
    var from = dir > 0 ? a : b, to = dir > 0 ? b : a, total = 380;
    return { ms: total, frame: function (ms) {
      var t = clamp01(ms / total);
      var e = easeOut(clamp01(t / 0.35));
      var tx = (dir > 0 ? -W * 0.04 : W * 0.10) * e;
      from.forEach(function (r) { r.style.transform = 'translateX(' + tx + 'px)'; r.style.opacity = 1 - e; });
      to.forEach(function (r, i) {
        var n = i > 8 ? 8 : i, delay = n * 14;
        var u = clamp01((t * total - delay) / (total - delay));
        var f = easeEmph(u);
        r.style.transform = 'translateX(' + ((dir > 0 ? 1 : -1) * W * (dir > 0 ? 0.16 : 0.06) * (1 - f)) + 'px)';
        r.style.opacity = clamp01((u - 0.18) / 0.42);
      });
    } };
  }

  function metroRows(s, title, names) {
    var rows = [row(s, 8, 96, title, null, 'mt')];
    var y = 116;
    names.forEach(function (n) { rows.push(row(s, y, 66, n[0], n[1], 'mr')); y += 66; });
    return rows;
  }
  var SET = [['wi-fi', 'Home-5G'], ['bluetooth', 'off'], ['sounds', 'ring'], ['display', '60%'], ['battery', '82%']];
  var WIFI = [['Home-5G', 'connected'], ['Cafe', 'open'], ['Workshop', 'saved']];

  // libzrnui/src/style-metro.c, page_xf
  function metroPage(host, dir) {
    var s = stage(host, 'metro');
    var a = metroRows(s, 'settings', SET), b = metroRows(s, 'wi-fi', WIFI);
    var from = dir > 0 ? a : b, to = dir > 0 ? b : a;
    function order(i, rows) {
      var r = i + 1;
      if (dir < 0) r = rows - i;
      return r > 7 ? 7 : r;
    }
    return { ms: 720, frame: function (ms) {
      from.forEach(function (n, i) {
        var u = clamp01((ms - order(i, from.length) * 28) / 128);
        n.style.transform = 'rotateY(' + ((dir > 0 ? -50 : 50) * easeIn(u)) + 'deg)';
        n.style.opacity = u >= 1 ? 0 : 1 - u * u;
      });
      to.forEach(function (n, i) {
        var u = clamp01((ms - 330 - order(i, to.length) * 28) / 180);
        n.style.transform = 'rotateY(' + (80 * (1 - easeOut(u))) + 'deg)';
        n.style.opacity = u <= 0 ? 0 : clamp01(u * 3);
      });
    } };
  }

  // ztmetro/core/zrnmetrocore.c, the page change in ZrnMetroCore's own apps
  function corePage(host, dir) {
    var s = stage(host, 'metro');
    var a = metroRows(s, 'settings', SET), b = metroRows(s, 'wi-fi', WIFI);
    var from = dir > 0 ? a : b, to = dir > 0 ? b : a;
    var ord = function (i, n) { return dir > 0 ? i : n - 1 - i; };
    var outMs = (from.length - 1) * 33 + 128, inAt = outMs + 120, total = inAt + (to.length - 1) * 33 + 180;
    return { ms: total, frame: function (ms) {
      from.forEach(function (n, i) {
        var t = clamp01((ms - ord(i, from.length) * 33) / 128), e = t * t;
        n.style.transform = 'rotateY(' + ((dir > 0 ? -50 : 50) * e) + 'deg)';
        n.style.opacity = ms >= outMs ? 0 : e < 0.7 ? 1 : (1 - e) / 0.3;
      });
      to.forEach(function (n, i) {
        var t = clamp01((ms - inAt - ord(i, to.length) * 33) / 180), u = 1 - t, e = 1 - u * u * u;
        n.style.transform = 'rotateY(' + (80 * (1 - e)) + 'deg)';
        n.style.opacity = t <= 0 ? 0 : e > 0.3 ? 1 : e / 0.3;
      });
    } };
  }

  // ztanims[] in zrnmetrocore.c: [axis, from, to, pivot, s0, s1, dy0, dy1, a0, a1, ms, weight, curve]
  var CATALOGUE = {
    'turnstile-in': [0, -80, 0, 0, 1, 1, 0, 0, 1, 1, 350, 60, 'l'],
    'turnstile-out': [0, 0, 50, 0, 1, 1, 0, 0, 1, 0, 128, 60, 'e'],
    'swivel-in': [1, -45, 0, 0.5, 1, 1, 0, 0, 1, 1, 300, 200, 'l'],
    'swivel-out': [1, 0, 60, 0.5, 1, 1, 0, 0, 1, 1, 200, 150, 'e'],
    'continuum-hide': [1, 0, 80, 0, 1, 1, 0, 120, 1, 0, 120, 60, 'e'],
    'continuum-show': [1, -50, 0, 0, 1.5, 1, -60, 0, 0, 1, 350, 60, 'l'],
    'readerboard-in': [1, -45, 0, 0, 1, 1, 0, 0, 0, 1, 166, 60, 'l'],
    'readerboard-out': [1, 0, 90, 0, 1, 1, 0, 0, 1, 0, 166, 60, 'e'],
    'slide-up-fade-in': [0, 0, 0, 0, 1, 1, 24, 0, 0, 1, 240, 150, 'l'],
    'rotate-90': [2, 90, 0, 0.5, 1, 1, 0, 0, 1, 1, 167, 7.5, 's'],
    'fade-in': [0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 350, 150, 'l'],
    'fade-out': [0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 150, 150, 'e'],
    'tile-flip-notify': [1, -180, 0, 0.5, 1, 1, 0, 0, 1, 1, 520, 0, 'o']
  };
  // zt_corners: rotation about the pivot, then scale about the middle, then dy.
  function pose(A, t) {
    var e, deg;
    if (A[12] === 'o') { // -180 to 35 (Log 10), to -6 (SCurve 10), to 0 (linear)
      if (t < 0.367) deg = -180 + 215 * shape('l', 10, t / 0.367);
      else if (t < 0.833) deg = 35 - 41 * shape('s', 10, (t - 0.367) / (0.833 - 0.367));
      else deg = -6 + 6 * (t - 0.833) / (1 - 0.833);
      e = 1;
    } else {
      e = shape(A[12], A[11], t);
      deg = A[1] + (A[2] - A[1]) * e;
    }
    return { deg: deg, scale: A[4] + (A[5] - A[4]) * e, dy: A[6] + (A[7] - A[6]) * e, alpha: A[8] + (A[9] - A[8]) * e };
  }
  function place(n, A, p, w, h) {
    var rot, px = 0, py = 0;
    // The core's z is u*sin(a): on Y that is CSS rotateY(-a), on X rotateX(a).
    if (A[0] === 0) { px = w * A[3]; rot = 'rotateY(' + (-p.deg) + 'deg)'; }
    else if (A[0] === 1) { py = h * A[3]; rot = 'rotateX(' + p.deg + 'deg)'; }
    else { px = w / 2; py = h / 2; rot = 'rotateZ(' + p.deg + 'deg)'; }
    n.style.transformOrigin = '0 0';
    n.style.transform = 'translate3d(' + (w / 2) + 'px,' + (h / 2 + p.dy) + 'px,0) scale3d(' + p.scale + ',' + p.scale + ',' + p.scale + ') translate(' + (-w / 2 + px) + 'px,' + (-h / 2 + py) + 'px) ' + rot + ' translate(' + (-px) + 'px,' + (-py) + 'px)';
    n.style.opacity = p.alpha;
  }
  function named(host, name) {
    var A = CATALOGUE[name], s = stage(host, 'metro mini', 300);
    s.style.perspectiveOrigin = '50% 50%';
    var w = 260, h = 110, n = el('div', 'tile', s, name);
    n.style.cssText += ';left:50px;top:95px;width:' + w + 'px;height:' + h + 'px';
    return { ms: A[10], hold: true, frame: function (ms) {
      place(n, A, pose(A, clamp01(ms / A[10])), w, h);
    } };
  }

  // zrnboard.h and board_frame in zrnmetrocore.c: the domino, 12 ms a tile
  function board(host) {
    var s = stage(host, 'metro');
    metroRows(s, 'people', [['Ada', ''], ['Ben', ''], ['Cara', ''], ['Dev', ''], ['Eli', ''], ['Faye', '']]);
    var scrim = el('div', 'scrim', s);
    var tiles = [], side = 74.25, pitch = side + 9, x0 = (W - 4 * side - 3 * 9) / 2;
    '#abcdefghijklmnopqrstuvwxyz◌'.split('').forEach(function (c, i) {
      var live = '#abcdefg'.indexOf(c) >= 0;
      var n = el('div', 'tile' + (live ? '' : ' dim'), s, c);
      n.style.cssText += ';left:' + (x0 + (i % 4) * pitch) + 'px;top:' + (9 + Math.floor(i / 4) * pitch) + 'px;width:' + side + 'px;height:' + side + 'px';
      tiles.push(n);
    });
    var IN = CATALOGUE['swivel-in'], OUT = CATALOGUE['swivel-out'];
    var inEnd = 27 * 12 + 300, hold = 500, outAt = inEnd + hold, total = outAt + 27 * 12 + 200;
    return { ms: total, frame: function (ms) {
      scrim.style.opacity = ms < outAt ? 0.85 * clamp01(ms / 100) : 0.85 * (1 - clamp01((ms - outAt) / (total - outAt)));
      tiles.forEach(function (n, i) {
        if (ms < outAt) {
          var own = ms - i * 12;
          n.style.visibility = own < 0 ? 'hidden' : 'visible';
          place(n, IN, pose(IN, clamp01(own / 300)), side, side);
        } else {
          var o = ms - outAt - i * 12;
          n.style.visibility = o >= 200 ? 'hidden' : 'visible';
          place(n, OUT, pose(OUT, clamp01(o / 200)), side, side);
        }
      });
    } };
  }

  // press: libzrnui core.c (90 in, 200 or 220 out) with each style's press_xf
  function press(host) {
    var s = stage(host, 'metro', 300);
    var rs = [row(s, 30, 66, 'tilts toward the finger', 'press near an edge', 'mr'), row(s, 110, 66, 'press a corner', 'or the middle', 'mr')];
    var b = el('div', 'tile flat', s, 'buttons fill');
    b.style.cssText += ';left:16px;top:200px;width:328px;height:40px';
    var cur = rs[0], fx = 0.9, fy = 0, from = 0, to = 1, start = 0, dur = 90, live = false;
    function apply(n, a) {
      // press_xf in style-metro.c returns at once for a button: it fills instead
      if (n === b) { n.style.background = 'rgba(255,255,255,' + a + ')'; n.style.color = a > 0.5 ? '#000' : '#fff'; return; }
      var w = n.offsetWidth, h = n.offsetHeight;
      var lift = function (d) { return d > 0 ? Math.asin(Math.min(1, 40 / (d / 2))) * 180 / Math.PI : 14; };
      var dy = fx * Math.min(14, lift(w)) * a, dx = fy * Math.min(14, lift(h)) * a;
      n.style.transformOrigin = '50% 50%';
      n.style.transform = 'scale(' + (1 - 0.045 * a) + ') rotateX(' + dx + 'deg) rotateY(' + dy + 'deg)';
    }
    function value(ms) { return from + (to - from) * easeOut(clamp01((ms - start) / dur)); }
    [rs[0], rs[1], b].forEach(function (n) {
      n.addEventListener('pointerdown', function (ev) {
        var q = n.getBoundingClientRect();
        rs.forEach(function (m) { m.style.transform = ''; });
        cur = n; fx = (ev.clientX - q.left) / q.width * 2 - 1; fy = (ev.clientY - q.top) / q.height * 2 - 1;
        live = true; from = 0; to = 1; dur = 90; start = performance.now();
        var at = start;
        (function tick(now) {
          apply(cur, value(now - 0));
          if (live || now - start < dur) requestAnimationFrame(tick);
        })(at);
      });
      var up = function () {
        if (!live || cur !== n) return;
        var now = performance.now();
        from = value(now); to = 0; dur = 200; start = now; live = false;
      };
      n.addEventListener('pointerup', up);
      n.addEventListener('pointerleave', up);
    });
    return { ms: 90 + 120 + 200, frame: function (ms) {
      if (live) return;
      cur = rs[0]; fx = 0.9; fy = 0;
      var a = ms < 90 ? easeOut(ms / 90) : ms < 210 ? 1 : 1 - easeOut((ms - 210) / 200);
      apply(cur, a);
    } };
  }

  function toggleKnob(host, style) {
    var s = stage(host, style, 120), metro = style === 'metro';
    var track = el('div', 'tk', s), fill = el('div', 'tkf', track), knob = el('div', 'kn', track);
    return { ms: 180, frame: function (ms) {
      var k = easeOut(ms / 180);
      fill.style.opacity = k;
      knob.style.transform = 'translateX(' + (metro ? 1 + k * 40 : 3 + k * 20) + 'px)';
    } };
  }

  function toast(host, style) {
    var s = stage(host, style, 300), metro = style === 'metro';
    el('div', 'rt pad', s, metro ? 'settings' : 'Settings');
    var t = el('div', metro ? 'tm' : 'tc', s, 'Saved');
    return { ms: 2600, frame: function (age) {
      var shown = easeOut(age < 200 ? age / 200 : age > 2300 ? (2600 - age) / 300 : 1);
      if (metro) t.style.transform = 'translateY(' + (-(1 - shown) * 60) + 'px)';
      else { t.style.opacity = shown; t.style.transform = 'translate(-50%,' + ((1 - shown) * 16) + 'px)'; }
    } };
  }

  function busy(host, style) {
    var s = stage(host, style, 160), metro = style === 'metro';
    el('div', 'rt pad', s, metro ? 'settings' : 'Settings');
    if (metro) {
      var dots = [0, 1, 2, 3, 4].map(function () { return el('div', 'dot', s); });
      return { ms: 2600, loop: true, frame: function (ms) {
        dots.forEach(function (d, i) {
          var p = (ms % 2600) / 2000 - i * 0.075;
          d.style.opacity = p < 0 || p > 1 ? 0 : 1;
          var c = p - 0.5;
          d.style.transform = 'translateX(' + (W * (0.5 + 4 * c * c * c) - 2) + 'px)';
        });
      } };
    }
    var seg = el('div', 'seg', s);
    seg.style.width = W * 0.3 + 'px';
    return { ms: 1300, loop: true, frame: function (ms) {
      var p = (ms % 1300) / 1300;
      seg.style.transform = 'translateX(' + (-W * 0.3 + (W + W * 0.3) * easeEmph(p)) + 'px)';
    } };
  }

  function indeterminate(host) {
    var s = stage(host, 'cool', 80);
    var bar = el('div', 'bar', s), seg = el('div', 'seg in', bar), w = 324;
    return { ms: 1400, loop: true, frame: function (ms) {
      var p = (ms % 1400) / 1400, len = w * 0.35, at = -len + (w + len) * easeOut(p);
      var a = Math.max(at, 0), b = Math.min(at + len, w);
      seg.style.left = a + 'px';
      seg.style.width = Math.max(0, b - a) + 'px';
    } };
  }

  function focus(host) {
    var s = stage(host, 'cool', 100), f = el('div', 'fld', s, 'Search');
    return { ms: 150, frame: function (ms) { f.style.borderColor = 'rgba(0,80,239,' + easeOut(ms / 150) + ')'; } };
  }

  // fling: core.c zui_step. Simulated in 1 ms steps, so the scrubber can go anywhere.
  function fling(host) {
    var s = stage(host, 'cool'), list = el('div', 'list', s), n = 24, rowH = 62;
    for (var i = 0; i < n; i++) row(list, i * rowH, 56, 'Row ' + (i + 1), null, 'card');
    var max = n * rowH - H + 20, v0 = 3.2;
    var pos = [0], scroll = 0, vel = v0, flinging = true;
    for (var t = 1; t < 6000; t++) {
      if (flinging) {
        scroll += vel;
        vel *= Math.pow(0.9972, 1);
        if (scroll < 0 || scroll > max) vel *= Math.pow(0.8, 1 / 16);
        if (Math.abs(vel) < 0.02) { flinging = false; vel = 0; }
      }
      if (!flinging && (scroll < 0 || scroll > max)) {
        var tgt = scroll < 0 ? 0 : max;
        scroll += (tgt - scroll) * (1 - Math.exp(-1 / 70));
        if (Math.abs(tgt - scroll) < 0.3) scroll = tgt;
      }
      pos.push(scroll);
    }
    var end = pos.length - 1;
    while (end > 1 && pos[end] === pos[end - 1]) end--;
    return { ms: end, frame: function (ms) {
      list.style.transform = 'translateY(' + (-pos[Math.min(Math.round(ms), pos.length - 1)]) + 'px)';
    } };
  }

  var DEMOS = {
    'cool-forward': function (h) { return coolPage(h, 1); },
    'cool-back': function (h) { return coolPage(h, -1); },
    'metro-forward': function (h) { return metroPage(h, 1); },
    'metro-back': function (h) { return metroPage(h, -1); },
    'core-forward': function (h) { return corePage(h, 1); },
    'core-back': function (h) { return corePage(h, -1); },
    board: board, press: press, fling: fling, focus: focus, indeterminate: indeterminate,
    'knob-cool': function (h) { return toggleKnob(h, 'cool'); },
    'knob-metro': function (h) { return toggleKnob(h, 'metro'); },
    'toast-cool': function (h) { return toast(h, 'cool'); },
    'toast-metro': function (h) { return toast(h, 'metro'); },
    'busy-cool': function (h) { return busy(h, 'cool'); },
    'busy-metro': function (h) { return busy(h, 'metro'); }
  };
  Object.keys(CATALOGUE).forEach(function (k) { DEMOS['n:' + k] = function (h) { return named(h, k); }; });

  function mount(root) {
    var name = root.getAttribute('data-demo');
    var host = el('div', 'demo-stage', root);
    var d = DEMOS[name](host);
    var bar = el('div', 'demo-bar', root);
    var play = el('button', 'btn small', bar, 'Replay');
    play.type = 'button';
    var speedBtn = el('button', 'btn small ghost', bar, '1x');
    speedBtn.type = 'button';
    speedBtn.title = 'Speed';
    var range = el('input', '', bar);
    range.type = 'range'; range.min = 0; range.max = d.ms; range.value = reduced ? d.ms : 0;
    range.setAttribute('aria-label', 'Time in milliseconds');
    var read = el('output', 'read', bar);
    var speed = 1, raf = 0;
    function show(ms) { d.frame(ms); range.value = ms; read.textContent = Math.round(ms) + ' / ' + d.ms + ' ms'; }
    function stop() { cancelAnimationFrame(raf); raf = 0; }
    function run() {
      stop();
      var t0 = performance.now(), wait = d.loop ? 0 : 0;
      (function tick(now) {
        var ms = (now - t0 - wait) * speed;
        if (d.loop) ms = ms % d.ms;
        else if (ms >= d.ms) { show(d.ms); raf = 0; return; }
        show(Math.max(0, ms));
        raf = requestAnimationFrame(tick);
      })(t0);
    }
    root._run = run;
    play.addEventListener('click', run);
    speedBtn.addEventListener('click', function () {
      speed = speed === 1 ? 0.25 : speed === 0.25 ? 0.1 : 1;
      speedBtn.textContent = speed + 'x';
      run();
    });
    range.addEventListener('input', function () { stop(); show(+range.value); });
    show(d.loop || !reduced ? 0 : d.ms);
    if (reduced) { root.classList.add('still'); return; }
    if (window.IntersectionObserver) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) { if (d.loop || !root._seen) run(); root._seen = true; }
          else if (d.loop) stop();
        });
      }, { threshold: 0.4 }).observe(root);
    }
  }
  document.querySelectorAll('[data-demo]').forEach(mount);

  // curve plots: draw what the formula gives
  document.querySelectorAll('[data-curve]').forEach(function (svg) {
    var spec = svg.getAttribute('data-curve').split(':'), f;
    if (spec[0] === 'out') f = easeOut;
    else if (spec[0] === 'in') f = easeIn;
    else if (spec[0] === 'emph') f = easeEmph;
    else f = function (t) { return shape(spec[0], +spec[1], t); };
    var d = '';
    for (var i = 0; i <= 80; i++) {
      var t = i / 80;
      d += (i ? 'L' : 'M') + (t * 100).toFixed(1) + ' ' + (100 - f(t) * 100).toFixed(1);
    }
    svg.innerHTML = '<rect x="0" y="0" width="100" height="100" fill="none" stroke="var(--faint)" vector-effect="non-scaling-stroke"/><path d="' + d + '" fill="none" stroke="currentColor" vector-effect="non-scaling-stroke"/>';
  });

  window.ZRN_EASE = { easeOut: easeOut, easeIn: easeIn, easeEmph: easeEmph, shape: shape };
  window.ZRN_JUMP = function (name, ms) { // for the site's own render checks
    document.querySelectorAll('[data-demo="' + name + '"] input[type=range]').forEach(function (r) {
      r.value = ms; r.dispatchEvent(new Event('input'));
    });
  };
})();
