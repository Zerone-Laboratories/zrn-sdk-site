#!/usr/bin/env python3
"""Builds public/*.html from gen/pages.py and gen/elements.py (SDK v2)."""
import html, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import elements as E, pages as P

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
GEN = pathlib.Path(__file__).resolve().parent
NAV = [("index", "Overview"), ("start", "Getting started"), ("apps", "Ways to make an app"),
       ("project", "Project layout"), ("elements", "UI elements"), ("layout", "Layout and theme"),
       ("animations", "Animations"), ("shipping", "Build and ship"), ("publish", "Publish to the store"), ("troubleshooting", "Troubleshooting"),
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
