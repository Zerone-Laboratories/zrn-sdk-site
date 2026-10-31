"""Every UI element the site documents, as real code in four languages.

gen/render.py compiles these into four programs, renders each page with
`zrn render`, and compares the four languages pixel by pixel. What the site
shows is what compiled.

Each snippet is the body of a function that has `app` and `page`.
"""

ICONS = ["wifi", "bluetooth", "bell", "moon", "sun", "lock", "volume", "battery",
         "info", "search", "plus", "check", "close", "more", "back", "chevron",
         "music", "person", "gear", "phone"]

ELEMENTS = [
    dict(id="text", title="Text", h=300, api="zui_text, zui_heading, zui_caption",
         blurb="Three sizes of words. Long text wraps by itself. Change it later with <code>set_text</code>.",
         c='''zui_heading(page, "A heading");
zui_text(page, "Body text. It wraps at the page's width, and HarfBuzz shapes it, so Sinhala and Tamil come out right.");
zui_caption(page, "A caption: small and quiet.");''',
         cpp='''page.heading("A heading");
page.text("Body text. It wraps at the page's width, and HarfBuzz shapes it, so Sinhala and Tamil come out right.");
page.caption("A caption: small and quiet.");''',
         rs='''page.heading("A heading");
page.text("Body text. It wraps at the page's width, and HarfBuzz shapes it, so Sinhala and Tamil come out right.");
page.caption("A caption: small and quiet.");''',
         py='''page.heading("A heading")
page.text("Body text. It wraps at the page's width, and HarfBuzz shapes it, so Sinhala and Tamil come out right.")
page.caption("A caption: small and quiet.")'''),

    dict(id="button", title="Buttons", h=480, api="zui_button, zui_set_variant, zui_set_enabled",
         blurb="Four variants: primary (the default), tonal, plain and danger. Use one primary button a page at most. A disabled node draws at 40 % opacity and takes no touch.",
         c='''zui_button(page, "Primary", NULL, NULL);
zui_set_variant(zui_button(page, "Tonal", NULL, NULL), ZUI_TONAL);
zui_set_variant(zui_button(page, "Plain", NULL, NULL), ZUI_PLAIN);
zui_set_variant(zui_button(page, "Danger", NULL, NULL), ZUI_DANGER);
zui_set_enabled(zui_button(page, "Disabled", NULL, NULL), false);''',
         cpp='''using zrn::ui::Variant;
page.button("Primary");
page.button("Tonal").set_variant(Variant::Tonal);
page.button("Plain").set_variant(Variant::Plain);
page.button("Danger").set_variant(Variant::Danger);
page.button("Disabled").set_enabled(false);''',
         rs='''use zrnui::Variant;
page.button("Primary");
page.button("Tonal").set_variant(Variant::Tonal);
page.button("Plain").set_variant(Variant::Plain);
page.button("Danger").set_variant(Variant::Danger);
page.button("Disabled").set_enabled(false);''',
         py='''page.button("Primary")
page.button("Tonal", variant=zrnui.TONAL)
page.button("Plain", variant=zrnui.PLAIN)
page.button("Danger", variant=zrnui.DANGER)
page.button("Disabled").enabled = False'''),

    dict(id="item", title="List rows", h=480, api="zui_item, zui_set_detail, zui_set_icon, zui_set_tint",
         blurb="An item is a title, an optional line under it, an optional value on the right and an optional icon. It gets an arrow only when it has a tap handler. Inside a card, dividers come by themselves.",
         ctop='static void row_tapped(zui_node *row, void *data) { zui_toast(zui_node_app(row), "Tapped"); }',
         c='''zui_node *list = zui_section(page, "Rows");
zui_item(list, "Title only", NULL, NULL, NULL);
zui_item(list, "With a second line", "Under the title", NULL, NULL);
zui_item(list, "Goes somewhere", NULL, row_tapped, NULL);
zui_node *wifi = zui_item(list, "Wi-Fi", NULL, row_tapped, NULL);
zui_set_icon(wifi, "wifi");
zui_set_detail(wifi, "Home-5G");
zui_node *tinted = zui_item(list, "Tinted icon", "zrnCoolStyle only", NULL, NULL);
zui_set_icon(tinted, "music");
zui_set_tint(tinted, 0xd9486e);''',
         cpp='''auto list = page.section("Rows");
list.item("Title only");
list.item("With a second line", "Under the title");
list.item("Goes somewhere", "", [&app] { app.toast("Tapped"); });
list.item("Wi-Fi", "", [&app] { app.toast("Tapped"); }).set_icon("wifi").set_detail("Home-5G");
list.item("Tinted icon", "zrnCoolStyle only").set_icon("music").set_tint(0xd9486e);''',
         rs='''let list = page.section("Rows");
list.item("Title only", None);
list.item("With a second line", Some("Under the title"));
list.item("Goes somewhere", None).on_click(move || app.toast("Tapped"));
list.item("Wi-Fi", None).on_click(move || app.toast("Tapped")).set_icon("wifi").set_detail("Home-5G");
list.item("Tinted icon", Some("zrnCoolStyle only")).set_icon("music").set_tint(0xd9486e);''',
         py='''rows = page.section("Rows")
rows.item("Title only")
rows.item("With a second line", "Under the title")
rows.item("Goes somewhere", on_click=lambda: app.toast("Tapped"))
rows.item("Wi-Fi", on_click=lambda: app.toast("Tapped"), icon="wifi", detail="Home-5G")
rows.item("Tinted icon", "zrnCoolStyle only", icon="music", tint=0xd9486e)'''),

    dict(id="switch", title="Switches", h=330, api="zui_switch, zui_get_on, zui_set_on, zui_set_detail",
         blurb="A row with an on/off control. In C the handler reads <code>zui_get_on</code>; the other languages pass the new state. The knob slides over 180 ms. On a switch, <code>set_detail</code> sets its second line. C++ calls it <code>toggle</code> because <code>switch</code> is a keyword.",
         ctop='''static void wifi_changed(zui_node *sw, void *data) {
	zui_set_detail(sw, zui_get_on(sw) ? "Connected" : "Off");
}''',
         c='''zui_node *card = zui_section(page, "Connections");
zui_switch(card, "Wi-Fi", true, wifi_changed, NULL);
zui_switch(card, "Bluetooth", false, NULL, NULL);
zui_set_enabled(zui_switch(card, "Roaming", false, NULL, NULL), false);''',
         cpp='''auto card = page.section("Connections");
auto wifi = card.toggle("Wi-Fi", true);
wifi.on([](zrn::ui::Node sw, int) { sw.set_detail(sw.is_on() ? "Connected" : "Off"); });
card.toggle("Bluetooth", false);
card.toggle("Roaming", false).set_enabled(false);''',
         rs='''let card = page.section("Connections");
let wifi = card.switch("Wi-Fi", true);
wifi.on_change(move |on| { wifi.set_detail(if on { "Connected" } else { "Off" }); });
card.switch("Bluetooth", false);
card.switch("Roaming", false).set_enabled(false);''',
         py='''card = page.section("Connections")
wifi = card.switch("Wi-Fi", True)
wifi.on_event(lambda sw, event: setattr(wifi, "detail", "Connected" if wifi.on else "Off"))
card.switch("Bluetooth", False)
card.switch("Roaming", False).enabled = False'''),

    dict(id="slider", title="Sliders", h=300, api="zui_slider, zui_get_value, zui_event",
         blurb="A value from 0 to 1. <code>CHANGE</code> fires while the finger moves and <code>SUBMIT</code> when it lifts, so save on submit.",
         ctop='''static void level_moved(zui_node *s, void *data) {
	if (zui_event(s) == ZUI_EVENT_SUBMIT) printf("saved %.2f\\n", zui_get_value(s));
}''',
         c='''zui_node *card = zui_section(page, "Display");
zui_slider(card, "Brightness", 0.6, level_moved, NULL);
zui_slider(page, "Outside a card", 0.25, NULL, NULL);''',
         cpp='''auto card = page.section("Display");
card.slider("Brightness", 0.6, [](double v, bool done) { if (done) printf("saved %.2f\\n", v); });
page.slider("Outside a card", 0.25);''',
         rs='''let card = page.section("Display");
card.slider("Brightness", 0.6).on_slide(|v, done| { if done { println!("saved {v:.2}"); } });
page.slider("Outside a card", 0.25);''',
         py='''card = page.section("Display")
card.slider("Brightness", 0.6, on_release=lambda v: print("saved %.2f" % v))
page.slider("Outside a card", 0.25)'''),

    dict(id="progress", title="Progress", h=270, api="zui_progress, zui_set_value",
         blurb="Give it 0 to 1, or a value below 0 when you cannot say how long it will take. The indeterminate bar moves by itself, and the picture is one instant of it.",
         c='''zui_text(page, "Copying 7 of 10");
zui_progress(page, 0.7);
zui_text(page, "No idea how long");
zui_progress(page, -1);''',
         cpp='''page.text("Copying 7 of 10");
page.progress(0.7);
page.text("No idea how long");
page.progress(-1);''',
         rs='''page.text("Copying 7 of 10");
page.progress(0.7);
page.text("No idea how long");
page.progress(-1.0);''',
         py='''page.text("Copying 7 of 10")
page.progress(0.7)
page.text("No idea how long")
page.progress(-1)''', animated=True),

    dict(id="field", title="Text fields", h=300, api="zui_field, zui_get_text, zui_set_text",
         blurb="A box to type into. Tapping it asks the shell for the on-screen keyboard. <code>CHANGE</code> fires per edit and <code>SUBMIT</code> on Enter. There is no password mode or multi-line field in this commit.",
         ctop='''static void search_typed(zui_node *f, void *data) {
	if (zui_event(f) == ZUI_EVENT_SUBMIT) printf("search: %s\\n", zui_get_text(f));
}''',
         c='''zui_field(page, "Search", search_typed, NULL);
zui_set_text(zui_field(page, "Name", NULL, NULL), "Already filled in");''',
         cpp='''page.field("Search", [](const std::string &t, bool submitted) {
	if (submitted) printf("search: %s\\n", t.c_str());
});
page.field("Name").set_text("Already filled in");''',
         rs='''page.field("Search").on_edit(|t, submitted| { if submitted { println!("search: {t}"); } });
page.field("Name").set_text("Already filled in");''',
         py='''page.field("Search", on_submit=lambda t: print("search:", t))
page.field("Name").set_text("Already filled in")'''),

    dict(id="section", title="Sections and cards", h=430, api="zui_section, zui_card",
         blurb="<code>section</code> adds a heading and returns the card under it, so add rows to what it returns. A bare <code>card</code> is the same group with no heading. In Metro cards are flat: the rows just sit on black.",
         c='''zui_item(zui_section(page, "A section"), "In its card", NULL, NULL, NULL);
zui_node *card = zui_card(page);
zui_text(card, "A card with no heading can hold anything.");
zui_button(card, "Like this", NULL, NULL);''',
         cpp='''page.section("A section").item("In its card");
auto card = page.card();
card.text("A card with no heading can hold anything.");
card.button("Like this");''',
         rs='''page.section("A section").item("In its card", None);
let card = page.card();
card.text("A card with no heading can hold anything.");
card.button("Like this");''',
         py='''page.section("A section").item("In its card")
card = page.card()
card.text("A card with no heading can hold anything.")
card.button("Like this")'''),

    dict(id="layout", title="Rows, columns, space", h=380, api="zui_row, zui_column, zui_space, zui_set_flex",
         blurb="A page is already a column. A <code>row</code> sets things side by side, and <code>set_flex</code> shares out the spare width. <code>space</code> adds fixed points. Do not fake layout with space: use sections.",
         c='''zui_node *row = zui_row(page);
zui_set_flex(zui_button(row, "1 share", NULL, NULL), 1);
zui_node *wide = zui_button(row, "2 shares", NULL, NULL);
zui_set_variant(wide, ZUI_TONAL);
zui_set_flex(wide, 2);
zui_space(page, 40);
zui_node *col = zui_column(page);
zui_text(col, "A column keeps things together");
zui_caption(col, "and can be hidden as one.");''',
         cpp='''auto row = page.row();
row.button("1 share").set_flex(1);
row.button("2 shares").set_variant(zrn::ui::Variant::Tonal).set_flex(2);
page.space(40);
auto col = page.column();
col.text("A column keeps things together");
col.caption("and can be hidden as one.");''',
         rs='''let row = page.row();
row.button("1 share").set_flex(1.0);
row.button("2 shares").set_variant(zrnui::Variant::Tonal).set_flex(2.0);
page.space(40.0);
let col = page.column();
col.text("A column keeps things together");
col.caption("and can be hidden as one.");''',
         py='''row = page.row()
row.button("1 share").flex = 1
row.button("2 shares", variant=zrnui.TONAL).flex = 2
page.space(40)
col = page.column()
col.text("A column keeps things together")
col.caption("and can be hidden as one.")'''),

    dict(id="icons", title="Icons", h=1270, api="zui_set_icon", tall=True,
         blurb="Twenty line icons, drawn as strokes, named in <code>libzrnui/src/icons.c</code>. An unknown name draws nothing. Metro draws no icons at all: its rows are words only, as the renders show. There is no call in this commit to supply your own picture on a row.",
         c='''const char *names[] = { %s };
zui_node *card = zui_card(page);
for (size_t i = 0; i < sizeof(names) / sizeof(*names); i++)
	zui_set_icon(zui_item(card, names[i], NULL, NULL, NULL), names[i]);''' % ", ".join('"%s"' % n for n in ICONS),
         cpp='''auto card = page.card();
for (const char *name : { %s })
	card.item(name).set_icon(name);''' % ", ".join('"%s"' % n for n in ICONS),
         rs='''let card = page.card();
for name in [%s] {
    card.item(name, None).set_icon(name);
}''' % ", ".join('"%s"' % n for n in ICONS),
         py='''card = page.card()
for name in [%s]:
    card.item(name, icon=name)''' % ", ".join('"%s"' % n for n in ICONS)),
]

LANGS = {
    "c": "C", "cpp": "C++", "rs": "Rust", "py": "Python",
}


def program_c(els):
    out = ['#include <stdio.h>', '#include <stddef.h>', '#include <zrnui.h>', '']
    for e in els:
        if e.get("ctop"):
            out += [e["ctop"], '']
        body = "\n".join("\t" + l for l in e["c"].splitlines())
        out += ['static void el_%s(zui_app *app, zui_node *page) {' % e["id"], '\t(void)app;', body, '}', '']
    out += ['int main(void) {', '\tzui_app *app = zui_app_new("zrn-sdk-site-proof", "SDK");']
    first = None
    for e in els:
        v = 'p_' + e["id"]
        out.append('\tzui_node *%s = zui_page(app, "%s"); el_%s(app, %s);' % (v, e["title"], e["id"], v))
        first = first or v
    out += ['\treturn zui_run(app, %s);' % first, '}', '']
    return "\n".join(out)


def program_cpp(els):
    out = ['#include <cstdio>', '#include <string>', '#include <zrnui.hpp>', '']
    for e in els:
        body = "\n".join("\t" + l for l in e["cpp"].splitlines())
        out += ['static void el_%s([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {' % e["id"], body, '}', '']
    out += ['int main() {', '\tzrn::ui::App app("zrn-sdk-site-proof", "SDK");']
    first = None
    for e in els:
        v = 'p_' + e["id"]
        out.append('\tauto %s = app.page("%s"); el_%s(app, %s);' % (v, e["title"], e["id"], v))
        first = first or v
    out += ['\treturn app.run(%s);' % first, '}', '']
    return "\n".join(out)


def program_rs(els):
    out = ['#![allow(unused_variables)]', '']
    for e in els:
        body = "\n".join("    " + l for l in e["rs"].splitlines())
        out += ["fn el_%s<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {" % e["id"], body, '}', '']
    out += ['fn main() {', '    let app = zrnui::App::new("zrn-sdk-site-proof", "SDK");']
    first = None
    for e in els:
        v = 'p_' + e["id"]
        out.append('    let %s = app.page("%s"); el_%s(&app, %s);' % (v, e["title"], e["id"], v))
        first = first or v
    out += ['    std::process::exit(app.run(%s));' % first, '}', '']
    return "\n".join(out)


def program_py(els):
    out = ['import zrnui', '']
    for e in els:
        body = "\n".join("    " + l for l in e["py"].splitlines())
        out += ['def el_%s(app, page):' % e["id"], body, '', '']
    out += ['app = zrnui.App("zrn-sdk-site-proof", "SDK")']
    first = None
    for e in els:
        v = 'p_' + e["id"]
        out.append('%s = app.page("%s"); el_%s(app, %s)' % (v, e["title"], e["id"], v))
        first = first or v
    out += ['app.run(%s)' % first, '']
    return "\n".join(out)


# A small live app, for what only exists while an app runs: busy, toast, and a
# page change captured in a real compositor. Driven by `zrn run --headless`.
LIVE_C = r'''#include <stdlib.h>
#include <zrnui.h>
static zui_app *app;
static zui_node *wifi;
static void open_wifi(zui_node *row, void *data) { zui_push(wifi); }
static void toast(void *data) { zui_toast(app, "Saved"); }
static void busy(void *data) { zui_busy(app, true); }
int main(void) {
	app = zui_app_new("zrn-sdk-site-live", "Settings");
	wifi = zui_page(app, "Wi-Fi");
	zui_switch(zui_card(wifi), "Wi-Fi", true, NULL, NULL);
	zui_node *nets = zui_section(wifi, "Networks");
	zui_item(nets, "Home-5G", "Connected", NULL, NULL);
	zui_item(nets, "Cafe", "Open", NULL, NULL);
	zui_item(nets, "Workshop", "Saved", NULL, NULL);
	zui_node *page = zui_page(app, "Settings");
	zui_node *c = zui_section(page, "Connections");
	zui_node *r = zui_item(c, "Wi-Fi", NULL, open_wifi, NULL);
	zui_set_icon(r, "wifi");
	zui_set_detail(r, "Home-5G");
	zui_set_icon(zui_item(c, "Bluetooth", NULL, open_wifi, NULL), "bluetooth");
	zui_set_icon(zui_item(c, "Sounds", NULL, open_wifi, NULL), "volume");
	zui_slider(zui_section(page, "Display"), "Brightness", 0.6, NULL, NULL);
	zui_button(page, "Check for updates", NULL, NULL);
	if (getenv("LIVE_TOAST")) zui_timer(app, 200, false, toast, NULL);
	if (getenv("LIVE_BUSY")) zui_timer(app, 100, false, busy, NULL);
	return zui_run(app, page);
}
'''
