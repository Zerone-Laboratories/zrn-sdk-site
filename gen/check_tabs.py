#!/usr/bin/env python3
"""Compiles every language-tab snippet on the site that is not in elements.py."""
import os, pathlib, shutil, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import pages as P
SDK = pathlib.Path(os.environ["SDK"]).resolve(); WORK = pathlib.Path(os.environ["WORK"]).resolve() / "tabs"
ENV = dict(os.environ, HOME=str(WORK / "home"), TMPDIR=str(WORK))
shutil.rmtree(WORK, ignore_errors=True); (WORK / "home").mkdir(parents=True)
ZRN = str(SDK / "tools/zrn")
def indent(s, n): return "\n".join(" " * n + l for l in s.splitlines())
def wrap(lang, name, code):
    if name == "hello": return code
    if lang == "c":
        helpers = "\n".join(l for l in code.splitlines() if l.startswith("static"))
        body = "\n".join(l for l in code.splitlines() if not l.startswith("static"))
        return ('#include <stddef.h>\n#include <zrnui.h>\nstatic void ready(int fd, void *d) {}\n%s\nint main(void) { int fd = 0; (void)fd;\n'
                'zui_app *app = zui_app_new("zrn-tab", "T");\n%s\n%s\n}\n') % (helpers, body, "" if "return" in body else 'return zui_run(app, zui_page(app, "x"));')
    if lang == "cpp":
        return ('#include <zrnui.hpp>\nstatic void ready(int, void *) {}\nint main() { int fd = 0; (void)fd; (void)ready;\nzrn::ui::App app("zrn-tab", "T");\n%s\n%s\n}\n'
                % (code, "" if "return" in code else 'return app.run(app.page("x"));'))
    if lang == "rs":
        return 'fn main() {\nlet app = zrnui::App::new("zrn-tab", "T");\n%s\n%s\n}\n' % (code, "" if "exit" in code else 'std::process::exit(app.run(app.page("x")));')
    pre = 'import zrnui\nfd = 0\ndef read_it(fd): pass\n'
    if "zrnui.App(" not in code: pre += 'app = zrnui.App("zrn-tab", "T")\n'
    return pre + code + ('' if "app.run" in code else '\napp.run(app.page("x"))') + "\n"
MAIN = {"c": ("c", "main.c"), "cpp": ("cpp", "main.cpp"), "rs": ("rust", "src/main.rs"), "py": ("python", "main.py")}
bad = 0
for name, tabs in P.TABS.items():
    for k, code in tabs.items():
        lang, main = MAIN[k]; d = WORK / (name + "-" + k)
        subprocess.run([ZRN, "new", "T", "--lang", lang, "--id", "zrn-t", "--dir", str(d)], env=ENV, capture_output=True, check=True)
        (d / main).write_text(wrap(k, name, code))
        r = subprocess.run([ZRN, "build"], cwd=d, env=ENV, capture_output=True, text=True)
        print(name, k, "ok" if r.returncode == 0 else "FAIL")
        if r.returncode: bad += 1; print(r.stdout[-1500:], r.stderr[-1500:])
sys.exit(1 if bad else 0)
