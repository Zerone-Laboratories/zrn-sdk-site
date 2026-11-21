#!/usr/bin/env python3
"""Builds public/*.html from gen/pages.py and gen/elements.py (SDK v2)."""
import html, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import elements as E, pages as P, layers as L

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
GEN = pathlib.Path(__file__).resolve().parent
NAV = [("index", "Overview"), ("start", "Getting started"), ("apps", "Ways to make an app"),
       ("project", "Project layout"), ("elements", "UI elements"), ("layout", "Layout and theme"),
       ("animations", "Animations"), ("shell", "How the shell draws"), ("shipping", "Build and ship"), ("publish", "Publish to the store"), ("troubleshooting", "Troubleshooting"),
       ("status", "Status and gaps"), ("next", "Coming next")]


def shots(name):
    fig = []
    for tag, cap in (("dark", "Dark"), ("light", "Light")):
        fig.append('<figure><img src="/img/%s-%s.webp" alt="%s drawn by zrnui in the %s theme" loading="lazy"><figcaption>%s</figcaption></figure>' % (name, tag, name, cap, cap))
    return '<div class="shots">%s</div>' % "".join(fig)


def frost():
    out = []
    for m, cap in (("none", "NONE"), ("normal", "NORMAL"), ("ascending", "ASCENDING: full at the top, fading down"), ("descending", "DESCENDING: full at the bottom, fading up")):
        out.append('<h3>Z_FROSTED_DIFFUSION_%s</h3><p>%s</p><div class="shots">%s</div>' % (m.upper(), cap, "".join(
            '<figure><img src="/img/frost-%s-%s.webp" alt="frosted diffusion %s in the %s theme" loading="lazy"><figcaption>%s</figcaption></figure>' % (m, t, m, t, t.title())
            for t in ("dark", "light"))))
    return "\n".join(out)


def clip(name):
    out = []
    for t in ("dark", "light"):
        out.append('<figure><video autoplay loop muted playsinline preload="auto" width="360" height="640" poster="/clips/%s-%s.webp" aria-label="%s, %s theme">'
                   '<source src="/clips/%s-%s.webm" type="video/webm"><source src="/clips/%s-%s.mp4" type="video/mp4"></video><figcaption>%s</figcaption></figure>'
                   % (name, t, name, t, name, t, name, t, t.title()))
    return '<div class="shots">%s</div>' % "".join(out)


def layers():
    """The exploded picture: dark or light with the reader's theme, a link to the full size."""
    pics = []
    for t in ("light", "dark"):
        pics.append('<a class="only-%s" href="/img/shell-layers-%s.png"><img src="/img/shell-layers-%s.webp" width="1600" height="1000" '
                    'alt="The ztMETRO frame at the left, and its ten layers spread out in perspective to the right, bottom to top: Start and the app list, '
                    'frost strips, app window, keyboard, status bar, action centre, nav bar, lock screen, call, volume and toasts"></a>' % (t, t, t))
    return '<figure class="layers">%s<figcaption>One frame of ztMETRO and its layers, bottom (left) to top (right). Open it full size.</figcaption></figure>' % "".join(pics)


def layer_stack():
    """The layers as panes that fan apart as the page scrolls and fold back as it scrolls up (assets/layers.js).
    Without script, or with reduced motion, it is not shown: the picture below says the same."""
    panes = []
    n = len(L.LAYERS)
    for i, (key, name, code_name, shown) in enumerate(L.LAYERS):
        imgs = "".join('<img class="only-%s" src="/img/layers/%s-%s.webp" alt="" width="540" height="960">' % (t, key, t) for t in ("light", "dark"))
        panes.append('<div class="pane" data-k="%g" data-shown="%d"><div class="face">%s</div>'
                     '<p class="ltag %s"><b>%02d</b><span class="nm"> %s</span><small>%s</small></p></div>'
                     % (i - (n - 1) / 2, 1 if shown else 0, imgs, "below" if i % 2 == 0 else "above", i + 1, name, html.escape(code_name)))
    return ('<div class="explode" role="img" aria-label="The layers of a ztMETRO frame, which spread apart as you scroll down and fold together as you scroll up">'
            '<div class="stage"><div class="stack">%s</div><p class="hint">Scroll, and the frame comes apart into its layers</p></div></div>'
            '<script src="/assets/layers.js" defer></script>' % "".join(panes))


def layer_clip():
    out = []
    for t in ("light", "dark"):
        out.append('<video class="only-%s" autoplay loop muted playsinline preload="metadata" width="1280" height="720" poster="/clips/shell-layers-%s.webp" '
                   'aria-label="The frame fans apart into its layers and folds back, %s theme"><source src="/clips/shell-layers-%s.webm" type="video/webm">'
                   '<source src="/clips/shell-layers-%s.mp4" type="video/mp4"></video>' % (t, t, t, t, t))
    return '<figure class="layers">%s</figure>' % "".join(out)


def code(c):
    return '<pre><code>%s</code></pre>' % html.escape(c)


def elements_html():
    out = []
    for e in E.ELEMENTS:
        src = (e["ctop"] + "\n\n" if e.get("ctop") else "") + e["c"]
        out.append('<h2 id="%s">%s</h2><p>%s</p><p><code>%s</code></p>' % (e["id"], e["title"], e["blurb"], e["api"]))
        out.append(shots(e["id"]))
        out.append(code(src))
    return "\n".join(out)


def page(key, title, desc, body):
    links = "".join('<li><a class="n" href="%s"%s>%s</a></li>' % (
        "/" if k == "index" else "/" + k, ' aria-current="page"' if k == key else "", n) for k, n in NAV)
    canon = "https://sdk.ztos.online/" + ("" if key == "index" else key)
    return P.SHELL.format(title=html.escape(title), desc=html.escape(desc, quote=True), canon=canon,
                          links=links, body=body, commit=P.COMMIT)


def main():
    hello = html.escape((GEN / "hello.c").read_text().replace("\t", "    ").rstrip())
    for key, (title, desc, body) in P.PAGES.items():
        body = body.replace("{{ELEMENTS}}", elements_html()).replace("{{HELLO}}", hello).replace("{{FROST}}", frost())
        body = body.replace("{{LAYERS}}", layers()).replace("{{LAYERCLIP}}", layer_clip()).replace("{{STACK}}", layer_stack())
        body = re.sub(r"\{\{SHOTS:(\w+)\}\}", lambda m: shots(m.group(1)), body)
        body = re.sub(r"\{\{CLIP:(\w+)\}\}", lambda m: clip(m.group(1)), body)
        (OUT / (key + ".html")).write_text(page(key, title, desc, body))
    urls = "".join("<url><loc>https://sdk.ztos.online/%s</loc></url>" % ("" if k == "index" else k) for k in P.PAGES if k != "404")
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % urls)
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://sdk.ztos.online/sitemap.xml\n")
    bad = [f.name for f in OUT.glob("*.html") if "—" in f.read_text()]
    if bad:
        sys.exit("em dash in " + ", ".join(bad))


main()
