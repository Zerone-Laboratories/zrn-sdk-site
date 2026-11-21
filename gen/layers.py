#!/usr/bin/env python3
"""The exploded-layers picture and clip for "How the shell draws" (public/shell.html).

    SDK=/path/to/zrn-sdk WORK=/path/to/scratch SEGOE_FONT_DIR=/path/to/segoe-wp python3 gen/layers.py

Builds gen/layers.c against zrnui, which draws each ztMETRO layer with the GLES2
renderer offscreen (360 x 640 points at 3 device pixels a point, demo content
only), then lays the layers out in perspective here with Pillow and writes

    public/img/shell-layers-{dark,light}.{png,webp}    the picture, 1600 x 1000
    public/clips/shell-layers-{dark,light}.{webm,mp4,webp}   the clip, 1280 x 720, 5 s
    public/img/layers/<layer>-{dark,light}.webp        each layer alone, for the scroll-driven stack

The order of the layers is ztmetro's render_frame (ztOSMobile, ztmetro/ztmetro.c),
bottom first; the page says which lines. Segoe WP is read from SEGOE_FONT_DIR at
render time and never copied here. Needs cmake, ninja, a C23 compiler, mesa
(EGL, GLES2), libpng, ffmpeg (libvpx-vp9, libx264), numpy and Pillow.
"""
import math, os, pathlib, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
GEN = ROOT / "gen"
SDK = pathlib.Path(os.environ.get("SDK", ".")).resolve()
WORK = pathlib.Path(os.environ.get("WORK", ".")).resolve()
SEGOE = os.environ.get("SEGOE_FONT_DIR")
IMG, CLIPS = ROOT / "public/img", ROOT / "public/clips"

# bottom first, as render_frame draws them: (file, name, the shell's own name, shown in the flat frame)
LAYERS = [
    ("start", "Start, app list", "tiles, items", True),
    ("frost", "frost strips", "frost[0..1]", False),
    ("app", "app window", "wl_surface texture", True),
    ("keyboard", "keyboard", "osk_layer", True),
    ("status", "status bar", "status_layer", True),
    ("shade", "action centre", "shade_layer", False),
    ("nav", "nav bar", "nav_layer", True),
    ("lock", "lock screen", "lock_layer", False),
    ("call", "call", "ztphone over the lock", False),
    ("volume", "volume and toasts", "volume_layer, toast_layer", False),
]
PW, PH = 360, 640  # points


def build():
    proj = WORK / "layers"
    proj.mkdir(parents=True, exist_ok=True)
    src = (GEN / "render.py").read_text()
    (proj / "writepng.h").write_text(src.split("WRITEPNG = r'''", 1)[1].split("'''", 1)[0])
    (proj / "CMakeLists.txt").write_text("""cmake_minimum_required(VERSION 3.16)
project(sitelayers C)
set(CMAKE_C_STANDARD 23)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(ZRNUI_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(ZRNUI_BUILD_SHARED OFF CACHE BOOL "" FORCE)
add_subdirectory(%s ${CMAKE_BINARY_DIR}/zrnui)
find_package(PNG REQUIRED)
add_executable(layers %s)
target_include_directories(layers PRIVATE ${CMAKE_SOURCE_DIR})
target_compile_options(layers PRIVATE -Wall -Wextra -Werror)
target_link_libraries(layers PRIVATE zrnui::zrnui PNG::PNG)
""" % (SDK / "zrnui", GEN / "layers.c"))
    env = dict(os.environ)
    for k in ("ZRNUI_RENDERER", "ZRNUI_ANIMATIONS", "ZRNUI_THEME", "ZRNUI_FONT_DIR"):
        env.pop(k, None)
    if SEGOE:
        env["ZRNUI_FONT_DIR"] = str(pathlib.Path(SEGOE).resolve())
    subprocess.run(["cmake", "-S", proj, "-B", proj / "build", "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Release"], check=True, capture_output=True)
    subprocess.run(["cmake", "--build", proj / "build"], check=True, capture_output=True)
    out = proj / "out"
    out.mkdir(exist_ok=True)
    for t in ("dark", "light"):
        r = subprocess.run([proj / "build/layers", out, t], env=env, capture_output=True, text=True)
        if r.returncode:
            sys.exit("layers failed\n" + r.stderr)
        print("\n".join(l for l in r.stderr.splitlines() if l.startswith("layers")))
    return out


def matte(out, name, theme):
    """A layer as RGBA: its coverage from the difference between the black and the white pass."""
    if name == "app":
        full = Image.new("RGBA", (PW * 3, PH * 3), (0, 0, 0, 0))
        full.paste(Image.open(out / ("app-%s.png" % theme)).convert("RGBA"), (0, 28 * 3))
        return full
    b = np.asarray(Image.open(out / ("%s-%s-b.png" % (name, theme))).convert("RGB")).astype(np.float32)
    w = np.asarray(Image.open(out / ("%s-%s-w.png" % (name, theme))).convert("RGB")).astype(np.float32)
    a = np.clip(1.0 - (w - b).mean(axis=2) / 255.0, 0, 1)
    rgb = np.where(a[..., None] > 0.002, b / np.maximum(a[..., None], 0.002), 0)
    px = np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8)
    im = Image.fromarray(px, "RGBA")
    if name == "frost":
        # only the bars' strips: what the shell blurs under the status bar and the nav bar (STATUS_H, NAV_BAR_H + FROST_MARGIN)
        keep = Image.new("L", im.size, 0)
        d = ImageDraw.Draw(keep)
        d.rectangle((0, 0, im.width, (28 + 10) * 3), fill=255)
        d.rectangle((0, (640 - 40 - 10) * 3, im.width, im.height), fill=255)
        im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(keep))))
    return im


def font(face, size):
    if SEGOE:
        p = pathlib.Path(SEGOE) / face
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.truetype("DejaVuSans.ttf", size)


def palette(theme):
    dark = theme == "dark"
    return dict(bg=(0, 0, 0) if dark else (255, 255, 255), fg=(255, 255, 255) if dark else (0, 0, 0),
                sub=(154, 154, 154) if dark else (110, 110, 110), line=(70, 70, 70) if dark else (200, 200, 200),
                pane=(255, 255, 255, 18) if dark else (0, 0, 0, 14), edge=(255, 255, 255, 90) if dark else (0, 0, 0, 70),
                accent=(0x33, 0x7A, 0xFF) if dark else (0x00, 0x50, 0xEF))


def plate(im, pal, scale):
    """A layer on its pane: a faint glass the size of the screen with a hairline edge, then the layer."""
    w, h = round(PW * scale), round(PH * scale)
    p = Image.new("RGBA", (w, h), pal["pane"])
    p.alpha_composite(im.resize((w, h), Image.LANCZOS))
    ImageDraw.Draw(p).rectangle((0, 0, w - 1, h - 1), outline=pal["edge"], width=max(1, round(scale)))
    return p


def coeffs(dst, src):
    """Pillow PERSPECTIVE coefficients mapping output points dst to input points src."""
    a = []
    for (x, y), (u, v) in zip(dst, src):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    return np.linalg.solve(np.array(a, float), np.array([c for p in src for c in p], float)).tolist()


def project(i, n, t, cx, cy, size):
    """Screen corners of layer i of n at spread t (0 flat, 1 apart), the stack's middle at (cx, cy).

    Each pane turns about its vertical axis by up to 60 degrees and a little about its
    horizontal one; the panes move apart along the stack, bottom layer at the front left."""
    th, ph = math.radians(60 * t), math.radians(-6 * t)
    gap = 104 * t * size / 400
    f = 2200.0
    hw, hh = size * 0.5625 / 2, size / 2
    k = i - (n - 1) / 2
    out = []
    for x, y in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)):
        # turn about y, then about x
        X, Z = x * math.cos(th), x * math.sin(th)
        Y, Z = y * math.cos(ph) - Z * math.sin(ph), y * math.sin(ph) + Z * math.cos(ph)
        # along the stack: to the right and back, a little up
        X += k * gap * 1.0
        Z += k * gap * 0.3
        Y -= k * gap * 0.08
        s = f / (f + Z)
        out.append((cx + X * s, cy + Y * s))
    return out


def stack(canvas, plates, t, cx, cy, size, alphas):
    n = len(plates)
    # farthest first: the top layers are at the back
    for i in reversed(range(n)):
        if alphas[i] <= 0.004:
            continue
        p = plates[i]
        dst = project(i, n, t, cx, cy, size)
        src = [(0, 0), (p.width, 0), (p.width, p.height), (0, p.height)]
        warped = p.transform(canvas.size, Image.PERSPECTIVE, coeffs(dst, src), Image.BICUBIC)
        if alphas[i] < 0.999:
            warped.putalpha(warped.getchannel("A").point(lambda v, a=alphas[i]: round(v * a)))
        canvas.alpha_composite(warped)


def labels(canvas, t, cx, cy, size, pal, alpha=1.0):
    """Each layer's name and the shell's own name, alternately above and below the stack, on a hairline."""
    d = ImageDraw.Draw(canvas)
    n = len(LAYERS)
    big, small, num = font("SegoeWP-Semilight.ttf", 21), font("SegoeWP.ttf", 15), font("SegoeWP-Semibold.ttf", 15)
    a = round(255 * alpha)
    corners = [project(i, n, t, cx, cy, size) for i in range(n)]
    top_row = min(c[0][1] for c in corners) - 26
    bottom_row = max(c[3][1] for c in corners) + 26

    def col(c):
        return c[:3] + (a,)
    for i, (key, name, code, _) in enumerate(LAYERS):
        c = corners[i]
        below = i % 2 == 0
        ax, ay = (c[3] if below else c[0])
        ax += (c[2][0] - c[3][0]) * 0.18 if below else (c[1][0] - c[0][0]) * 0.18
        ay = (c[3][1] + (c[2][1] - c[3][1]) * 0.18) if below else (c[0][1] + (c[1][1] - c[0][1]) * 0.18)
        ly = bottom_row if below else top_row
        d.line((ax, ay + (6 if below else -6), ax, ly + (-4 if below else 4)), fill=col(pal["line"]), width=1)
        d.ellipse((ax - 2.5, ay - 2.5 + (6 if below else -6), ax + 2.5, ay + 2.5 + (6 if below else -6)), fill=col(pal["accent"]))
        ty = ly if below else ly - 44
        tw = 24 + max(d.textlength(name, font=big), d.textlength(code, font=small))
        tx = min(ax, canvas.width - 28 - tw)
        d.text((tx, ty), "%02d" % (i + 1), font=num, fill=col(pal["accent"]))
        d.text((tx + 24, ty - 5), name, font=big, fill=col(pal["fg"]))
        d.text((tx + 24, ty + 21), code, font=small, fill=col(pal["sub"]))


def flat(plates_full, theme):
    """The frame as it is seen: the layers that are in it, composited in order."""
    pal = palette(theme)
    im = Image.new("RGBA", plates_full[0].size, pal["bg"] + (255,))
    for (key, _, _, shown), p in zip(LAYERS, plates_full):
        if shown:
            im.alpha_composite(p)
    return im


CAPTION = [
    ("Drawn on the GPU.", "render_frame draws the layers bottom to top with GLES2. App windows are the textures their buffers already are; the shell's own parts are textures repainted only when they change. What the lock screen or an app at rest covers is not drawn."),
    ("The shell moves the apps.", "Start's turnstile, an app swinging in and out, the switcher and the turn of the screen are drawn by the shell, so every app arrives and leaves the same way."),
    ("A fixed order.", "The nav bar, the lock screen, a call and the volume are drawn after the apps, so nothing an app draws can cover them."),
]


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        nxt = (cur + " " + w).strip()
        if d.textlength(nxt, font=f) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = nxt
    return lines + [cur]


def picture(layers, theme):
    pal = palette(theme)
    W, H = 1600, 1000
    canvas = Image.new("RGBA", (W, H), pal["bg"] + (255,))
    d = ImageDraw.Draw(canvas)
    d.text((64, 44), "HOW ZTMETRO DRAWS A FRAME", font=font("SegoeWP-Semibold.ttf", 17), fill=pal["fg"])
    d.text((61, 66), "one screen, ten layers", font=font("SegoeWP-Light.ttf", 46), fill=pal["fg"])
    # the frame as seen, at the left
    size = 420
    fw, fh = round(size * 0.5625), size
    fx, fy = 64, 214
    shown = flat(layers, theme).resize((fw, fh), Image.LANCZOS)
    canvas.alpha_composite(shown, (fx, fy))
    d.rectangle((fx - 1, fy - 1, fx + fw, fy + fh), outline=pal["edge"][:3], width=1)
    d.text((fx, fy + fh + 14), "the frame you see", font=font("SegoeWP-Semilight.ttf", 19), fill=pal["fg"])
    d.text((fx, fy + fh + 38), "an app, its keyboard and the bars", font=font("SegoeWP.ttf", 13), fill=pal["sub"])
    # an arrow into the stack
    ay = fy + fh / 2
    d.line((fx + fw + 22, ay, fx + fw + 70, ay), fill=pal["line"], width=2)
    d.polygon([(fx + fw + 70, ay - 6), (fx + fw + 80, ay), (fx + fw + 70, ay + 6)], fill=pal["line"])
    # the layers apart
    plates = [plate(l, pal, 1.2) for l in layers]
    cx, cy = 1010, fy + fh / 2 + 4
    stack(canvas, plates, 1.0, cx, cy, size, [1.0] * len(plates))
    labels(canvas, 1.0, cx, cy, size, pal)
    # drawn first, drawn last
    by = 802
    d.line((430, by, 1536, by), fill=pal["line"], width=1)
    d.polygon([(1536, by - 5), (1546, by), (1536, by + 5)], fill=pal["line"])
    sm = font("SegoeWP.ttf", 15)
    d.text((430, by + 8), "drawn first (bottom)", font=sm, fill=pal["sub"])
    d.text((1546 - d.textlength("drawn last (top)", font=sm), by + 8), "drawn last (top)", font=sm, fill=pal["sub"])
    # the caption
    x, cw = 64, 470
    hb, bf = font("SegoeWP-Semibold.ttf", 19), font("SegoeWP.ttf", 16)
    for i, (head, body) in enumerate(CAPTION):
        cx0 = x + i * (cw + 36)
        d.rectangle((cx0, 852, cx0 + 28, 855), fill=pal["accent"])
        d.text((cx0, 866), head, font=hb, fill=pal["fg"])
        for j, line in enumerate(wrap(d, body, bf, cw)):
            d.text((cx0, 894 + j * 22), line, font=bf, fill=pal["sub"])
    return canvas.convert("RGB")


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x) if x < 1 else 1.0


def clip(layers, theme, work):
    """The flat frame fans apart into its layers, holds, and folds back: 5 s at 60 frames a second."""
    pal = palette(theme)
    W, H, FPS, N = 1280, 720, 60, 300
    plates = [plate(l, pal, 0.9) for l in layers]
    raw = work / ("shell-layers-%s.rgba" % theme)
    with open(raw, "wb") as out:
        for k in range(N):
            s = k / FPS
            if s < 0.6:
                t = 0.0
            elif s < 2.1:
                t = ease((s - 0.6) / 1.5)
            elif s < 3.4:
                t = 1.0
            elif s < 4.6:
                t = 1.0 - ease((s - 3.4) / 1.2)
            else:
                t = 0.0
            size = 520 - 120 * t
            cx, cy = W / 2 + 40 * t, H / 2 - 10 * t
            canvas = Image.new("RGBA", (W, H), pal["bg"] + (255,))
            alphas = [1.0 if shown else min(1.0, t * 1.6) for (_, _, _, shown) in LAYERS]
            stack(canvas, plates, t, cx, cy, size, alphas)
            la = min(1.0, max(0.0, (t - 0.82) / 0.18))
            if la > 0:
                labels(canvas, t, cx, cy, size, pal, alpha=la)
            out.write(canvas.convert("RGB").tobytes())
            if k == 150:
                canvas.convert("RGB").save(work / ("shell-layers-%s-mid.png" % theme))
    base = CLIPS / ("shell-layers-%s" % theme)
    src = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", str(raw)]
    subprocess.run(src + ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "38", "-row-mt", "1", "-pix_fmt", "yuv420p", "-an", str(base) + ".webm"], check=True)
    subprocess.run(src + ["-c:v", "libx264", "-crf", "24", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(base) + ".mp4"], check=True)
    Image.open(work / ("shell-layers-%s-mid.png" % theme)).save(str(base) + ".webp", "WEBP", quality=82)
    raw.unlink()


def main():
    out = build()
    IMG.mkdir(parents=True, exist_ok=True)
    CLIPS.mkdir(parents=True, exist_ok=True)
    only = os.environ.get("ONLY", "picture,clip,plates").split(",")
    (IMG / "layers").mkdir(exist_ok=True)
    for theme in ("dark", "light"):
        layers = [matte(out, key, theme) for key, *_ in LAYERS]
        if "picture" in only:
            pic = picture(layers, theme)
            pic.save(IMG / ("shell-layers-%s.png" % theme), optimize=True)
            pic.save(IMG / ("shell-layers-%s.webp" % theme), "WEBP", quality=88, method=6)
        if "plates" in only:
            # each layer alone, for the page's scroll-driven stack (the pane's glass and edge are CSS)
            for (key, *_), im in zip(LAYERS, layers):
                im.resize((540, 960), Image.LANCZOS).save(IMG / "layers" / ("%s-%s.webp" % (key, theme)), "WEBP", quality=86, method=6)
        if "clip" in only:
            clip(layers, theme, WORK)
        print("shell-layers", theme, "done")


if __name__ == "__main__":
    main()
