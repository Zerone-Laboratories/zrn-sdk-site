/* How the shell draws: the frame's layers spread apart as the page scrolls down and fold back as it scrolls up.
   The same geometry as gen/layers.py: each pane turns up to 60 degrees about its upright axis and 6 about its
   horizontal one, and the panes move apart along the stack, bottom layer at the front left. */
(function () {
  var ex = document.querySelector(".explode");
  if (!ex || !window.matchMedia || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  document.documentElement.classList.add("explode-on");
  var stage = ex.querySelector(".stage"), stack = ex.querySelector(".stack"), hint = ex.querySelector(".hint");
  var panes = [].slice.call(ex.querySelectorAll(".pane")).map(function (el) {
    return { el: el, face: el.querySelector(".face"), tag: el.querySelector(".ltag"), k: parseFloat(el.dataset.k), shown: el.dataset.shown === "1" };
  });
  /* the stack's width apart, in pane heights, with room for the last label on the right */
  var spread = 9 * 0.26 + 0.5625 * 0.5 + 0.2, label;
  function ease(x) { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); }
  var queued = false;
  function draw() {
    queued = false;
    var r = ex.getBoundingClientRect(), vh = window.innerHeight, run = r.height - vh;
    var p = run > 0 ? Math.min(1, Math.max(0, -r.top / run)) : 0;
    var t = ease((p - 0.08) / 0.62);
    var w = stage.clientWidth;
    /* names under the panes only where two panes apart (labels alternate above and below) fit one; else numbers */
    var full = Math.min(vh * 0.56, (w * 0.94 - 150) / spread), nums = 2 * 0.26 * full < 120;
    if (nums !== stack.classList.contains("nums")) stack.classList.toggle("nums", nums);
    label = nums ? 24 : 150;
    var flat = Math.min(vh * 0.66, w * 0.8 / 0.5625), apart = Math.min(vh * 0.56, (w * 0.94 - label) / spread);
    var h = flat + (apart - flat) * t, pw = h * 0.5625, gap = 0.26 * h * t;
    stack.style.width = pw + "px";
    stack.style.height = h + "px";
    stack.style.perspective = (5.5 * h) + "px";
    stack.style.transform = "translateX(" + (-label / 2 * t) + "px)";
    stack.style.setProperty("--t", t.toFixed(3));  /* the panes' glass shows only as they part */
    var tags = Math.min(1, Math.max(0, (t - 0.82) / 0.18));
    panes.forEach(function (q) {
      q.el.style.transform = "translate3d(" + (q.k * gap) + "px," + (-q.k * gap * 0.08) + "px," + (-q.k * gap * 0.3) + "px)";
      q.face.style.transform = "rotateX(" + (6 * t) + "deg) rotateY(" + (60 * t) + "deg)";
      q.el.style.opacity = q.shown ? 1 : Math.min(1, t * 1.6);
      q.tag.style.opacity = tags;
    });
    hint.style.opacity = Math.max(0, 1 - t * 4);
  }
  function queue() { if (!queued) { queued = true; requestAnimationFrame(draw); } }
  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", queue);
  draw();
})();
