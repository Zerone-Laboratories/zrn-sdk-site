#!/usr/bin/env python3
"""The exploded-layers picture, clip and scroll stack for "How the shell draws" (public/shell.html).

    CAPTURES=/path/to/captures SDK=/path/to/zrn-sdk WORK=/path/to/scratch SEGOE_FONT_DIR=/path/to/segoe-wp \
        python3 gen/layers.py

CAPTURES holds screenshots of ztMETRO taken on the Galaxy S9 with grim (1440 x 2960, 4 pixels a
point): lock.png, start.png, shade.png, app.png (Settings), osk.png (Settings with the keyboard up)
and toast.png (Settings with a demo toast). They are cut into the shell's layers here, and the
personal parts are covered first (redact()). The captures themselves stay out of this repository:
only the cut, covered layers are written to public/. The call screen is not captured (that would
mean a real call): gen/layers.c draws it with zrnui, in the phone's red accent.

In the shell each Start tile is its own texture (and in the turnstile each moves on its own clock),
so layer 01 is built from the tiles cut out of the capture, each lying flat in its place.

Writes
    public/img/shell-layers-{dark,light}.{png,webp}         the picture, 1600 x 1000
    public/clips/shell-layers-{dark,light}.{webm,mp4,webp}  the clip, 1280 x 720, 6 s
    public/img/layers/*.webp, gen/layers.json                each layer and tile, for the scroll stack

Layer 01 is at the front and each later layer further back, as a frame is painted: the order is
render_frame's in ztOSMobile ztmetro/ztmetro.c, bottom first. Segoe WP is read from SEGOE_FONT_DIR
and never copied here.
"""
import json, math, os, pathlib, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
GEN = ROOT / "gen"
SDK = pathlib.Path(os.environ.get("SDK", ".")).resolve()
WORK = pathlib.Path(os.environ.get("WORK", ".")).resolve()
CAP = pathlib.Path(os.environ.get("CAPTURES", ".")).resolve()
SEGOE = os.environ.get("SEGOE_FONT_DIR")
IMG, CLIPS = ROOT / "public/img", ROOT / "public/clips"

# bottom first, as render_frame draws them: (key, name, the shell's own name, in the flat frame)
LAYERS = [
    ("start", "Start", "Cairo, a GL texture\nper tile", False),
    ("frost", "frost strips", "GLSL blur,\nhalf-size atlas", False),
    ("app", "app window", "client wl_surface\nas a GL texture", True),
    ("keyboard", "keyboard", "osk_layer:\nCairo to GL texture", True),
    ("status", "status bar", "status_layer: Cairo,\nuploaded on change", True),
    ("shade", "action centre", "shade_layer:\nCairo to GL texture", False),
    ("nav", "nav bar", "nav_layer: Cairo,\nuploaded on change", True),
    ("lock", "lock screen", "lock_layer:\nCairo to GL texture", False),
    ("call", "call", "ztphone wl_surface,\nblurred backdrop", False),
    ("volume", "volume, toasts", "volume_layer,\ntoast_layer: Cairo", True),
]
PX = 4                      # capture pixels a point
W_PT, H_PT = 360, 740       # the S9 as ztOS lays it out
STATUS, NAV = 28, 40        # STATUS_H, NAV_BAR_H
ASPECT = W_PT / H_PT

# the turnstile's tile timing in ztmetro.c (TILE_*): ms
TILE_LIFE_MS, TILE_ROW_MS, TILE_LEFT_MS = 186.0, 50.0, 51.0
TILE_SMALL_EARLY_MS, TILE_LAST_LATE_MS, TILE_JITTER_MS, TILE_JITTER_SPEED = 33.0, 70.0, 6.0, 0.05


def font(face, size):
    if SEGOE:
        p = pathlib.Path(SEGOE) / face
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.truetype("DejaVuSans.ttf", size)


# ---------------------------------------------------------------- the captures, covered

def cover(im, box, fill=(0, 0, 0), text=None, size=46, face="SegoeWP.ttf", ink=(153, 153, 153)):
    d = ImageDraw.Draw(im)
    d.rectangle(box, fill=fill)
    if text:
        d.text((box[0] + 6, box[1] + 2), text, font=font(face, size), fill=ink)


def redact(name, im):
    """Cover what is personal: network names, the carrier, the device's name, notification text."""
    if name in ("app", "osk", "toast"):
        # Settings: the Wi-Fi network's name and the carrier, under "Wi-Fi" and "cellular + SIM"
        cover(im, (50, 1378, 520, 1442), text="connected")
        if name != "osk":
            cover(im, (50, 1855, 620, 1918), text="4G, data off")
        else:
            cover(im, (50, 1855, 620, 1903))
    if name == "shade":
        cover(im, (40, 104, 240, 166))                      # the carrier
        cover(im, (180, 880, 1400, 1040))                   # the notification's source (the device's name)
        cover(im, (40, 1040, 1400, 1240))                   # its text
        ImageDraw.Draw(im).text((210, 905), "ztOS SDK", font=font("SegoeWP-Semilight.ttf", 64), fill=(255, 255, 255))
        ImageDraw.Draw(im).text((56, 1072), "Build finished", font=font("SegoeWP-Semibold.ttf", 46), fill=(255, 255, 255))
        ImageDraw.Draw(im).text((56, 1150), "hello.c compiled", font=font("SegoeWP.ttf", 46), fill=(153, 153, 153))
    return im


def captures():
    c = {}
    for n in ("lock", "start", "shade", "app", "osk", "toast"):
        c[n] = redact(n, Image.open(CAP / ("%s.png" % n)).convert("RGBA"))
    return c


def band(im, y0, y1):
    """Rows y0..y1 of a capture on a transparent screen."""
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im.crop((0, y0, im.width, y1)), (0, y0))
    return out


def deglyph(strip):
    """The bar strips of Start without the bars' own glyphs (those are the status and nav layers)."""
    a = np.asarray(strip.convert("RGB")).astype(np.float32)
    glyph = Image.fromarray(((a.max(axis=2) > 170) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
    soft = strip.filter(ImageFilter.GaussianBlur(18))
    return Image.composite(soft, strip, glyph)


def tiles(start):
    """Each tile of Start, from the capture: connected areas of colour on the black page, on a point grid."""
    a = np.asarray(start.convert("RGB")).astype(np.int32)
    g = a.reshape(H_PT, PX, W_PT, PX, 3).max(axis=(1, 3)).max(axis=2) > 24
    g[:STATUS + 2] = False
    g[H_PT - NAV:] = False
    seen = np.zeros_like(g)
    out = []
    for y in range(H_PT):
        for x in range(W_PT):
            if g[y, x] and not seen[y, x]:
                stack, pts = [(y, x)], []
                seen[y, x] = True
                while stack:
                    cy, cx = stack.pop()
                    pts.append((cy, cx))
                    for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= ny < H_PT and 0 <= nx < W_PT and g[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
                ys, xs = [p[0] for p in pts], [p[1] for p in pts]
                x0, y0, x1, y1 = min(xs), min(ys), max(xs) + 1, max(ys) + 1
                if (x1 - x0) * (y1 - y0) >= 900:   # a tile (the smallest is about 40 x 40 points)
                    out.append([x0, y0, x1, y1])
    return out


def tile_timing(rects):
    """Delay and speed of each tile, from the shell's turnstile constants."""
    rng = random.Random(7)
    rows = sorted({r[1] for r in rects})
    bottom = sorted({r[3] for r in rects})
    out = []
    for r in rects:
        from_bottom = sum(1 for b in bottom if b > r[3])     # rows below it
        delay = from_bottom * TILE_ROW_MS
        if r[2] - r[0] < 100:
            delay -= TILE_SMALL_EARLY_MS
        right = [q for q in rects if q is not r and abs(q[1] - r[1]) < 8 and q[0] > r[0]]
        if right:
            delay += TILE_LEFT_MS * 0.5                      # the left of two neighbours after the right
        if r[1] == rows[0] and r[0] == min(q[0] for q in rects if q[1] == rows[0]):
            delay += TILE_LAST_LATE_MS                       # the top-left tile goes last
        delay += rng.uniform(-TILE_JITTER_MS, TILE_JITTER_MS)
        speed = 1.0 + rng.uniform(-TILE_JITTER_SPEED, TILE_JITTER_SPEED)
        out.append(dict(delay=delay, speed=speed, lift=0.7 + rng.random() * 0.6, turn=0.7 + rng.random() * 0.6))
    lo = min(t["delay"] for t in out)
    span = max(t["delay"] for t in out) - lo + TILE_LIFE_MS
    for t in out:
        t["d"] = (t["delay"] - lo) / span                    # 0..1 of the stagger
        t["life"] = TILE_LIFE_MS / span / t["speed"]
    return out


def call_pane():
    """The call screen, drawn by gen/layers.c with zrnui (no call is placed to capture it)."""
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
    r = subprocess.run([proj / "build/layers", out, "dark"], env=env, capture_output=True, text=True)
    if r.returncode:
        sys.exit("layers.c failed\n" + r.stderr)
    b = np.asarray(Image.open(out / "call-dark-b.png").convert("RGB")).astype(np.float32)
    w = np.asarray(Image.open(out / "call-dark-w.png").convert("RGB")).astype(np.float32)
    a = np.clip(1.0 - (w - b).mean(axis=2) / 255.0, 0, 1)
    rgb = np.where(a[..., None] > 0.002, b / np.maximum(a[..., None], 0.002), 0)
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), "RGBA")
    return im.resize((W_PT * PX, H_PT * PX), Image.LANCZOS)


def cut():
    """The ten layers (and Start's tiles) from the covered captures."""
    c = captures()
    s, n = STATUS * PX, (H_PT - NAV) * PX
    start = c["start"]
    rects = tiles(start)
    base = band(start, s, n)
    d = ImageDraw.Draw(base)
    tile_ims = []
    for x0, y0, x1, y1 in rects:
        box = (x0 * PX, y0 * PX, x1 * PX, y1 * PX)
        tile_ims.append(start.crop(box))
        d.rectangle(box, fill=(0, 0, 0, 255))
    frost = Image.new("RGBA", start.size, (0, 0, 0, 0))
    frost.paste(deglyph(start.crop((0, 0, start.width, s + 10 * PX))), (0, 0))
    frost.paste(deglyph(start.crop((0, n - 10 * PX, start.width, start.height))), (0, n - 10 * PX))
    kb_top = 1904
    layers = {
        "start": base,
        "frost": frost,
        "app": band(c["app"], s, n),
        "keyboard": band(c["osk"], kb_top, n),
        "status": band(c["app"], 0, s),
        "shade": band(c["shade"], 0, n),
        "nav": band(c["app"], n, start.height),
        "lock": c["lock"],
        "call": call_pane(),
        "volume": band(c["toast"], 0, 232),
    }
    flat = c["osk"].copy()
    flat.alpha_composite(layers["volume"])
    return layers, rects, tile_ims, tile_timing(rects), flat


# ---------------------------------------------------------------- geometry

TURN, TILT = 58.0, 3.0       # degrees a pane turns about its upright axis, and leans back
STEP_X, STEP_Z, STEP_Y = 0.25, 0.30, -0.015   # per layer, in pane heights: right, back, up
EYE = 7.0                    # the eye's distance, in pane heights


def point(i, x, y, z, t):
    """A point of pane i (x right, y down, z toward the eye; in pane heights, about its centre) in the
    scene: the pane turned (TURN * t) and leant (TILT * t), then moved along the stack. Returns X, Y, Z
    with Z away from the eye."""
    th, ph = math.radians(TURN * t), math.radians(TILT * t)
    X = x * math.cos(th) + z * math.sin(th)
    Z = x * math.sin(th) - z * math.cos(th)
    Y = y * math.cos(ph) - Z * math.sin(ph)
    Z = y * math.sin(ph) + Z * math.cos(ph)
    return X + i * STEP_X * t, Y + i * STEP_Y * t, Z + i * STEP_Z * t


def screen(P):
    X, Y, Z = P
    s = EYE / (EYE + Z)
    return X * s, Y * s


def pane_corners(i, t):
    hw, hh = ASPECT / 2, 0.5
    return [screen(point(i, x, y, 0, t)) for x, y in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]


def tile_amount(tm, t):
    """How far a tile has turned out of its pane: always 0. The tiles sit flat on layer 01, in
    their places as captured (the picture shows the layers, not the turnstile)."""
    return 0.0


def tile_corners(rect, tm, t):
    """A tile of Start on layer 01: with tile_amount() at 0 it lies flat, where it was captured."""
    a = tile_amount(tm, t)
    turn = math.radians(26 * tm["turn"] * a)
    edge = -ASPECT / 2
    x0, y0, x1, y1 = (rect[0] / H_PT - ASPECT / 2, rect[1] / H_PT - 0.5, rect[2] / H_PT - ASPECT / 2, rect[3] / H_PT - 0.5)
    out = []
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        r = x - edge
        out.append(screen(point(0, edge + r * math.cos(turn), y, r * math.sin(turn), t)))
    return out


def fit(t, box, n=len(LAYERS)):
    """Scale and offset that put the stack at spread t inside box (x0, y0, x1, y1)."""
    pts = [p for i in range(n) for p in pane_corners(i, t)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    s = min((box[2] - box[0]) / (max(xs) - min(xs)), (box[3] - box[1]) / (max(ys) - min(ys)))
    ox = (box[0] + box[2]) / 2 - s * (max(xs) + min(xs)) / 2
    oy = (box[1] + box[3]) / 2 - s * (max(ys) + min(ys)) / 2
    return s, ox, oy


# ---------------------------------------------------------------- drawing

def palette(theme):
    dark = theme == "dark"
    return dict(bg=(0, 0, 0) if dark else (255, 255, 255), fg=(255, 255, 255) if dark else (0, 0, 0),
                sub=(160, 160, 160) if dark else (100, 100, 100), line=(90, 90, 90) if dark else (190, 190, 190),
                pane=(22, 22, 22, 235), edge=(255, 255, 255, 70) if dark else (0, 0, 0, 90),
                accent=(229, 20, 0))


def coeffs(dst, src):
    a = []
    for (x, y), (u, v) in zip(dst, src):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    return np.linalg.solve(np.array(a, float), np.array([c for p in src for c in p], float)).tolist()


def warp(canvas, im, quad, alpha=1.0):
    src = [(0, 0), (im.width, 0), (im.width, im.height), (0, im.height)]
    w = im.transform(canvas.size, Image.PERSPECTIVE, coeffs(quad, src), Image.BICUBIC)
    if alpha < 0.999:
        w.putalpha(w.getchannel("A").point(lambda v: round(v * alpha)))
    canvas.alpha_composite(w)


def plate(im, pal, px):
    """A layer on its pane: dark glass the size of the screen with a hairline edge."""
    w, h = round(px * ASPECT), round(px)
    p = Image.new("RGBA", (w, h), pal["pane"])
    p.alpha_composite(im.resize((w, h), Image.LANCZOS))
    ImageDraw.Draw(p).rectangle((0, 0, w - 1, h - 1), outline=pal["edge"], width=1)
    return p


def draw_stack(canvas, L, t, s, ox, oy, pal, alphas, px):
    """Back to front, so 01 is in front. Near t = 0 that order would put Start over the app, so the
    frame as seen (L["flat"]) lies over the stack and fades as the layers part."""
    plates = L["plates"]
    tr = lambda q: [(ox + s * x, oy + s * y) for x, y in q]
    for i in reversed(range(len(plates))):                  # the farthest first: 01 is painted last, in front
        if alphas[i] > 0.004:
            warp(canvas, plates[i], tr(pane_corners(i, t)), alphas[i])
        if i == 0:
            order = sorted(range(len(L["rects"])), key=lambda k: tile_amount(L["timing"][k], t))
            for k in order:
                warp(canvas, L["tiles"][k], tr(tile_corners(L["rects"][k], L["timing"][k], t)), alphas[0])
    if L.get("flat") is not None and t < 0.2:
        warp(canvas, L["flat"], tr(pane_corners(0, t)), 1.0 - t / 0.2)


def labels(canvas, t, s, ox, oy, pal, alpha=1.0, numbers_only=False, size=(21, 15)):
    d = ImageDraw.Draw(canvas)
    n = len(LAYERS)
    big, small, num = font("SegoeWP-Semilight.ttf", size[0]), font("SegoeWP.ttf", size[1]), font("SegoeWP-Semibold.ttf", size[1])
    col = lambda c: c[:3] + (round(255 * alpha),)
    corners = [[(ox + s * x, oy + s * y) for x, y in pane_corners(i, t)] for i in range(n)]
    gap = round(size[0] * 1.2)
    top = min(c[0][1] for c in corners) - gap
    bottom = max(c[3][1] for c in corners) + gap
    for i, (key, name, code, _) in enumerate(LAYERS):
        c = corners[i]
        below = i % 2 == 0
        a, b = (c[3], c[2]) if below else (c[0], c[1])
        ax, ay = a[0] + (b[0] - a[0]) * 0.2, a[1] + (b[1] - a[1]) * 0.2
        ly = bottom if below else top
        d.line((ax, ay + (5 if below else -5), ax, ly + (-4 if below else 4)), fill=col(pal["line"]), width=1)
        lh = round(size[0] * 1.15)
        code_lines = code.split("\n")
        sh = round(size[1] * 1.3)
        ty = ly if below else ly - lh - sh * len(code_lines)
        ind = round(size[1] * 1.8)
        tw = ind + max([d.textlength(name, font=big)] + [d.textlength(c, font=small) for c in code_lines])
        tx = min(ax, canvas.width - 24 - tw)
        d.text((tx, ty + round(size[0] * 0.2)), "%02d" % (i + 1), font=num, fill=col(pal["accent"]))
        d.text((tx + ind, ty - round(size[0] * 0.2)), name, font=big, fill=col(pal["fg"]))
        for j, c in enumerate(code_lines):
            d.text((tx + ind, ty + lh + j * sh), c, font=small, fill=col(pal["sub"]))


CAPTION = [
    ("Drawn on the GPU.", "render_frame draws the layers bottom to top with GLES2. App windows are the textures their buffers already are; the shell's own parts are textures repainted only when they change. An app at rest can instead go straight to a display plane (plane_pick)."),
    ("The shell moves the apps.", "Start's turnstile, an app swinging in and out, the switcher and the turn of the screen are drawn by the shell, so every app arrives and leaves the same way. In the turnstile each Start tile moves on its own clock."),
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


def prepare(layers, rects, tile_ims, timing, pal, px, flat=None):
    k = px / (H_PT * PX)
    return dict(flat=plate(flat, pal, px) if flat is not None else None, plates=[plate(layers[key], pal, px) for key, *_ in LAYERS], rects=rects, timing=timing,
                tiles=[im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS) for im in tile_ims])


def picture(layers, rects, tile_ims, timing, flat, theme):
    pal = palette(theme)
    W, H = 2000, 1250
    canvas = Image.new("RGBA", (W, H), pal["bg"] + (255,))
    d = ImageDraw.Draw(canvas)
    d.text((56, 40), "HOW ZTMETRO DRAWS A FRAME", font=font("SegoeWP-Semibold.ttf", 22), fill=pal["fg"])
    d.text((53, 66), "one compositor: ztMETRO (wlroots)", font=font("SegoeWP-Light.ttf", 54), fill=pal["fg"])
    # the base: the frame as seen, and the surface everything is drawn into
    fh = 700
    fw = round(fh * ASPECT)
    fx, fy = 56, 190
    canvas.alpha_composite(flat.resize((fw, fh), Image.LANCZOS), (fx, fy))
    d.rectangle((fx - 1, fy - 1, fx + fw, fy + fh), outline=pal["edge"][:3], width=1)
    t1, t2 = font("SegoeWP-Semilight.ttf", 30), font("SegoeWP.ttf", 19)
    d.text((fx, fy + fh + 14), "OpenGL ES 2 surface", font=t1, fill=pal["fg"])
    for j, line in enumerate(("EGL, wlroots GLES2 renderer, DRM", "Panfrost on the Mali-G72", "app at rest: plane_pick puts", "its dmabuf on a display plane")):
        d.text((fx, fy + fh + 56 + j * 25), line, font=t2, fill=pal["sub"])
    s, ox, oy = fit(1.0, (fx + fw + 40, 250, W - 200, 860))
    L = prepare(layers, rects, tile_ims, timing, pal, s * 1.05)
    draw_stack(canvas, L, 1.0, s, ox, oy, pal, [1.0] * len(LAYERS), s)
    labels(canvas, 1.0, s, ox, oy, pal, size=(25, 18))
    by = 1030
    x0 = fx + fw + 40
    d.line((x0, by, W - 64, by), fill=pal["line"], width=1)
    d.polygon([(W - 64, by - 6), (W - 52, by), (W - 64, by + 6)], fill=pal["line"])
    sm = font("SegoeWP.ttf", 19)
    d.text((x0, by + 10), "draw order: 01 first, in front", font=sm, fill=pal["sub"])
    d.text((W - 52 - d.textlength("10 last, at the back", font=sm), by + 10), "10 last, at the back", font=sm, fill=pal["sub"])
    hb, bf = font("SegoeWP-Semibold.ttf", 22), font("SegoeWP.ttf", 18)
    cw = (W - 112 - 2 * 48) / 3
    for i, (head, body) in enumerate(CAPTION):
        cx0 = 56 + i * (cw + 48)
        d.rectangle((cx0, 1066, cx0 + 32, 1069), fill=pal["accent"])
        d.text((cx0, 1080), head, font=hb, fill=pal["fg"])
        for j, line in enumerate(wrap(d, body, bf, cw)):
            d.text((cx0, 1112 + j * 25), line, font=bf, fill=pal["sub"])
    return canvas.convert("RGB")


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def clip(layers, rects, tile_ims, timing, flat, theme):
    """The stack, flat with 01 in front, comes apart layer by layer and tile by tile, holds, and folds back: 6 s, 60 frames a second."""
    pal = palette(theme)
    W, H, FPS, N = 1280, 720, 60, 360
    s1, ox1, oy1 = fit(1.0, (24, 96, 1130, 630))
    s0 = 560.0
    ox0, oy0 = W / 2, H / 2
    L = prepare(layers, rects, tile_ims, timing, pal, max(s0, s1) * 1.02)
    raw = WORK / ("shell-layers-%s.rgba" % theme)
    with open(raw, "wb") as out:
        for k in range(N):
            sec = k / FPS
            t = 0.0 if sec < 0.6 else ease((sec - 0.6) / 1.8) if sec < 2.4 else 1.0 if sec < 3.8 else 1.0 - ease((sec - 3.8) / 1.6) if sec < 5.4 else 0.0
            s, ox, oy = s0 + (s1 - s0) * t, ox0 + (ox1 - ox0) * t, oy0 + (oy1 - oy0) * t
            canvas = Image.new("RGBA", (W, H), pal["bg"] + (255,))
            # every layer is there from the first frame, stacked flat with 01 in front: they part, nothing fades
            draw_stack(canvas, L, t, s, ox, oy, pal, [1.0] * len(LAYERS), s)
            la = min(1.0, max(0.0, (t - 0.85) / 0.15))
            if la > 0:
                labels(canvas, t, s, ox, oy, pal, alpha=la, size=(16, 12))
            out.write(canvas.convert("RGB").tobytes())
            if k == 190:
                canvas.convert("RGB").save(WORK / ("shell-layers-%s-mid.png" % theme))
    base = CLIPS / ("shell-layers-%s" % theme)
    src = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", str(raw)]
    subprocess.run(src + ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "42", "-row-mt", "1", "-pix_fmt", "yuv420p", "-an", str(base) + ".webm"], check=True)
    subprocess.run(src + ["-c:v", "libx264", "-crf", "27", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(base) + ".mp4"], check=True)
    Image.open(WORK / ("shell-layers-%s-mid.png" % theme)).save(str(base) + ".webp", "WEBP", quality=82)
    raw.unlink()


def plates_out(layers, rects, tile_ims, timing, flat):
    """Each layer and each tile for the scroll stack, and where the tiles are (gen/layers.json)."""
    d = IMG / "layers"
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.webp"):
        f.unlink()
    flat.resize((540, 1110), Image.LANCZOS).save(d / "flat.webp", "WEBP", quality=86, method=6)
    for key, *_ in LAYERS:
        layers[key].resize((540, 1110), Image.LANCZOS).save(d / ("%s.webp" % key), "WEBP", quality=86, method=6)
    for k, im in enumerate(tile_ims):
        im.resize((max(1, im.width * 3 // 8), max(1, im.height * 3 // 8)), Image.LANCZOS).save(d / ("tile-%02d.webp" % k), "WEBP", quality=86, method=6)
    meta = dict(aspect=ASPECT, turn=TURN, tilt=TILT, step=[STEP_X, STEP_Y, STEP_Z], eye=EYE,
                tiles=[dict(rect=[r[0] / W_PT, r[1] / H_PT, r[2] / W_PT, r[3] / H_PT], **{k: round(v, 4) for k, v in tm.items()})
                       for r, tm in zip(rects, timing)])
    (GEN / "layers.json").write_text(json.dumps(meta, indent=1) + "\n")


def main():
    IMG.mkdir(parents=True, exist_ok=True)
    CLIPS.mkdir(parents=True, exist_ok=True)
    layers, rects, tile_ims, timing, flat = cut()
    print("tiles:", len(rects))
    only = os.environ.get("ONLY", "picture,clip,plates").split(",")
    if "plates" in only:
        plates_out(layers, rects, tile_ims, timing, flat)
    for theme in ("dark", "light"):
        if "picture" in only:
            pic = picture(layers, rects, tile_ims, timing, flat, theme)
            pic.save(IMG / ("shell-layers-%s.png" % theme), optimize=True)
            pic.save(IMG / ("shell-layers-%s.webp" % theme), "WEBP", quality=88, method=6)
        if "clip" in only:
            clip(layers, rects, tile_ims, timing, flat, theme)
        print("shell-layers", theme, "done")


if __name__ == "__main__":
    main()
