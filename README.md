# zrn-sdk-site

The source of https://sdk.ztos.online, the ztOS SDK wiki. Static files, served
by a Cloudflare Worker with no code, the same way as devices.ztos.online.
It documents zrnSDK v2 (zrnui, zrnapp, zrnkit) at the commit in `gen/pages.py`.

```
gen/elements.py   every pictured UI element, as C against zrnui
gen/render.py     compiles those, draws them with zrnui's software renderer
gen/pages.py      the words
gen/hello.c       examples/helloworld/hello.c at that commit
gen/build.py      writes public/*.html
public/           what is served
proof/            the generated programs and the render report
```

To rebuild against a clean checkout of zrn-sdk:

```
git -C /path/to/zrn-sdk worktree add --detach /path/to/sdk-clean <commit>
SDK=/path/to/sdk-clean WORK=/path/to/scratch SEGOE_FONT_DIR=/path/to/segoe-wp python3 gen/render.py
python3 gen/build.py
npx wrangler deploy
```

`render.py` needs cmake, ninja, a C23 compiler, freetype2, libpng, fontconfig
and Pillow. No window, compositor or GPU. Change `COMMIT` in `gen/pages.py`
when the SDK moves, copy `examples/helloworld/hello.c` to `gen/hello.c`, and
document only what is committed.

Text is licensed CC BY 4.0, code MIT.

`SEGOE_FONT_DIR` is a folder with the Segoe WP files of a Windows Phone 8.1
firmware (`SegoeWP.ttf`, `SegoeWP-Light.ttf`, `SegoeWP-Semilight.ttf`,
`SegoeWP-Semibold.ttf`, `SegoeWP-Bold.ttf`). render.py hands it to zrnui as
`ZRNUI_FONT_DIR` and writes the file loaded for each face to
`proof/report.txt`. Segoe WP is Microsoft's: never copy it into this
repository or `public/`. Without `SEGOE_FONT_DIR` the pictures use the bundled
Selawik (SIL OFL 1.1). The site's own text asks for "Segoe UI" / "Segoe WP"
only when the reader has them installed.

The current pictures and clips were drawn from the zrn-sdk working tree on top
of the pinned commit (app bar measured on a phone, Segoe WP lookup), not from a
clean checkout; `proof/report.txt` says so.

`gen/frost.c` draws the zrn-frosted-diffusion pictures on the Coming next page.
That effect is not in the pinned commit: build it against a zrn-sdk tree that
has it, with zrnui's GLES2 renderer (EGL surfaceless), and run
`frost OUT.png <mode 0-3> <light 0|1>`.
