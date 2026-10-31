# zrn-sdk-site

The source of https://sdk.ztos.online, the ztOS SDK wiki. Static files, served
by a Cloudflare Worker with no code, the same way as devices.ztos.online.

```
gen/elements.py   every UI element, as code in C, C++, Rust and Python
gen/render.py     compiles those, renders them with zrn, compares the languages
gen/pages.py      the words
gen/build.py      writes public/*.html
public/           what is served
proof/            the generated programs and the comparison report
```

To rebuild against a copy of zrn-sdk:

```
SDK=/path/to/zrn-sdk WORK=/path/to/scratch SDK_COMMIT=<commit> python3 gen/render.py
python3 gen/build.py
npx wrangler deploy
```

`render.py` needs Pillow, and the things `zrn doctor` asks for, including
kwin_wayland for the live pictures. Change `COMMIT` in `gen/pages.py` when the
SDK moves, and document only what is merged.

Text is licensed CC BY 4.0, code MIT. Inter and Selawik in the pictures are SIL
OFL 1.1.
