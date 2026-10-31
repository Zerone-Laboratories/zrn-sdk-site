#!/usr/bin/env python3
"""Builds public/*.html from gen/pages.py and gen/elements.py."""
import html, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import elements as E, pages as P

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
LANGNAME = {"c": "C", "cpp": "C++", "rs": "Rust", "py": "Python"}
NAV = [("index", "Overview"), ("start", "Getting started"), ("apps", "Ways to make an app"),
       ("project", "Project and permissions"), ("elements", "UI elements"), ("layout", "Layout, themes, styles"),
       ("animations", "Animations"), ("shipping", "Package and publish"), ("troubleshooting", "Troubleshooting"),
       ("status", "Status and gaps")]


def tabs(codes):
    out = ['<div class="langs" data-langs><div role="tablist" aria-label="Language">']
    for k in codes:
        out.append('<button type="button" role="tab" data-l="%s" aria-selected="false">%s</button>' % (k, LANGNAME[k]))
    out.append('</div>')
    for k, code in codes.items():
        out.append('<pre data-l="%s" aria-label="%s"><code>%s</code></pre>' % (k, LANGNAME[k], html.escape(code)))
    out.append('</div>')
    return "\n".join(out)


def shots(name, tall=False):
    fig = []
    for tag, cap in (("cool-dark", "zrnCoolStyle, dark"), ("cool-light", "zrnCoolStyle, light"), ("metro", "Metro")):
        img = '<img src="img/%s-%s.webp" alt="%s rendered in %s" loading="lazy">' % (name, tag, name, cap)
        if tall:
            img = '<div class="tall" tabindex="0">%s</div>' % img
        fig.append('<figure>%s<figcaption>%s</figcaption></figure>' % (img, cap))
    return '<div class="shots">%s</div>' % "".join(fig)


def elements_html():
    out = []
    for e in E.ELEMENTS:
        codes = {k: e[k] for k in LANGNAME}
        if e.get("ctop"):
            codes["c"] = e["ctop"] + "\n\n" + codes["c"]
        out.append('<h2 id="%s">%s</h2><p>%s</p><p><code>%s</code></p>' % (e["id"], e["title"], e["blurb"], e["api"]))
        out.append(shots(e["id"], e.get("tall")))
        out.append(tabs(codes))
    return "\n".join(out)


def page(key, title, desc, body):
    links = "".join('<li><a class="n" href="%s"%s>%s</a></li>' % (
        "/" if k == "index" else "/" + k, ' aria-current="page"' if k == key else "", n) for k, n in NAV)
    canon = "https://sdk.ztos.online/" + ("" if key == "index" else key)
    return P.SHELL.format(title=html.escape(title), desc=html.escape(desc, quote=True), canon=canon,
                          links=links, body=body, commit=P.COMMIT)


def main():
    for key, (title, desc, body) in P.PAGES.items():
        body = body.replace("{{ELEMENTS}}", elements_html())
        body = re.sub(r"\{\{SHOTS:(\w+)\}\}", lambda m: shots(m.group(1)), body)
        body = re.sub(r"\{\{TAB:(\w+)\}\}", lambda m: tabs(P.TABS[m.group(1)]), body)
        (OUT / (key + ".html")).write_text(page(key, title, desc, body))
    urls = "".join("<url><loc>https://sdk.ztos.online/%s</loc></url>" % ("" if k == "index" else k) for k in P.PAGES if k != "404")
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % urls)
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://sdk.ztos.online/sitemap.xml\n")
    bad = []
    for f in OUT.glob("*.html"):
        if "—" in f.read_text():
            bad.append(f.name)
    if bad:
        sys.exit("em dash in " + ", ".join(bad))


main()
