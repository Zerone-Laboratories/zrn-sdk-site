// Language tabs. Without this script every language simply shows, one after another.
(function () {
  var key = 'zrn-sdk-lang', lang = 'c';
  try { lang = localStorage.getItem(key) || 'c'; } catch (e) {}
  function apply(l) {
    document.querySelectorAll('[data-langs]').forEach(function (box) {
      var have = box.querySelector('pre[data-l="' + l + '"]') ? l : box.querySelector('pre').getAttribute('data-l');
      box.querySelectorAll('[role=tab]').forEach(function (t) { t.setAttribute('aria-selected', String(t.getAttribute('data-l') === have)); });
      box.querySelectorAll('pre').forEach(function (p) { p.hidden = p.getAttribute('data-l') !== have; });
    });
  }
  document.addEventListener('click', function (ev) {
    var t = ev.target.closest && ev.target.closest('[role=tab]');
    if (!t) return;
    var l = t.getAttribute('data-l');
    try { localStorage.setItem(key, l); } catch (e) {}
    apply(l);
  });
  apply(lang);
})();
