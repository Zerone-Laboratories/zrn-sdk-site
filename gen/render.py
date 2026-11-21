#!/usr/bin/env python3
"""Compile every element of gen/elements.py and the clips of gen/anim.c
against zrnui (SDK v2), draw them with zrnui's GLES2 renderer offscreen
(Mesa, surfaceless EGL) in Dark and Light (Cobalt accent, the default), and
write public/img/<id>-{dark,light}.webp, public/clips/<name>-{dark,light}.
{webm,mp4} and proof/report.txt.

    SDK=/path/to/clean-checkout [SDK_NEXT=/path/to/tree-with-frost] \
    WORK=/path/to/scratch python3 gen/render.py

SDK must be a clean checkout of the commit in gen/pages.py (git worktree add
--detach <dir> <commit>). SDK_NEXT, when given, is a zrn-sdk tree that has
zrn-frosted-diffusion (not committed yet); it records the frost clip. Needs
cmake, ninja, a C23 compiler, freetype2, libpng, fontconfig, mesa (EGL,
GLES2), ffmpeg (libvpx-vp9, libx264) and Pillow. No window or compositor.
"""
import os, pathlib, subprocess, sys
from PIL import Image, ImageChops
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import elements as E

ROOT = pathlib.Path(__file__).resolve().parent.parent
SDK = pathlib.Path(os.environ["SDK"]).resolve()
WORK = pathlib.Path(os.environ["WORK"]).resolve()
IMG = ROOT / "public/img"
WORK.mkdir(parents=True, exist_ok=True)
IMG.mkdir(parents=True, exist_ok=True)
(ROOT / "proof").mkdir(exist_ok=True)
ENV = dict(os.environ)
for k in ("ZRNUI_RENDERER", "ZRNUI_ANIMATIONS", "ZRNUI_THEME", "ZRNUI_FONT_DIR", "ZRNUI_ANIMATION_SPEED", "ZRNUI_FONT_LOG"):
    ENV.pop(k, None)
# SEGOE_FONT_DIR: a folder with the Segoe WP files of a Windows Phone 8.1 firmware (SegoeWP.ttf, SegoeWP-Light.ttf, ...).
# They are Microsoft's: read from that folder at render time, never copied into this repository or public/.
# Without it the pictures are drawn in the bundled Selawik.
SEGOE = os.environ.get("SEGOE_FONT_DIR")
if SEGOE:
    ENV["ZRNUI_FONT_DIR"] = str(pathlib.Path(SEGOE).resolve())


def run(*a, cwd=None):
    r = subprocess.run([str(x) for x in a], cwd=cwd, env=ENV, capture_output=True, text=True)
    if r.returncode:
        sys.exit("FAILED %s\n%s\n%s" % (" ".join(map(str, a)), r.stdout, r.stderr))
    return "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "MESA" not in l and "pci id" not in l)


WRITEPNG = r'''#pragma once
#include <png.h>
#include <stdint.h>
#include <stdio.h>
static int write_png(const char* path, const uint8_t* px, int w, int h, int stride) {
	FILE* f = fopen(path, "wb");
	if (!f) return 0;
	png_structp p = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
	png_infop i = png_create_info_struct(p);
	if (setjmp(png_jmpbuf(p))) { fclose(f); return 0; }
	png_init_io(p, f);
	png_set_IHDR(p, i, w, h, 8, PNG_COLOR_TYPE_RGBA, PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);
	png_write_info(p, i);
	for (int y = 0; y < h; y++) png_write_row(p, (png_bytep)(px + (size_t)y * stride));
	png_write_end(p, NULL);
	png_destroy_write_struct(&p, &i);
	fclose(f);
	return 1;
}
'''

proj = WORK / "render"
proj.mkdir(exist_ok=True)
(proj / "writepng.h").write_text(WRITEPNG)
exes = []
for e in E.ELEMENTS:
    for theme in ("dark", "light"):
        name = "%s_%s" % (e["id"], theme)
        (proj / (name + ".c")).write_text(E.program_c(e, "Z_THEME_" + theme.upper()))
        exes.append(name)
(proj / "CMakeLists.txt").write_text("""cmake_minimum_required(VERSION 3.16)
project(sitepics C)
set(CMAKE_C_STANDARD 23)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(ZRNUI_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(ZRNUI_BUILD_SHARED OFF CACHE BOOL "" FORCE)
add_subdirectory(%s ${CMAKE_BINARY_DIR}/zrnui)
find_package(PNG REQUIRED)
foreach(n %s)
  add_executable(${n} ${n}.c)
  target_compile_options(${n} PRIVATE -Wall -Wextra -Werror)
  target_link_libraries(${n} PRIVATE zrnui::zrnui PNG::PNG)
endforeach()
add_executable(anim %s)
target_compile_options(anim PRIVATE -Wall -Wextra -Werror)
target_link_libraries(anim PRIVATE zrnui::zrnui)
""" % (SDK / "zrnui", " ".join(exes), ROOT / "gen/anim.c"))
print("build", flush=True)
run("cmake", "-S", proj, "-B", proj / "build", "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Release")
run("cmake", "--build", proj / "build")

commit = subprocess.run(["git", "-C", str(SDK), "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True).stdout.strip()
dirty = subprocess.run(["git", "-C", str(SDK), "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
report = ["zrn-sdk commit: %s%s" % (commit or "unknown", " (WORKING TREE NOT CLEAN)" if dirty else " (clean)"),
          "renderer: zrnui GLES2 (Z_RENDERER_GPU) offscreen through Mesa, 360 points wide at density 3, Cobalt accent",
          "pictures cropped to the content plus 19 points; built with -Wall -Wextra -Werror"]


def font_report(exe, *args):
    """The file zrnui loaded for each face (ZRNUI_FONT_LOG), as names only: no local paths in the report."""
    env = dict(ENV, ZRNUI_FONT_LOG="1")
    r = subprocess.run([str(exe), *map(str, args)], env=env, capture_output=True, text=True)
    faces = ("regular", "light", "semilight", "semibold", "bold", "symbol")
    out = []
    for l in r.stderr.splitlines():
        if l.startswith("fonts: face "):
            n, path = l[len("fonts: face "):].split(" -> ", 1)
            out.append("%s=%s" % (faces[int(n)], os.path.basename(path)))
    return "fonts: " + ", ".join(out)


def crop(im):
    """Down to the last row that is not the page background, plus 19 points."""
    bg = im.getpixel((im.width - 1, im.height - 1))
    diff = ImageChops.difference(im, Image.new("RGB", im.size, bg)).getbbox()
    if not diff:
        return im
    bottom = min(im.height, diff[3] + 19 * 3)
    return im.crop((0, 0, im.width, max(bottom, 120 * 3)))
if E.ELEMENTS:
    report.append(font_report(proj / "build" / ("%s_dark" % E.ELEMENTS[0]["id"]), WORK / "fontcheck.png"))
for e in ([] if os.environ.get("CLIPS_ONLY") else E.ELEMENTS):
    for theme in ("dark", "light"):
        name = "%s_%s" % (e["id"], theme)
        png = WORK / (name + ".png")
        log = run(proj / "build" / name, png).strip()
        im = Image.open(png).convert("RGB")
        if e.get("crop", True):
            im = crop(im)
        im.save(IMG / ("%s-%s.webp" % (e["id"], theme)), "WEBP", quality=88, method=6)
        report.append("%-8s %-5s %s" % (e["id"], theme, log))

# clips: real animations, a frame every 1/60 s read back from the GPU renderer
CLIPS = ROOT / "public/clips"
CLIPS.mkdir(parents=True, exist_ok=True)
W, H, FPS = 720, 1280, 60


def record(exe, scenario, theme):
    raw = WORK / ("%s-%s.rgba" % (scenario, theme))
    with open(raw, "wb") as out:
        r = subprocess.run([str(exe), scenario, theme], stdout=out, stderr=subprocess.PIPE, env=ENV, text=True)
    log = "\n".join(l for l in r.stderr.splitlines() if l.startswith("anim"))
    if r.returncode:
        sys.exit("FAILED anim %s %s\n%s" % (scenario, theme, r.stderr))
    base = CLIPS / ("%s-%s" % (scenario, theme))
    src = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", str(raw),
           "-vf", "scale=540:960:flags=lanczos,tpad=stop_mode=clone:stop_duration=0.6"]
    subprocess.run(src + ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "40", "-row-mt", "1", "-pix_fmt", "yuv420p", "-an", str(base) + ".webm"], check=True)
    subprocess.run(src + ["-c:v", "libx264", "-crf", "28", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(base) + ".mp4"], check=True)
    # a still of the first frame, for the poster
    Image.frombytes("RGBA", (W, H), open(raw, "rb").read(W * H * 4)).convert("RGB").resize((540, 960), Image.LANCZOS).save(str(base) + ".webp", "WEBP", quality=80)
    raw.unlink()
    sizes = "webm %d KB, mp4 %d KB" % ((base.with_suffix(".webm")).stat().st_size // 1024, (base.with_suffix(".mp4")).stat().st_size // 1024)
    report.append("clip %-10s %-5s %s; %s" % (scenario, theme, log, sizes))


ONLY = os.environ.get("ONLY", "").split(",") if os.environ.get("ONLY") else None
for scenario in ("turnstile", "pivot", "tilt", "appbar", "toggle", "theme", "hub"):
    if ONLY and scenario not in ONLY:
        continue
    for theme in ("dark", "light"):
        record(proj / "build/anim", scenario, theme)

NEXT = os.environ.get("SDK_NEXT")
if NEXT and (not ONLY or "frost" in ONLY):
    nproj = WORK / "render-next"
    nproj.mkdir(exist_ok=True)
    (nproj / "CMakeLists.txt").write_text("""cmake_minimum_required(VERSION 3.16)
project(sitenext C)
set(CMAKE_C_STANDARD 23)
set(ZRNUI_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(ZRNUI_BUILD_SHARED OFF CACHE BOOL "" FORCE)
add_subdirectory(%s ${CMAKE_BINARY_DIR}/zrnui)
add_executable(anim %s)
target_compile_definitions(anim PRIVATE WITH_FROST)
target_link_libraries(anim PRIVATE zrnui::zrnui)
""" % (pathlib.Path(NEXT).resolve() / "zrnui", ROOT / "gen/anim.c"))
    run("cmake", "-S", nproj, "-B", nproj / "build", "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Release")
    run("cmake", "--build", nproj / "build")
    ncommit = subprocess.run(["git", "-C", NEXT, "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True).stdout.strip()
    report.append("frost clip from %s at %s plus uncommitted changes" % (NEXT, ncommit))
    for theme in ("dark", "light"):
        record(nproj / "build/anim", "frost", theme)

if not os.environ.get("CLIPS_ONLY"):
    (ROOT / "proof/report.txt").write_text("\n".join(report) + "\n")
(ROOT / "proof/elements.c").write_text("\n\n".join("/* ---- %s ---- */\n%s" % (e["id"], E.program_c(e, "Z_THEME_DARK")) for e in E.ELEMENTS))
print("\n".join(report))
