"""The wiki's words. Everything here was checked against zrn-sdk at COMMIT."""
COMMIT = "ea16771"

SHELL = """<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#121212">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ztOS SDK">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://ztos.online/og.jpg">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<div class="layout">
<aside class="sidebar">
<a class="wordmark" href="/">ztOS <span>SDK</span></a>
<nav class="desk" aria-label="Pages"><ul>{links}</ul></nav>
<details class="menu"><summary>Pages</summary><nav aria-label="Pages"><ul>{links}</ul></nav></details>
<div class="side-foot"><a href="https://ztos.online">ztos.online</a><a href="https://github.com/Zerone-Laboratories/zrn-sdk">zrn-sdk on GitHub</a><a href="https://github.com/Zerone-Laboratories/zrn-sdk-site">This site's source</a></div>
</aside>
<main>
{body}
<p class="foot">Checked against zrn-sdk commit <code>{commit}</code>. Pictures are real renders of code that compiled. <a href="https://github.com/Zerone-Laboratories/zrn-sdk-site">Source and proof</a>.</p>
</main>
</div>
<script src="/assets/site.js"></script>
<script src="/assets/motion.js"></script>
</body>
</html>
"""

TABS = {
    "hello": {
        "c": '''#include <zrnui.h>

static zui_node *status;

static void tapped(zui_node *button, void *data) {
	zui_set_text(status, "Tapped");
	zui_toast(zui_node_app(button), "Hello from Notes");
}

int main(void) {
	zui_app *app = zui_app_new("io.github.you.notes", "Notes");
	zui_node *page = zui_page(app, "Notes");
	zui_node *card = zui_section(page, "Status");
	status = zui_heading(card, "Not tapped yet");
	zui_button(page, "Tap me", tapped, NULL);
	return zui_run(app, page);
}''',
        "cpp": '''#include <zrnui.hpp>

int main() {
	zrn::ui::App app("io.github.you.notes", "Notes");
	auto page = app.page("Notes");
	auto status = page.section("Status").heading("Not tapped yet");
	page.button("Tap me", [&]() {
		status.set_text("Tapped");
		app.toast("Hello from Notes");
	});
	return app.run(page);
}''',
        "rs": '''fn main() {
    let app = zrnui::App::new("io.github.you.notes", "Notes");
    let page = app.page("Notes");
    let status = page.section("Status").heading("Not tapped yet");
    let app_ref = &app;
    page.button("Tap me").on_click(move || {
        status.set_text("Tapped");
        app_ref.toast("Hello from Notes");
    });
    std::process::exit(app.run(page));
}''',
        "py": '''import zrnui

app = zrnui.App("io.github.you.notes", "Notes")
page = app.page("Notes")
status = page.section("Status").heading("Not tapped yet")


def tapped():
    status.set_text("Tapped")
    app.toast("Hello from Notes")


page.button("Tap me", tapped)
app.run(page)''',
    },
    "nav": {
        "c": '''static void open_wifi(zui_node *row, void *wifi_page) { zui_push(wifi_page); }

zui_node *wifi = zui_page(app, "Wi-Fi");
zui_node *page = zui_page(app, "Settings");
zui_item(zui_card(page), "Wi-Fi", NULL, open_wifi, wifi);
return zui_run(app, page);''',
        "cpp": '''auto wifi = app.page("Wi-Fi");
auto page = app.page("Settings");
page.card().item("Wi-Fi", "", [&] { wifi.push(); });
return app.run(page);''',
        "rs": '''let wifi = app.page("Wi-Fi");
let page = app.page("Settings");
page.card().item("Wi-Fi", None).on_click(move || wifi.push());
std::process::exit(app.run(page));''',
        "py": '''wifi = app.page("Wi-Fi")
page = app.page("Settings")
page.card().item("Wi-Fi", on_click=wifi.push)
app.run(page)''',
    },
    "loop": {
        "c": '''static void tick(void *data) { zui_toast(data, "A second passed"); }
static void done(void *data) { zui_busy(data, false); zui_toast(data, "Done"); }

int id = zui_timer(app, 1000, true, tick, app);   /* every second */
zui_timer_cancel(app, id);
zui_busy(app, true);
zui_post(app, done, app);                         /* from any thread */
zui_watch_fd(app, fd, ready, NULL);               /* ready(fd, data) when readable */
zui_haptic("tap");                                /* tick, tap, click, heavy */''',
        "cpp": '''int id = app.timer(1000, true, [&] { app.toast("A second passed"); });
app.cancel_timer(id);
app.busy(true);
app.post([&] { app.busy(false); app.toast("Done"); });   // from any thread
zui_watch_fd(app.get(), fd, ready, nullptr);             // C API
zui_haptic("tap");''',
        "rs": '''let id = app.timer(1000, true, move || println!("a second passed"));
app.cancel_timer(id);
app.busy(true);
let poster = app.poster();                 // Send + Clone, for other threads
std::thread::spawn(move || { poster.post(|| println!("on the UI thread")); });''',
        "py": '''tid = app.timer(1000, lambda: app.toast("A second passed"), repeat=True)
app.cancel(tid)
app.busy(True)
app.post(lambda: app.busy(False))          # from any thread
app.watch(fd, lambda fd: read_it(fd))      # fn(fd) when readable''',
    },
    "accent": {
        "c": '''zui_app_set_accent(app, 0x0050ef);   /* DotMatrix ignores this; the style rules say leave it */''',
        "cpp": '''app.set_accent(0x0050ef);''',
        "rs": '''app.set_accent(0x0050ef);''',
        "py": '''app = zrnui.App("io.github.you.notes", "Notes", accent=0x0050ef)''',
    },
}

def demo(name, title=None):
    return '<div class="demo" data-demo="%s">%s</div>' % (name, "<h4>%s</h4>" % title if title else "")

def curve(spec, label):
    return '<figure><svg viewBox="0 0 100 100" data-curve="%s" role="img" aria-label="%s" preserveAspectRatio="none"></svg><figcaption>%s</figcaption></figure>' % (spec, label, label)

CATALOGUE_ROWS = [
    ("turnstile-in", "Y", "-80 to 0", "left edge", "no", "350", "Log 60"),
    ("turnstile-out", "Y", "0 to 50", "left edge", "1 to 0", "128", "Exp 60"),
    ("swivel-in", "X", "-45 to 0", "middle", "no (shown from its start)", "300", "Log 200"),
    ("swivel-out", "X", "0 to 60", "middle", "no (hidden at its end)", "200", "Exp 150"),
    ("continuum-hide", "X", "0 to 80", "top edge", "1 to 0, drops 120 pt", "120", "Exp 60"),
    ("continuum-show", "X", "-50 to 0", "top edge", "0 to 1, scale 1.5 to 1, from -60 pt", "350", "Log 60"),
    ("readerboard-in", "X", "-45 to 0", "top edge", "0 to 1", "166", "Log 60"),
    ("readerboard-out", "X", "0 to 90", "top edge", "1 to 0", "166", "Exp 60"),
    ("slide-up-fade-in", "none", "none", "none", "0 to 1, up from 24 pt", "240", "Log 150"),
    ("rotate-90", "Z", "90 to 0", "middle", "no", "167", "SCurve 7.5"),
    ("fade-in", "none", "none", "none", "0 to 1", "350", "Log 150"),
    ("fade-out", "none", "none", "none", "1 to 0", "150", "Exp 150"),
    ("tile-flip-notify", "X", "-180, 35, -6, 0", "middle", "no", "520", "Log 10, SCurve 10, linear"),
]

ANIMATIONS = """
<h1>Animations</h1>
<p class="lead">Every animation here runs from the same formula and the same numbers as the C code, and each one names the file those numbers come from.</p>

<div class="note"><p><b>A zrnui app does not call any of these.</b> libzrnui has <b>no animation API</b> at commit <code>""" + COMMIT + """</code>: page changes, presses, switches and toasts animate by themselves, and the style decides how. <b>Swivel, fade and the other named transitions are not in libzrnui.</b> They exist in ZrnMetroCore (ztOS's own apps) and in the older Python SDK's <code>animate()</code>.</p></div>

<div class="table-wrap"><table>
<tr><th>Where you are</th><th>What you get</th><th>How</th></tr>
<tr><td>zrn-sdk, libzrnui</td><td>Page change, press, switch, pivot, toast, busy, progress, fling</td><td>Automatic. No call, no way to change the numbers</td></tr>
<tr><td>Older Python SDK, <code>ztos</code></td><td>Its own turnstile and tilt, plus 13 named transitions</td><td><code>ztos.animate(widget, "swivel-in")</code>. Some values differ: see <a href="#old">below</a></td></tr>
<tr><td>ZrnMetroCore (<code>ztmetro/core</code>)</td><td>13 named transitions, the Swivel board, <code>zmc_turn</code></td><td><code>zmc_transition()</code>, <code>zmc_board_open()</code>. For apps in the ztOS tree, not an SDK</td></tr>
</table></div>

<h2 id="how">Using these demos</h2>
<p><b>Replay</b> runs it again. The speed button cycles 1x, 0.25x and 0.1x. The slider shows any single millisecond. Demos start when you scroll to them. If your system asks for reduced motion, nothing starts by itself and each demo rests on its last frame, so you can step through with the slider.</p>

<div class="gap"><b>Where the web version only approximates</b>
<ul>
<li><b>Same:</b> durations, staggers, angles, pivots, opacity, easing formulas and the eye distance (a 34 degree field of view on a 740 pt tall screen, <code>gfx.c</code>, <code>zrnmetrogpu.c</code>). A browser's <code>perspective</code> is the same divide the shader does.</li>
<li><b>Different:</b> the fonts and row layouts are plain CSS stand-ins, not Segoe UI through the SDF renderer. The real look is in the <a href="/elements">renders</a>.</li>
<li><b>Different:</b> the demos draw in the Metro look only. DotMatrix runs the same motion through its lattice, as the real frames show.</li>
<li><b>Different:</b> phones here run at your browser's frame rate, not the S9's, and the C code samples its clock once per compositor frame.</li>
<li><b>Different:</b> libzrnui rotates each row's quads, while these demos rotate a whole row box. Each named-transition demo shows one rectangle in a 300 pt tall stage, while the eye distance stays that of a 740 pt screen.</li>
<li><b>Not compared to the phone:</b> these were compared by eye with frames from the laptop's virtual compositor, not with the S9's display.</li>
</ul></div>

<h2 id="curves">The curves</h2>
<p>Progress over time for each easing. <b>libzrnui</b> has three, in <code>libzrnui/src/core.c</code>: <code>zui_ease_out</code> is <code>1 - (1-t)^3</code>, <code>zui_ease_in</code> is <code>t^3</code>, and <code>zui_ease_emph</code> is a cubic Bezier (0.2, 0.8, 0.2, 1). <b>ZrnMetroCore</b> rebuilds the firmware's named curves in <code>zt_shape</code>, with <code>k = weight / 30</code>: Exp is <code>(e^(k t) - 1) / (e^k - 1)</code> and Log is <code>1 - (e^(k (1-t)) - 1) / (e^k - 1)</code>. The firmware stores names and weights. The formula itself is a reconstruction, as the core's own comment says.</p>
<div class="curves">""" + curve("out", "zui_ease_out") + curve("in", "zui_ease_in") + curve("emph", "zui_ease_emph") + curve("l:200", "Log 200 (swivel in)") + curve("e:150", "Exp 150 (swivel out)") + curve("l:60", "Log 60") + curve("e:60", "Exp 60") + curve("s:7.5", "SCurve 7.5") + """</div>

<h2 id="page-metro">Page change: the turnstile <span class="tag">libzrnui</span></h2>
<p>Automatic on <code>zui_push</code> and <code>zui_back</code>, in both styles, with the same numbers. Runs <b>720 ms</b> in all. Rows leave one at a time, 28 ms apart, each over 128 ms, turning 50 degrees about the left edge on <code>zui_ease_in</code> toward the viewer, with opacity <code>1 - u^2</code>. New rows start at 330 ms, also 28 ms apart, each over 180 ms from 80 degrees behind the screen, on <code>zui_ease_out</code>. Going back, both run bottom up and the old rows turn the other way.</p>
<p>Source: <code>page_xf</code>, <code>OUT_MS</code>, <code>IN_MS</code>, <code>STAGGER</code>, <code>GAP_AT</code> in <code>libzrnui/src/style-metro.c</code>. The comment above them says 33 ms apart; the code that runs says 28.</p>
<div class="demos">""" + demo("metro-forward", "Forward") + demo("metro-back", "Back") + """</div>
<p>Real frames, from <code>zrn run --headless</code> in a virtual compositor, one run per picture. Frames the compositor delayed past the end are dropped, and the times are not exact: this shows the shape, while the numbers above come from the code. Metro, then DotMatrix.</p>
<div class="strip" tabindex="0"><img src="/img/frames-metro.webp" alt="Real frames of the page change in Metro" loading="lazy"></div>
<div class="strip" tabindex="0"><img src="/img/frames-dotmatrix.webp" alt="Real frames of the page change in DotMatrix" loading="lazy"></div>

<h2 id="page-core">Page change: ZrnMetroCore turnstile <span class="tag dashed">ztOS apps only</span></h2>
<p>The built-in apps' own version, for comparison: rows 33 ms apart, 128 ms out on <code>t^2</code>, a 120 ms black gap, 180 ms in on <code>1 - (1-t)^3</code>. The total depends on the row count. <code>zmc_turn</code> plays this on one page when its content changes. Source: <code>ROW_OUT_MS</code>, <code>ROW_IN_MS</code>, <code>ROW_STAGGER_MS</code>, <code>GAP_MS</code> and <code>TURN_OUT_DEG</code> in <code>ztmetro/core/zrnmetrocore.c</code>. Simplified here: the real one also holds the tapped row until last, and an app's first page arrives by a different curve (<code>zmr_entrance</code>, 28 ms stagger, 190 ms rows, 200 ms title), which is not shown.</p>
<div class="demos">""" + demo("core-forward", "Forward") + demo("core-back", "Back") + """</div>

<h2 id="swivel">Swivel: the domino board <span class="tag dashed">ztOS apps only</span></h2>
<p>The jump grid and the pickers. Each of the 28 tiles turns about a horizontal line through its own middle, in reading order, and each starts while the one before is still moving.</p>
<div class="table-wrap"><table>
<tr><th></th><th>Angle</th><th>Time</th><th>Curve</th><th>Visibility</th></tr>
<tr><td>In</td><td>-45 to 0 degrees</td><td>0.3 s</td><td>Log 200</td><td>opacity 0 at 0 s, 1 at 0.01 s</td></tr>
<tr><td>Out</td><td>0 to 60 degrees</td><td>0.2 s</td><td>Exp 150</td><td>opacity 1 until 0.199 s, 0 at 0.2 s</td></tr>
</table></div>
<p>These come from the Lumia 530 firmware's <code>ANIMATIONS.UIX</code> (<code>SwivelTransitionIn</code> at 0x3f29, <code>SwivelTransitionOut</code> at 0x3eb3), recorded in <code>ztmetro/core/zrnboard.h</code> as <code>ZB_SWIVEL_*</code>. <b>The firmware fixes each tile's motion but not the stagger.</b> The 12 ms step (<code>ZB_STAGGER_MS</code>) is ztOS's own choice, and so is using the same order going out. The source says which is which. Tile sizes are also from there and <code>CONSTANTS.UIX</code>: 99 wide with a 12 gap at 480, scaled by 0.75.</p>
<p>A picker adds fixed steps this demo leaves out: the box lit for 116 ms, the page gone in 50 ms, the surface in 33 ms (<code>ZB_BOX_MS</code>, <code>ZB_PAGE_OUT_MS</code>, <code>ZB_PAGE_IN_MS</code>).</p>
<div class="demos">""" + demo("board", "Board in, 500 ms held here for viewing, then out") + """</div>

<h2 id="catalogue">Every named transition <span class="tag dashed">ZrnMetroCore, older Python SDK</span></h2>
<p>The table <code>ztanims[]</code> in <code>ztmetro/core/zrnmetrocore.c</code>, read from the Lumia 530's compiled Iris markup. The readerboard pair stays only for the motion catalogue in <code>zrndevtest</code>.</p>
<div class="table-wrap"><table>
<tr><th>Name</th><th>Axis</th><th>Degrees</th><th>Pivot</th><th>Other</th><th>ms</th><th>Curve</th></tr>
""" + "".join("<tr><td><code>%s</code></td>%s</tr>\n" % (r[0], "".join("<td>%s</td>" % c for c in r[1:])) for r in CATALOGUE_ROWS) + """</table></div>
<div class="demos wide">""" + "".join(demo("n:" + r[0], r[0]) for r in CATALOGUE_ROWS) + """</div>

<h2 id="press">Press and tilt <span class="tag">libzrnui</span></h2>
<p>Press a row in this demo: it follows your pointer. What is under the finger leans toward it by up to <b>14 degrees</b>, but its far edge never lifts more than <b>40 pt</b>, and it sinks <b>4.5 %</b>. Rows tilt. Sliders and fields do not move, and a button fills instead. In takes <b>90 ms</b>, and the release takes 200 ms (160 ms when the press is cancelled by a scroll), all on <code>zui_ease_out</code>. DotMatrix uses the same <code>press_xf</code>.</p>
<p>Source: <code>press_xf</code>, <code>TILT_DEG</code>, <code>TILT_LIFT</code>, <code>PRESS_SINK</code> in <code>style-metro.c</code>, timing in <code>core.c</code>. ZrnMetroCore shares the numbers (<code>ZMC_TILT_*</code>).</p>
<div class="demos">""" + demo("press", "Tilt: press it") + """</div>

<h2 id="small">Small things <span class="tag">libzrnui</span></h2>
<div class="table-wrap"><table>
<tr><th>What</th><th>Numbers</th><th>Source</th></tr>
<tr><td>Switch block</td><td>180 ms, <code>zui_ease_out</code></td><td><code>zui_set_on</code>, <code>core.c</code></td></tr>
<tr><td>Pivot</td><td>240 ms from where the finger left it, <code>zui_ease_out</code>. Past a quarter of a screen a swipe goes on to the next tab</td><td><code>zui_tabs_select</code>, <code>extras.c</code>; <code>core.c</code></td></tr>
<tr><td>Toast</td><td>2600 ms: in over 200, out over the last 300. A bar drops 60 pt from the top</td><td><code>core.c</code>, <code>toast</code> in <code>style-metro.c</code></td></tr>
<tr><td>Busy, unknown progress</td><td>five 4 pt dots every 2600 ms, each 7.5 % later, on <code>0.5 + 4 (p - 0.5)^3</code> across the width</td><td><code>dots</code>, <code>style-metro.c</code></td></tr>
<tr><td>Fling</td><td>speed times <code>0.9972^ms</code>, a further <code>0.8^(ms/16)</code> past an end, stop under 0.02 pt/ms, then back to the end with a 70 ms time constant</td><td><code>core.c</code></td></tr>
<tr><td>Glide to the end of a chat</td><td>a 45 ms time constant, for up to 600 ms</td><td><code>zui_page_scroll_end</code>, <code>core.c</code></td></tr>
</table></div>
<p>A field's box turns from grey to white the moment it has focus. That change is not animated.</p>
<div class="demos">""" + demo("knob", "Switch") + demo("pivot", "Pivot") + demo("toast", "Toast") + demo("busy", "Busy") + demo("fling", "Fling at 3.2 pt/ms") + """</div>

<h2 id="old">Older Python SDK: where its numbers differ <span class="tag dashed">older</span></h2>
<p><code>ztos.animate(widget, name, repeat=False, on_done=None)</code> plays a named transition over any Qt widget. Its table is <code>TRANSITIONS</code> in <code>sdk/runtime/ztos/__init__.py</code>. Most entries match the list above, but <b>its swivel predates the firmware decode now in <code>zrnboard.h</code></b>:</p>
<div class="table-wrap"><table>
<tr><th></th><th>ZrnMetroCore (firmware)</th><th>Older Python SDK</th></tr>
<tr><td><code>swivel-in</code></td><td>-45 to 0, 300 ms, Log 200, no fade</td><td>-60 to 0, 300 ms, Log 200, fades 0 to 1</td></tr>
<tr><td><code>swivel-out</code></td><td>0 to 60, 200 ms, Exp 150, no fade</td><td>0 to 60, 199 ms, Exp 60, fades 1 to 0</td></tr>
<tr><td>Press in, out</td><td>90, 200 ms</td><td>70, 160 ms, divided by the menu speed setting</td></tr>
<tr><td>Row out</td><td>128 ms</td><td>110 ms, divided by the menu speed setting</td></tr>
</table></div>
<p>Everything else that moves in that SDK is also scaled by <code>ANIM_SPEED</code>, which comes from a user setting, so its real durations vary.</p>
"""

PAGES = {
"index": ("ztOS SDK wiki", "How to make apps for ztOS: C, C++, Rust and Python, every UI element with real renders, every animation running live, and how to publish.", """
<h1>Make apps for ztOS</h1>
<p class="lead">ztOS apps are written in C, C++, Rust or Python against one small GPU toolkit, <b>libzrnui</b>. <b>ztCoolStyle</b> is the name of that UI system. It draws in <b>Metro</b> or <b>DotMatrix</b>, whichever the system is set to. Apps ship as one signed <code>.zexec</code> file, and the store builds them from your source.</p>
<p><b>Requires ztOS BETA-1.1 or later.</b> Apps made with this SDK run on BETA-1.1 and newer; earlier versions of ztOS cannot run them.</p>
<pre><code>git clone https://github.com/Zerone-Laboratories/zrn-sdk
cd zrn-sdk && export PATH="$PWD/tools:$PATH"
zrn doctor
zrn new "Notes" --lang c
cd notes && zrn build && zrn render out.png</code></pre>
{{SHOTS:item}}
<div class="cards">
<a href="/start"><b>Getting started</b><span>Install, first app, first picture</span></a>
<a href="/apps"><b>Ways to make an app</b><span>Each language, the CLI, the older SDK</span></a>
<a href="/project"><b>Project and permissions</b><span>zrnapp.toml, ids, the manifest</span></a>
<a href="/elements"><b>UI elements</b><span>Each one, rendered, with its code</span></a>
<a href="/layout"><b>Layout and styles</b><span>How pages fit, Metro and DotMatrix</span></a>
<a href="/animations"><b>Animations</b><span>Swivel, turnstile, fade, tilt, running live</span></a>
<a href="/shipping"><b>Package and publish</b><span>Test, sign, submit, update, revoke</span></a>
<a href="/troubleshooting"><b>Troubleshooting</b><span>Real errors and their fixes</span></a>
<a href="/status"><b>Status and gaps</b><span>What is missing or unproven</span></a>
</div>
<h2>How the code on this site was checked</h2>
<p>Each element's snippet is <b>compiled in every language that has it</b> and rendered with <code>zrn render</code>, using the phone's own fonts from the ztOS tree. The renders are then compared pixel by pixel across languages. They match exactly, except the progress page, whose moving dots are caught at a different instant each time. The generator and report are in <a href="https://github.com/Zerone-Laboratories/zrn-sdk-site">this site's repository</a>. Animation numbers are read out of the C source and each one names its file.</p>
"""),

"start": ("Getting started: ztOS SDK", "Install the zrn CLI and libzrnui's build dependencies, make a first app, and see it without a phone.", """
<h1>Getting started</h1>
<p class="lead">You can write an app and see it without a phone. This takes a few minutes on a Linux computer.</p>
<div class="gap"><b>What you cannot do yet</b><p>Install on a phone from here with one command. <code>zrn install</code> installs for the user on the computer it runs on. Every build made on a laptop so far is x86_64 (or <code>any</code> for Python). See <a href="/status">Status and gaps</a>.</p></div>
<h2 id="need">What you need</h2>
<ul>
<li>Python 3.11 or newer, a C compiler, <code>make</code>, <code>pkg-config</code>.</li>
<li>Development files for Wayland, Mesa (EGL, GLES2, GBM), FreeType, HarfBuzz, fontconfig, libpng and xkbcommon. <code>libzrnui/Makefile</code> asks pkg-config for <code>wayland-client wayland-egl egl glesv2 freetype2 harfbuzz fontconfig libpng xkbcommon gbm</code>.</li>
<li>A C++ compiler for C++ apps, <code>cargo</code> for Rust apps.</li>
<li>For <code>zrn run</code> with no Wayland session: <code>kwin_wayland</code> or <code>weston</code>. Only <code>kwin_wayland</code> has been tried for this site.</li>
</ul>
<h2 id="install">Install</h2>
<pre><code>git clone https://github.com/Zerone-Laboratories/zrn-sdk
cd zrn-sdk
export PATH="$PWD/tools:$PATH"     <span class="c"># zrn and zrn-exec</span>
zrn doctor                         <span class="c"># what is missing, and the command that fixes it</span></code></pre>
<p>A healthy <code>zrn doctor</code>, from the machine that built this site:</p>
<pre><code>ok   python               3.14
ok   cc                   /usr/sbin/cc
ok   pkg-config           /usr/sbin/pkg-config
ok   make                 /usr/sbin/make
ok   c++                  /usr/sbin/c++
ok   cargo                /usr/sbin/cargo
ok   libraries            all present
ok   libzrnui             .../libzrnui/build
ok   fonts                .../libzrnui/fonts
ok   crypto               python-cryptography
opt  dev key              ~/.config/zrn/keys/dev.key
     fix: zrn keygen (zrn pack also makes one)
ok   headless compositor  kwin_wayland
ok   offscreen GPU        /dev/dri/renderD*</code></pre>
<p><code>zrn build</code> builds libzrnui from the tree the first time if it is not installed. To install it for the whole system: <code>make -C libzrnui &amp;&amp; sudo make -C libzrnui install PREFIX=/usr</code>.</p>
<h2 id="first">Your first app</h2>
<pre><code>zrn new "Notes" --lang c --id io.github.you.notes   <span class="c"># or cpp, python, rust</span>
cd notes
zrn build
zrn render out.png                                  <span class="c"># no phone, no display</span></code></pre>
<p>It writes <code>zrnapp.toml</code>, <code>icon.svg</code>, <code>main.c</code>, <code>AGENTS.md</code> and <code>.gitignore</code>. A cut-down version of what each template holds:</p>
{{TAB:hello}}
<h2 id="see">Look at it</h2>
<pre><code>zrn render out.png                          <span class="c"># first page, 360x740 points at scale 2</span>
zrn render --page 1 out.png                 <span class="c"># by creation order</span>
zrn render --page "Wi-Fi" --scroll 300 out.png
zrn render --style dotmatrix out.png
zrn render --scale 4 out.png                <span class="c"># the S9's 1440x2960</span>
zrn run                                     <span class="c"># a phone-sized window</span>
zrn run --headless --script "wait 500; tap 180 170; wait 600; snap after.png; quit"</code></pre>
<p>The style flag is only for looking. An app cannot pick its style: the system does. <code>zrn render</code> draws through the same GLES2 path as a running app, using Mesa's surfaceless EGL. <code>--page</code> counts pages in the order your code <b>creates</b> them, which is not the order they open.</p>
<h2 id="next">Next</h2>
<p><a href="/elements">UI elements</a> shows what you can put on a page. <a href="/shipping">Package and publish</a> shows how it reaches people.</p>
"""),

"apps": ("Ways to make an app: ztOS SDK", "Every way to make a ztOS app: C, C++, Rust, Python with libzrnui, the zrn commands, coding agents, and the older Python and Qt SDK.", """
<h1>Ways to make an app</h1>
<p class="lead"><b>Use libzrnui</b>, in whichever of its four languages you like. The older Python and Qt SDK is what the current phone image can already run, so it stays documented, but new work belongs on libzrnui.</p>
<div class="table-wrap"><table>
<tr><th>Way</th><th>Status</th><th>Draws with</th><th>Ships as</th></tr>
<tr><td>C, <code>zrnui.h</code></td><td>Laptop only so far</td><td>libzrnui, GLES2</td><td><code>.zexec</code></td></tr>
<tr><td>C++, <code>zrnui.hpp</code></td><td>Laptop only so far</td><td>libzrnui, GLES2</td><td><code>.zexec</code></td></tr>
<tr><td>Rust, crate <code>zrnui</code></td><td>Laptop only so far. Lacks pictures, long lists, pivots, footer, bubbles</td><td>libzrnui, GLES2</td><td><code>.zexec</code></td></tr>
<tr><td>Python, <code>import zrnui</code></td><td>Laptop only so far. Lacks pictures, long lists, pivots, footer, bubbles</td><td>libzrnui, GLES2, no Qt</td><td><code>.zexec</code>, any CPU</td></tr>
<tr><td>Older Python SDK, <code>ztos</code></td><td>Older. Runs on the phone</td><td>Qt, with a GPU layer for motion</td><td>An aarch64 ELF launcher plus a zip</td></tr>
<tr><td>ZrnMetroCore, <code>ztmetro/core</code></td><td>The ztOS apps themselves. Not an SDK</td><td>Cairo and Pango, GPU quads</td><td>Part of the system</td></tr>
</table></div>
<h2 id="same">One library, four languages</h2>
<p>One C library sits under all of them. Bindings pass handles and closures and draw nothing themselves, so what they share produces the same pixels. <b>Pictures, long lists, pivots, the footer and bubbles are in C and C++ only at this commit.</b></p>
{{TAB:hello}}
<div class="table-wrap"><table>
<tr><th>Language</th><th>Memory and callbacks</th><th>Differences to know</th></tr>
<tr><td>C</td><td>One callback shape: <code>void cb(zui_node *node, void *data)</code>. <code>zui_event(node)</code> says why it ran. <code>zui_set_handler</code> takes a <code>free_data</code></td><td>Names start <code>zui_</code></td></tr>
<tr><td>C++</td><td>Header only, namespace <code>zrn::ui</code>. <code>App</code> frees everything. <code>Node</code> is a handle you can copy</td><td><code>toggle</code>, not <code>switch</code>. No <code>watch_fd</code>: use <code>zui_watch_fd(app.get(), ...)</code></td></tr>
<tr><td>Rust</td><td>Every <code>Node&lt;'a&gt;</code> is tied to its <code>App</code> by lifetime. Closures are boxed and dropped with the node</td><td>Handlers: <code>on_click</code>, <code>on_change</code>, <code>on_slide</code>, <code>on_edit</code>, <code>on_event</code>. Other threads use <code>app.poster()</code>. No <code>watch_fd</code> wrapper</td></tr>
<tr><td>Python</td><td><code>ctypes</code>, with callbacks kept until the node is freed. An exception in a callback prints and does not cross into C</td><td>Keyword handlers and properties: <code>.detail=</code>, <code>.value=</code>, <code>.on=</code>, <code>.icon=</code></td></tr>
</table></div>
<h2 id="pages">Pages and moving between them</h2>
<p>An app is a set of pages. Back on the first page closes the app. The hardware Back, Escape, the round back button and, in Metro, a tap on the title all go back.</p>
{{TAB:nav}}
<h2 id="loop">The main loop</h2>
<p>All calls come from one thread, the one that called <code>run</code>. <code>post</code> is the only way in from another. There is one app per process.</p>
{{TAB:loop}}
<h2 id="zrn">The zrn commands</h2>
<div class="table-wrap"><table>
<tr><th>Command</th><th>What it does</th></tr>
<tr><td><code>zrn new NAME --lang c|cpp|python|rust [--id ID] [--dir D]</code></td><td>A project from a template. The default id is <code>io.github.$USER.name</code></td></tr>
<tr><td><code>zrn build [--arch A]</code></td><td>C and C++ against the system's or the SDK's libzrnui. Rust with cargo. Python is syntax-checked</td></tr>
<tr><td><code>zrn render OUT.png [--page N|TITLE] [--style metro|dotmatrix] [--size WxH] [--scale S] [--scroll Y]</code></td><td>Draws a page, no display needed</td></tr>
<tr><td><code>zrn run [--headless] [--script S] [--style] [--size] [--scale] [--timeout T]</code></td><td>In your Wayland session, else a nested compositor. <code>--headless</code>: a virtual one</td></tr>
<tr><td><code>zrn pack [--arch] [--out D] [--key K] [--no-sign] [--bundle-zrnui]</code></td><td>Makes <code>dist/&lt;id&gt;-&lt;version&gt;-&lt;arch&gt;.zexec</code> and <code>.minisig</code></td></tr>
<tr><td><code>zrn verify FILE [--sig S] [--key K]</code></td><td>Exit 0 good, 1 broken, 2 not trusted</td></tr>
<tr><td><code>zrn install FILE [--key K]</code>, <code>zrn uninstall ID</code></td><td>For this user, on this computer</td></tr>
<tr><td><code>zrn info FILE</code></td><td>The manifest and the files inside</td></tr>
<tr><td><code>zrn exec FILE</code></td><td>What <code>zrn-exec</code> does: verify, unpack once, run</td></tr>
<tr><td><code>zrn keygen [--name N] [--output O] [--force] [--no-trust]</code></td><td>A signing key. <code>zrn pack</code> makes one if you have none</td></tr>
<tr><td><code>zrn submit [--repo R] [--commit C] [--contact C] [--notes N] [--send]</code></td><td>Shows the store entry for HEAD. Only <code>--send</code> sends it</td></tr>
<tr><td><code>zrn doctor</code></td><td>The toolchain, and how to fix what is missing</td></tr>
<tr><td><code>zrn init-agents [--agent a,b] [--all] [--list] [--force]</code></td><td>Instruction files and the <code>zrnui</code> skill for coding agents</td></tr>
</table></div>
<p>Every command takes <code>--json</code>, which prints one object on stdout. Errors look like <code>{"ok": false, "error": {"code", "message", "hint"}}</code>. Exit 3 is a usage error. <code>-C DIR</code> runs in another project folder.</p>
<h2 id="agents">With a coding agent</h2>
<pre><code>zrn init-agents --list
claude       CLAUDE.md                            .claude/skills/zrnui
codex        AGENTS.md                            .agents/skills/zrnui
gemini       GEMINI.md                            .gemini/skills/zrnui
cursor       .cursor/rules/zrnui.mdc              .cursor/skills/zrnui
copilot      .github/copilot-instructions.md      .github/skills/zrnui
opencode     AGENTS.md                            .opencode/skills/zrnui
antigravity  .agent/rules/zrnui.md                .agent/skills/zrnui
windsurf     .windsurf/rules/zrnui.md             .windsurf/skills/zrnui</code></pre>
<p>It only writes into an app's own folder, one with <code>zrnapp.toml</code>. An agent can check its own work with <code>zrn render</code> and read the picture. The paths for Cursor, Windsurf and Gemini are the least certain, as <code>DESIGN.md</code> says.</p>
<h2 id="old">The older Python SDK <span class="tag dashed">older</span></h2>
<p>In the ztOS repository at <code>sdk/</code>. Apps are Python with Qt (PySide6), in the Metro look only. A built app is a small aarch64 ELF launcher with a zip behind it. No screenshots here: nothing from this SDK was rendered for this site.</p>
<pre><code>ztos-sdk new "Notes"     <span class="c"># a new app in ./notes</span>
ztos-sdk run             <span class="c"># a 360x640 window; Escape is back</span>
ztos-sdk designer        <span class="c"># draw pages in Qt Designer</span>
ztos-sdk deploy          <span class="c"># build, install on the phone over SSH, open it</span>
ztos-sdk logs -f
ztos-sdk doctor          <span class="c"># also: build, install, launch, uninstall, list</span></code></pre>
<pre><code>import ztos

app = ztos.App()

class Home(ztos.Page):
    def __init__(self):
        super().__init__("notes")
        self.entry("new note", "start writing", lambda: app.push(Editor()))
        self.toggle("Sync", on=True, on_change=self.sync)

    def sync(self, on):
        ztos.notify("Notes", "sync on" if on else "sync off")

app.run(Home())</code></pre>
<p>It has things libzrnui lacks at this commit: <code>menu</code>, <code>Dialog</code>, <code>message</code>, <code>notify</code>, <code>store</code>, <code>battery</code>, <code>performance</code> and <code>animate</code>. The project file is <code>ztos.toml</code>, not <code>zrnapp.toml</code>, and its ids reserve both <code>zt</code> and <code>zrn</code>. The full reference is <a href="https://github.com/Zerone-Laboratories/ztOS/blob/main/sdk/README.md">sdk/README.md</a>.</p>
<h2 id="core">ZrnMetroCore <span class="tag dashed">not an SDK</span></h2>
<p>The C toolkit behind ztOS's own apps (<code>ztmetro/core</code>). It builds inside the ztOS tree and has no packaging or stable interface for outside apps. It appears here because its <a href="/animations">animations</a> are the reference for Metro's motion. <code>DESIGN.md</code> plans to move those apps to libzrnui one at a time.</p>
"""),

"project": ("Project file and permissions: ztOS SDK", "zrnapp.toml field by field, id rules, permissions, and the .zexec manifest.", """
<h1>Project file and permissions</h1>
<p class="lead"><code>zrnapp.toml</code> says who the app is and how to build it. <b>Permissions are declarations only for now: nothing enforces them.</b></p>
<h2 id="toml">zrnapp.toml</h2>
<p>This is what <code>zrn new "Notes" --lang python</code> writes:</p>
<pre><code>[app]
id = "io.github.you.notes"
name = "Notes"
version = "0.1.0"
summary = "Notes for ztOS"
author = ""
licence = "MIT"
icon = "icon.svg"
categories = ["Utility"]
permissions = []

[build]
lang = "python"
entry = "main.py"
include = ["*.py"]</code></pre>
<p>For C and C++ <code>[build]</code> has <code>lang</code> and <code>sources = ["main.c"]</code>. Rust has <code>lang = "rust"</code> and its <code>Cargo.toml</code>, whose <code>zrnui</code> dependency is a path into your copy of the SDK.</p>
<div class="table-wrap"><table>
<tr><th>Field</th><th>Rule</th></tr>
<tr><td><code>id</code></td><td>Reverse-DNS with three or more parts, lower case. Never changes. Also the Wayland app_id and desktop id. Pass the same id to <code>App</code> in your code</td></tr>
<tr><td><code>version</code></td><td>Semantic. Higher than any version already in the store</td></tr>
<tr><td><code>name</code>, <code>summary</code>, <code>author</code>, <code>licence</code>, <code>icon</code></td><td>All needed by the store. Licence is an SPDX id</td></tr>
<tr><td><code>homepage</code>, <code>categories</code></td><td>Shown in the app list and the store</td></tr>
<tr><td><code>permissions</code></td><td>See below</td></tr>
</table></div>
<p>A bad id stops the build and tells you the fix:</p>
<pre><code>zrn: error: .../zrnapp.toml: id 'badid' is not valid
zrn: fix: use reverse-DNS with at least three parts (io.github.you.app) or zrn-name for Zerone Laboratories' apps</code></pre>
<h2 id="perms">Permissions</h2>
<div class="gap"><b>Gap: declared, not enforced</b><p>An app can do what its user can do, whatever this list says. Moderators read the list and ask about each one. Enforcing it with bubblewrap or Landlock is planned in <code>DESIGN.md</code>'s Round 2. Declare honestly now, because that is what gets reviewed.</p></div>
<div class="table-wrap"><table>
<tr><th>Name</th><th>Means</th></tr>
<tr><td><code>network</code>, <code>audio</code>, <code>camera</code>, <code>location</code>, <code>bluetooth</code></td><td>The hardware or network</td></tr>
<tr><td><code>notifications</code>, <code>background</code></td><td>Showing notifications, running when not in front</td></tr>
<tr><td><code>phone</code>, <code>contacts</code>, <code>messages</code></td><td>Personal data and calls</td></tr>
<tr><td><code>files.music</code>, <code>files.pictures</code>, <code>files.documents</code>, <code>files.downloads</code></td><td>Those folders</td></tr>
</table></div>
<h2 id="manifest">What goes in the package</h2>
<p><code>zrn pack</code> turns the project into a manifest, <code>zexec.json</code>. From <code>zrn info</code> on the app above:</p>
<pre><code>{
 "arch": "any",
 "built": { "by": "zrn 0.1.0", "lang": "python" },
 "categories": [ "Utility" ],
 "entry": "app/main.py",
 "icon": "icon.svg",
 "id": "io.github.you.notes",
 "licence": "MIT",
 "min_ztos": "0.1",
 "name": "Notes",
 "permissions": [],
 "runtime": "python3",
 "summary": "Notes for ztOS",
 "version": "0.1.0",
 "zexec": 1,
 "zrnui": "0.1"
}
        417  zexec.json
        345  app/main.py
        207  icon.svg</code></pre>
<p>The store's CI adds <code>source</code>, which holds the repo and commit. <code>bundles</code> is set when libzrnui is inside. <code>arch</code> is <code>aarch64</code>, <code>x86_64</code> or <code>any</code>.</p>
<h2 id="licence">Licences</h2>
<p>libzrnui and the bindings are <b>LGPL-2.1-or-later</b>, so an app under any licence can link them. The <code>zrn</code> tools are GPL-2.0-or-later. Examples and templates are MIT, so what <code>zrn new</code> gives you is yours. The bundled fallback font, Selawik, is SIL OFL 1.1. Segoe UI and Segoe MDL2 Assets come from the system and are not in the SDK or on this site.</p>
"""),

"elements": ("UI elements: ztOS SDK", "Every libzrnui element, rendered in Metro and DotMatrix, with code in C, C++, Rust and Python where each has it.", """
<h1>UI elements</h1>
<p class="lead">Every element libzrnui has at commit <code>""" + COMMIT + """</code>, rendered by <code>zrn render</code> from the code beside it.</p>
<p>The language tab you pick is remembered. Each snippet is the body of a function that has <code>app</code> and <code>page</code>, and every language shown compiled and rendered the same pixels, except that the moving progress dots differ. Pictures use the phone's Segoe fonts.</p>
<div class="gap"><b>Not in this commit</b>
<p>Dialogs, menus and pickers. <a href="/status">Status and gaps</a> has the full list.</p></div>
<div class="cards">
<a href="#text"><b>Text</b></a><a href="#button"><b>Buttons</b></a><a href="#item"><b>List rows</b></a><a href="#switch"><b>Switches</b></a><a href="#slider"><b>Sliders</b></a><a href="#progress"><b>Progress</b></a><a href="#field"><b>Text fields</b></a><a href="#section"><b>Sections and cards</b></a><a href="#layout"><b>Rows, columns, space</b></a><a href="#round"><b>Round buttons</b></a><a href="#picture"><b>Pictures</b></a><a href="#list"><b>Long lists</b></a><a href="#pivot"><b>Pivots</b></a><a href="#bubble"><b>Bubbles</b></a><a href="#footer"><b>Footer</b></a><a href="#icons"><b>Icons</b></a><a href="#busy"><b>Busy</b></a><a href="#toast"><b>Toast</b></a><a href="#changing"><b>Changing things</b></a>
</div>
{{ELEMENTS}}
<h2 id="busy">Busy</h2>
<p><code>zui_busy(app, true)</code>, or <code>app.busy(True)</code> in Python, shows that something is loading: dots crossing the top of the screen. These pictures come from a running app in a virtual compositor, one instant of the movement. <a href="/animations#small">See it move</a>.</p>
{{SHOTS:busy}}
<h2 id="toast">Toast</h2>
<p><code>zui_toast(app, "Saved")</code>, or <code>app.toast("Saved")</code> in the other languages, shows a short message for 2.6 seconds, on an accent bar from the top.</p>
{{SHOTS:toast}}
<h2 id="changing">Changing things after they are made</h2>
<p>The tree stays. Keep the node and change it: the app redraws only when something changed.</p>
<div class="table-wrap"><table>
<tr><th>C</th><th>C++, Rust</th><th>Python</th><th>Does</th></tr>
<tr><td><code>zui_set_text</code>, <code>zui_get_text</code></td><td><code>set_text</code>, C++ <code>text_value</code>, Rust <code>get_text</code></td><td><code>set_text()</code>, <code>.text_value</code></td><td>Label, title or field text</td></tr>
<tr><td><code>zui_set_detail</code></td><td><code>set_detail</code></td><td><code>.detail=</code></td><td>An item's value on the right; a switch's second line</td></tr>
<tr><td><code>zui_set_subtitle</code></td><td><code>set_subtitle</code></td><td><code>.subtitle=</code></td><td>The line under a title</td></tr>
<tr><td><code>zui_set_value</code>, <code>zui_get_value</code></td><td><code>set_value</code>, <code>value</code></td><td><code>.value</code></td><td>Slider or progress, 0 to 1</td></tr>
<tr><td><code>zui_set_on</code>, <code>zui_get_on</code></td><td><code>set_on</code>, <code>is_on</code></td><td><code>.on</code></td><td>A switch</td></tr>
<tr><td><code>zui_set_enabled</code></td><td><code>set_enabled</code></td><td><code>.enabled=</code></td><td>40 % opacity, no touch</td></tr>
<tr><td><code>zui_set_visible</code></td><td><code>set_visible</code></td><td><code>.visible=</code></td><td>Hidden nodes take no room</td></tr>
<tr><td><code>zui_clear</code>, <code>zui_destroy</code></td><td><code>clear</code>, C++ <code>destroy</code></td><td><code>clear()</code>, <code>destroy()</code></td><td>Remove what is in it, or it. Do not use old handles after</td></tr>
</table></div>
"""),

"layout": ("Layout and styles: ztOS SDK", "How libzrnui lays out pages, ztCoolStyle's two styles Metro and DotMatrix, palettes, fonts and accent colours.", """
<h1>Layout and styles</h1>
<p class="lead"><b>You say what is on a page; the system decides how it looks.</b> Everything is in points on a 360 point wide phone, and the same code draws in either style.</p>
<h2 id="layout">How a page is laid out</h2>
<ul>
<li>A page is a column. Things appear in the order you add them.</li>
<li><code>section</code> and <code>card</code> group things. Prefer these to manual spacing.</li>
<li><code>row</code> sets things side by side. <code>set_flex</code> shares spare width by proportion.</li>
<li>Pages scroll by themselves when they outgrow the screen. A hidden node takes no room.</li>
<li>A <code>list</code> goes last in its page or tab. A <code>footer</code> stays at the bottom over the list.</li>
<li>Scale: <code>ZUI_SCALE</code>, else the shell's <code>ZTMETRO_SCALE</code> (4 on the S9, so 1440x2960 pixels is 360x740 points), else the compositor's.</li>
</ul>
<h2 id="pick">ztCoolStyle and who picks the style</h2>
<p><b>ztCoolStyle</b> is the name of this UI system. Its only styles are <b>Metro</b> and <b>DotMatrix</b>. <b>An app cannot pick one</b>, so it never differs from what is around it, and the two never mix. In order (<code>pick_style</code> in <code>core.c</code>):</p>
<ol>
<li><code>ZUI_STYLE</code> in the environment, for renders and tests only. This is what <code>--style</code> sets.</li>
<li>The session's <code>ZTRF_SHELL_STYLE</code>.</li>
<li><code>style =</code> in <code>~/.config/ztmetro/config</code>.</li>
<li>Metro.</li>
</ol>
<p><code>zui_app_set_style</code> and <code>zui_app_set_theme</code> are kept for the ABI and change nothing for a user: both styles are black, and there is no light theme.</p>
{{SHOTS:section}}
<h2 id="metro">Metro</h2>
<p>The same widgets as ZrnMetroCore draws them: black, white Segoe UI, the app's name in capitals over a 48 pt lowercase title fixed at the top, pivots whose next titles run grey off the edge, rectangular toggles, outlined buttons that fill when pressed, round buttons with a word under them, Messaging's thread rows and bubbles, the tilt on press and the turnstile between pages.</p>
<h2 id="dotmatrix">DotMatrix</h2>
<p>The same widgets in the same places. Everything filled is drawn by one fragment shader as dots 2.3 pt apart on one lattice, lit where the shape covers the cell's centre. Text is a 3x5 dot type drawn for this library, in upper case with no shaping, so <b>scripts other than Latin come out as <code>?</code></b>, as in ztMETRO. Pictures are dots of the palette's main colour at their brightness. Compared with the shell's own DotMatrix it lacks the ghost field and the glow.</p>
<p><code>dotmatrix_palette =</code> in the same config file picks one of six palettes, by number or by name: Mono, Amber, Green, Ice, White, Red. The accent is the palette's, so <code>set_accent</code> is ignored.</p>
<div class="strip" tabindex="0"><img src="/img/palettes.webp" alt="The same page in DotMatrix's six palettes" loading="lazy"></div>
<h2 id="numbers">The numbers</h2>
<p>From <code>.m</code> in <code>style-metro.c</code>, in points, the same for both styles.</p>
<div class="table-wrap"><table>
<tr><th>What</th><th>Value</th></tr>
<tr><td>Page margin, gap</td><td>16, 12</td></tr>
<tr><td>Title, header</td><td>48, fixed, in a 108 pt header</td></tr>
<tr><td>Body, heading, caption</td><td>16, 25.5, 13</td></tr>
<tr><td>Row height, with a second line</td><td>52, 66</td></tr>
<tr><td>Row title, second line</td><td>21, 13</td></tr>
<tr><td>Button height</td><td>40, or 72 round with its word</td></tr>
<tr><td>Field height</td><td>44, plus a 22 pt caption outside a footer</td></tr>
<tr><td>Corners, card padding</td><td>0</td></tr>
<tr><td>Line spacing</td><td>1.25</td></tr>
</table></div>
<h2 id="fonts">Fonts and colour</h2>
<ul>
<li><b>Text:</b> Segoe UI from the system. Selawik, its open metric twin, is bundled and used only where Segoe is absent.</li>
<li><b>Icons:</b> Segoe MDL2 Assets from the system. Strokes under DotMatrix or without the font.</li>
<li><b>Metro colours:</b> black <code>#000000</code>, white text, grey <code>#999999</code> second lines, red <code>#E51400</code> for danger, the accent for what is on.</li>
<li><b>Accent:</b> <code>ZUI_ACCENT</code>, else <code>accent =</code> in the config (a ztmetro colour name or <code>#rrggbb</code>), else cobalt <code>#0050EF</code>. Leave it to the system.</li>
</ul>
{{TAB:accent}}
<h2 id="rules">Style rules</h2>
<ul>
<li>One primary button a page at most. Others tonal or plain, and danger for what destroys.</li>
<li>Short noun titles. Metro shows them in lower case.</li>
<li>Leave the accent to the system.</li>
<li>Check both styles before you publish: <code>zrn render --style dotmatrix</code>.</li>
<li>Do not imitate system UI. Moderators reject it.</li>
</ul>
<h2 id="scripts">Other scripts</h2>
<p>In Metro, HarfBuzz shapes Sinhala, Tamil, Greek and Cyrillic, and CJK comes from fontconfig fallback. <b>Bidirectional text is not reordered</b>, so Arabic and Hebrew will not read correctly yet. DotMatrix shows Latin only.</p>
"""),

"animations": ("Animations: ztOS SDK", "Swivel with its domino stagger, turnstile, fade, tilt and every other ztOS animation, running live with the real durations, curves and angles.", ANIMATIONS),

"shipping": ("Package and publish: ztOS SDK", "Testing without a phone, packing a signed .zexec, submitting to the ztOS store, updates and revocation.", """
<h1>Package and publish</h1>
<p class="lead">Test with pictures, pack a signed <code>.zexec</code>, push your source, and the store builds that exact commit. <b>You never upload a binary.</b></p>
<div class="gap"><b>Warning: this path is not proven end to end</b>
<p>The submission Worker, bot and publishing workflow are deployed, and the publish run produced an empty signed index. <b>No real app has yet gone from submit through Accept to a listed build.</b> The phone's store app cannot show these apps yet. Expect rough edges, and tell the moderators on Discord what you hit.</p></div>
<h2 id="test">Test</h2>
<pre><code>zrn render out.png
zrn render --style metro out.png
zrn run --headless --script "wait 500; tap 180 170; type hi; wait 600; snap after.png; back; quit"
make check          <span class="c"># in the SDK: C, tool and Rust tests</span></code></pre>
<p>Script steps are <code>wait MS</code>, <code>tap X Y</code>, <code>drag X Y POINTS</code> (a finger moving that far up over 200 ms), <code>type TEXT</code>, <code>snap FILE</code>, <code>back</code> and <code>quit</code>, separated by semicolons. A snapshot takes a while, so use one per run when timing matters.</p>
<p>In C tests, <code>zui_layout</code>, <code>zui_inject_touch</code> and <code>zui_inject_text</code> work with no display. Python has <code>app.layout()</code> and <code>app.tap()</code>, and <code>Node.frame()</code> says where something landed. <code>ZUI_PERFLOG=1</code> prints what each frame costs the CPU.</p>
<h2 id="pack">Pack</h2>
<pre><code>$ zrn pack
zrn: made signing key A90978EBF45FDFE2 (~/.config/zrn/keys/dev.key); this user now trusts it
packed dist/io.github.you.notes-0.1.0-any.zexec (1120 bytes, sha256 ef4693336d58fd18...), signed by A90978EBF45FDFE2
$ zrn verify dist/io.github.you.notes-0.1.0-any.zexec
good: io.github.you.notes 0.1.0 (any), signed by A90978EBF45FDFE2
$ zrn install dist/io.github.you.notes-0.1.0-any.zexec
installed io.github.you.notes 0.1.0 -> ~/.local/share/zrn/apps/io.github.you.notes/io.github.you.notes.zexec
  app list: ~/.local/share/applications/io.github.you.notes.desktop</code></pre>
<p>Output above is real, with paths shortened. A native package holds a program for one CPU, so one built on a laptop runs only on x86_64. Python packages are <code>any</code>. Until libzrnui ships in the system image, <code>zrn pack --bundle-zrnui</code> puts it inside the package.</p>
<h3>What a .zexec is</h3>
<pre><code>#!/usr/bin/env zrn-exec\\n      <span class="c"># chmod +x and run it</span>
&lt;zip archive&gt;
  zexec.json                    <span class="c"># the manifest, first</span>
  icon.svg | icon.png
  bin/&lt;id&gt;                      <span class="c"># native: the program</span>
  lib/  share/                  <span class="c"># optional libraries and data</span>
  app/                          <span class="c"># python3: the sources</span>
&lt;file&gt;.zexec.minisig            <span class="c"># detached minisign-format signature</span></code></pre>
<p><code>zrn-exec</code> checks structure and signature before anything inside runs, unpacks once to <code>~/.cache/zrn/apps/&lt;id&gt;/&lt;sha256&gt;</code>, and logs what the app prints to <code>~/.local/state/zrn/&lt;id&gt;.log</code>. Packing is reproducible: the same commit gives the same bytes. Trusted keys live in <code>/etc/zrn/trusted-keys</code>, <code>/usr/share/zrn/trusted-keys</code> and <code>~/.config/zrn/trusted-keys</code>. The format has not been cross-checked against the real <code>minisign</code> program.</p>
<h2 id="submit">Submit to the store</h2>
<ol>
<li>Your app builds from a clean checkout. Rust crates are the only downloads allowed in a build.</li>
<li><code>zrnapp.toml</code> is complete, and the id is one you control.</li>
<li>Push to a <b>public GitHub repository</b>. Other hosts are planned.</li>
<li><code>zrn submit</code> shows the entry for HEAD, which must be clean. <code>zrn submit --send</code> sends it.</li>
</ol>
<p>Or on the ztOS Mobile Discord: <code>/submit-app repo:https://github.com/you/notes commit:&lt;40-digit SHA&gt; [subdir:app]</code>.</p>
<h3>What happens next</h3>
<ol>
<li>The Worker checks the commit exists and reads <code>zrnapp.toml</code> at that commit.</li>
<li>The bot opens a post in <b>#ztos-app-submissions</b> with the manifest, the permissions, and a link to the exact tree.</li>
<li>A moderator reads the source and presses <b>Accept</b> or <b>Reject</b>, with a reason.</li>
<li>Accept records the release in <code>ledger/&lt;id&gt;.toml</code>: the commit, who approved it and when.</li>
<li>CI builds that commit with no secrets and no token, for aarch64 (Python once, for any CPU). A separate job signs it without running anything from the package, then publishes it to the signed index.</li>
</ol>
<h3>What gets you rejected</h3>
<ul>
<li>Doing what the permissions do not say, or asking for permissions the app does not use.</li>
<li>Obfuscated code, code that downloads and runs code, or an app that is not what its name says.</li>
<li>A build that fails from a clean checkout.</li>
<li>Unreadable text or fake system UI.</li>
</ul>
<h2 id="update">Updates</h2>
<p>An update is a new submission: raise <code>version</code>, commit, push, <code>zrn submit --send</code>. Moderators see a compare link from your last approved commit. The store never follows a branch, so changing or force-pushing your repository does nothing to what is listed. If that removes the commit, the build fails rather than changes.</p>
<h2 id="revoke">Revocation</h2>
<p>A moderator can revoke a release for a security problem, abuse or a licence problem, with <b>Revoke</b> on the post or <code>/revoke-app id version reason</code>. The ledger records who, when and why, and the release leaves the index. The design says phones then disable it and show the reason, <b>but the phone client for this does not exist yet</b>. To recover, fix it and submit a new version.</p>
<p>Full rules: <a href="https://github.com/Zerone-Laboratories/ztOS-apprepo/blob/main/CONTRIBUTING.md">the store's CONTRIBUTING.md</a>. Threat model: <a href="https://github.com/Zerone-Laboratories/zrn-sdk/blob/main/DESIGN.md#threat-model">DESIGN.md</a>.</p>
"""),

"troubleshooting": ("Troubleshooting: ztOS SDK", "Real zrn errors and what to do about them.", """
<h1>Troubleshooting</h1>
<p class="lead"><b>Start with <code>zrn doctor</code>.</b> Every <code>zrn</code> error names the file or value and a fix. The errors quoted here were produced for real.</p>
<h2 id="id">"id ... is not valid"</h2>
<pre><code>zrn: error: .../zrnapp.toml: id 'badid' is not valid
zrn: fix: use reverse-DNS with at least three parts (io.github.you.app) or zrn-name for Zerone Laboratories' apps</code></pre>
<p>Use something like <code>io.github.you.notes</code>. Do not use <code>zrn-</code>, which is reserved for Zerone Laboratories.</p>
<h2 id="page">"the app did not draw"</h2>
<pre><code>zrn: error: the app did not draw .../x.png (exit 0)
zrnui: no page "nope" (the app has 1 pages: 0="Notes")
zrn: fix: the app must call zui_run()/app.run() with its first page; offscreen drawing needs Mesa's EGL (surfaceless) or a /dev/dri render node</code></pre>
<p><b>Read the middle line.</b> It lists the pages that exist. The "fix" line is generic, and here the cause is the wrong <code>--page</code>. Otherwise check that your program reaches <code>run</code>, and that <code>zrn doctor</code> shows "offscreen GPU".</p>
<h2 id="git">"not in a git repository"</h2>
<pre><code>zrn: error: .../notes is not in a git repository
zrn: fix: the store builds from a public git repository: push the app to one first</code></pre>
<p><code>zrn submit</code> needs a repository, a clean HEAD and a pushed commit.</p>
<h2 id="verify">zrn verify exits 2</h2>
<p>The package is sound but no key you trust signed it. Trust the signer in <code>~/.config/zrn/trusted-keys</code>, or pass <code>--key FILE</code>. Exit 1 means broken: rebuild it. The same check stops <code>zrn install</code> and <code>zrn-exec</code>.</p>
<h2 id="rust">A Rust project will not build elsewhere</h2>
<p><code>zrn new --lang rust</code> writes an absolute path to your SDK copy in <code>Cargo.toml</code>. <b>If you move the SDK or share the project, change that path.</b> How the store's CI handles it is decided by its build tooling, so test a clean checkout.</p>
<h2 id="render">The render looks different from the window</h2>
<ul>
<li><code>ZUI_STYLE</code>, <code>ZTRF_SHELL_STYLE</code> and <code>style =</code> in your <code>~/.config/ztmetro/config</code> decide the style, whatever your code does. <code>--style</code> overrides them for a run.</li>
<li>Moving dots are drawn at whichever instant the render happens, so two renders of them differ.</li>
<li>Without Segoe UI on your computer, renders use Selawik. Without Segoe MDL2 Assets, icons are the stroke versions.</li>
</ul>
<h2 id="icon">My icon does not appear</h2>
<p>Check the name against the <a href="/elements#icons">twenty-one that exist</a>: an unknown name draws nothing. If an icon looks like thin lines in Metro, your system lacks Segoe MDL2 Assets.</p>
<h2 id="slow">A callback did nothing, or the app froze</h2>
<ul>
<li>Everything runs on one thread. Do long work on another and come back through <code>post</code>.</li>
<li>Python: an exception in a callback prints a traceback and goes no further. Look at the terminal or <code>~/.local/state/zrn/&lt;id&gt;.log</code>.</li>
<li>Rust: a closure that outlives its <code>App</code> will not compile, by design.</li>
</ul>
<h2 id="old">The older SDK</h2>
<p><code>ztos-sdk doctor --fix</code> installs what the phone needs for that SDK, over SSH to <code>alarm@172.16.42.1</code>. A package with compiled code cannot be bundled there: install it on the phone with pacman.</p>
"""),

"status": ("Status and gaps: ztOS SDK", "What the ztOS SDK does not do yet, and what has not been proven.", """
<h1>Status and gaps</h1>
<p class="lead"><b>This page lists what libzrnui does not do yet</b>, as of commit <code>""" + COMMIT + """</code>, so that nobody has to discover it the hard way.</p>
<h2 id="unproven">Not proven</h2>
<ul>
<li><b>Nothing from zrn-sdk has been reported running on a phone</b> by <code>DESIGN.md</code> at this commit. Frame times on the Mali-G72 are inferred, not measured. CPU cost was measured on a 2012 laptop: about 0.78 ms a frame in Metro at the S9's resolution.</li>
<li><b>No aarch64 build on a laptop.</b> There is no local cross compiler. The store's CI is meant to build aarch64 on an ARM runner.</li>
<li><b>The store has not carried a real app end to end.</b></li>
<li><code>zrn run</code> as a visible window has not been tried: only <code>--headless</code> in <code>kwin_wayland</code>. Weston has not been tried here either.</li>
<li>The signature format has not been checked against the real <code>minisign</code> program.</li>
</ul>
<h2 id="missing">Missing from libzrnui</h2>
<ul>
<li>Dialogs, menus, pickers, date and time, pull to refresh.</li>
<li><b>Pictures, long lists, pivots, the footer and bubbles in Rust and Python.</b> Those bindings have no call for them yet, though C and C++ do.</li>
<li>Any app-level animation call or custom drawing. An app cannot pick or add a style.</li>
<li>Password or multi-line fields, and your own icon files.</li>
<li>Bidirectional text, screen reader names and other accessibility.</li>
<li>Notifications, stored settings, and the battery and performance calls that the older SDK has.</li>
<li>In DotMatrix: the shell's ghost field and glow, and any script other than Latin.</li>
</ul>
<h2 id="platform">Missing from the platform</h2>
<ul>
<li><b>Permissions are not enforced.</b></li>
<li><b>The phone's store app does not list these apps yet</b>, so it cannot install, update or disable them. That includes acting on a revocation.</li>
<li>libzrnui and <code>zrn-exec</code> are not in the system image. Until they are, use <code>--bundle-zrnui</code>, though <code>zrn-exec</code> itself still has to be present.</li>
<li>Only GitHub is accepted as a source host.</li>
</ul>
<h2 id="site">About this site</h2>
<ul>
<li>The element pictures came from <code>zrn render</code> on a laptop's GPU with the phone's fonts from the ztOS tree, and busy, toast and the page-change frames from <code>kwin_wayland</code>'s virtual backend. None came from a phone.</li>
<li>The older Python SDK and ZrnMetroCore were read from source, and were not run for this site.</li>
<li>The animation demos are web ports of the formulas. <a href="/animations#how">The differences are listed there</a>.</li>
</ul>
"""),

"404": ("Not found: ztOS SDK", "That page does not exist.", """
<h1>Not here</h1>
<p class="lead">That page does not exist. Try <a href="/">the overview</a>.</p>
"""),
}
