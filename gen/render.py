#!/usr/bin/env python3
"""Compile every element in C, C++, Rust and Python, render them with
`zrn render`, compare the languages pixel by pixel, and write optimised images
to public/img plus proof/report.txt.

    SDK=/path/to/zrn-sdk WORK=/path/to/scratch python3 gen/render.py
"""
import hashlib, os, pathlib, shutil, subprocess, sys
from PIL import Image, ImageChops
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import elements as E

ROOT = pathlib.Path(__file__).resolve().parent.parent
SDK = pathlib.Path(os.environ["SDK"]).resolve()
WORK = pathlib.Path(os.environ["WORK"]).resolve()
IMG = ROOT / "public/img"
ZRN = str(SDK / "tools/zrn")
# The phone's own fonts, from a ztOS checkout, for these renders only: never copied to public/.
FONTS = pathlib.Path(os.environ["ZTOS_FONTS"]).resolve()
WORK.mkdir(parents=True, exist_ok=True)
(WORK / "fonts.conf").write_text("""<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>
<dir>%s</dir><dir>/usr/share/fonts</dir><cachedir>%s/fc</cachedir></fontconfig>""" % (FONTS, WORK))
ENV = dict(os.environ, HOME=str(WORK / "home"), ZUI_ACCENT="cobalt", TMPDIR=str(WORK),
           FONTCONFIG_FILE=str(WORK / "fonts.conf"),
           PATH=str(SDK / "tools") + ":" + os.environ["PATH"])
for k in ("ZUI_STYLE", "ZUI_THEME", "ZTRF_SHELL_STYLE", "ZTMETRO_SCALE", "ZUI_SCALE"):
    ENV.pop(k, None)
(WORK / "home").mkdir(parents=True, exist_ok=True)
IMG.mkdir(parents=True, exist_ok=True)
(ROOT / "proof").mkdir(exist_ok=True)


def run(*a, cwd=None, check=True, env=None):
    r = subprocess.run(a, cwd=cwd, env=env or ENV, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit("FAILED %s\n%s\n%s" % (" ".join(map(str, a)), r.stdout, r.stderr))
    return r.stdout + r.stderr


def webp(src, dst, q=82):
    Image.open(src).convert("RGB").save(dst, "WEBP", quality=q, method=6)


PROJ = {"c": ("c", "main.c", E.program_c), "cpp": ("cpp", "main.cpp", E.program_cpp),
        "rs": ("rust", "src/main.rs", E.program_rs), "py": ("python", "main.py", E.program_py)}
report = ["libzrnui source: " + run("git", "-C", str(SDK), "rev-parse", "HEAD", check=False).strip() if (SDK / ".git").exists()
          else "libzrnui source: " + os.environ.get("SDK_COMMIT", "unknown")]

dirs = {}
for key, (lang, main, gen) in PROJ.items():
    d = WORK / ("proof-" + key)
    shutil.rmtree(d, ignore_errors=True)
    run(ZRN, "new", "Proof " + key, "--lang", lang, "--id", "zrn-proof-" + key, "--dir", str(d))
    (d / main).write_text(gen(E.ELEMENTS))
    (ROOT / "proof" / ("elements." + {"c": "c", "cpp": "cpp", "rs": "rs", "py": "py"}[key])).write_text(gen(E.ELEMENTS))
    print("build", key, flush=True)
    run(ZRN, "build", cwd=d)
    dirs[key] = d

STYLES = ["metro", "dotmatrix"]
bad = 0
for e in E.ELEMENTS:
    size = "360x%d" % e["h"]
    for style in STYLES:
        pics = {}
        for key, d in dirs.items():
            if key not in e:
                continue
            out = WORK / ("%s-%s-%s.png" % (e["id"], style, key))
            run(ZRN, "render", "--page", e["title"], "--style", style,
                "--size", size, "--scale", str(e.get("scale", 2)), str(out), cwd=d)
            pics[key] = out
        base = Image.open(pics["c"]).convert("RGB")
        res = []
        for key in pics:
            if key == "c":
                continue
            other = Image.open(pics[key]).convert("RGB")
            same = other.size == base.size and ImageChops.difference(base, other).getbbox() is None
            res.append("%s=%s" % (key, "same" if same else "DIFFERENT"))
            if not same and not e.get("animated"):
                bad += 1
        report.append("%-10s %-10s %s" % (e["id"], style, " ".join(res)))
        webp(pics["c"], IMG / ("%s-%s.webp" % (e["id"], style)))
report.append("unexpected differences: %d" % bad)
report.append("(progress holds moving dots, so its frames may differ by the instant drawn)")

# DotMatrix's six palettes, on one page
cfgdir = WORK / "home/.config/ztmetro"
cfgdir.mkdir(parents=True, exist_ok=True)
for k in range(6):
    (cfgdir / "config").write_text("dotmatrix_palette = %d\n" % k)
    run(ZRN, "render", "--page", "List rows", "--style", "dotmatrix", "--size", "360x400", "--scale", "1",
        str(WORK / ("pal%d.png" % k)), cwd=dirs["c"])
(cfgdir / "config").unlink()
ims = [Image.open(WORK / ("pal%d.png" % k)).convert("RGB") for k in range(6)]
strip = Image.new("RGB", (366 * 6 - 6, 400), (128, 128, 128))
for j, im in enumerate(ims):
    strip.paste(im, (j * 366, 0))
strip.save(IMG / "palettes.webp", "WEBP", quality=85, method=6)

# live: what only exists while an app runs, in a real (virtual) compositor
live = WORK / "live"
shutil.rmtree(live, ignore_errors=True)
run(ZRN, "new", "Live", "--lang", "c", "--id", "zrn-live", "--dir", str(live))
(live / "main.c").write_text(E.LIVE_C)
run(ZRN, "build", cwd=live)


def headless(style, script, **extra):
    env = dict(ENV, **extra)
    return run(ZRN, "run", "--headless", "--style", style, "--scale", "2",
               "--timeout", "30", "--script", script, cwd=live, env=env, check=False)


for style in STYLES:
    a = WORK / ("toast-%s.png" % style)
    a.unlink(missing_ok=True)
    headless(style, "wait 700; snap %s; quit" % a, LIVE_TOAST="1")
    b = WORK / ("busy-%s.png" % style)
    b.unlink(missing_ok=True)
    headless(style, "wait 900; snap %s; quit" % b, LIVE_BUSY="1")
    for name, src in (("toast", a), ("busy", b)):
        if src.exists():
            webp(src, IMG / ("%s-%s.webp" % (name, style)))
            report.append("live %-6s %-10s captured" % (name, style))
        else:
            report.append("live %-6s %-10s MISSING" % (name, style))

# frames of a real page change: tap Wi-Fi, wait, take one picture, quit, once
# per moment. A snapshot is slow, so one run gives one honest frame. Times are
# from the tap to the request for the picture, so a frame can run a little late.
for tag, y, moments in (("metro", 150, (40, 120, 200, 300, 380, 460, 560, 720)),
                       ("dotmatrix", 150, (40, 120, 200, 300, 380, 460, 560, 720))):
    style = tag
    ok = []
    for ms in moments:
        p = WORK / ("frame-%s-%d.png" % (tag, ms))
        p.unlink(missing_ok=True)
        headless(style, "wait 600; tap 180 %d; wait %d; snap %s; quit" % (y, ms, p))
        if p.exists():
            ok.append(Image.open(p).convert("RGB"))
    report.append("frames %-6s %d of %d, at %s ms" % (tag, len(ok), len(moments), moments))
    # a frame the compositor delayed past the end adds nothing: keep the moving ones and the end
    ok = [im for im in ok[:-1] if ImageChops.difference(im, ok[-1]).getbbox()] + ok[-1:]
    if ok:
        w, h = ok[0].size
        tw, th = 180, int(h * 180 / w)
        strip = Image.new("RGB", ((tw + 6) * len(ok) - 6, th), (128, 128, 128))
        for j, im in enumerate(ok):
            strip.paste(im.resize((tw, th), Image.LANCZOS), (j * (tw + 6), 0))
        strip.save(IMG / ("frames-%s.webp" % tag), "WEBP", quality=80, method=6)

(ROOT / "proof/report.txt").write_text("\n".join(report) + "\n")
print("\n".join(report))
sys.exit(1 if bad else 0)
