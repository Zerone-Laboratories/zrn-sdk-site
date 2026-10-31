"""Every UI element the site documents, as real code in four languages.

gen/render.py compiles these into four programs, renders each page with
`zrn render`, and compares the four languages pixel by pixel. What the site
shows is what compiled.

Each snippet is the body of a function that has `app` and `page`.
"""

ICONS = ["wifi", "bluetooth", "bell", "moon", "sun", "lock", "volume", "battery",
         "info", "search", "plus", "check", "close", "more", "back", "chevron",
         "music", "person", "gear", "phone", "send"]

ELEMENTS = [
    dict(id="text", title="Text", h=360, api="zui_text, zui_heading, zui_caption",
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
         blurb="Four variants: primary (the default, filled with the accent), tonal and plain (outlined), and danger (a red edge in Metro). Use one primary button a page at most. A disabled node draws at 40 % opacity and takes no touch.",
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

    dict(id="item", title="List rows", h=400, api="zui_item, zui_set_detail, zui_set_icon",
         blurb="An item is a title, an optional line under it, an optional value and an optional icon. In these styles the value is the accent-coloured second line, as ztMETRO's choices are. There is no arrow on a row: a handler makes it tappable, and it tilts under the finger.",
         ctop='static void row_tapped(zui_node *row, void *data) { zui_toast(zui_node_app(row), "Tapped"); }',
         c='''zui_node *list = zui_section(page, "Rows");
zui_item(list, "Title only", NULL, NULL, NULL);
zui_item(list, "With a second line", "Under the title", NULL, NULL);
zui_item(list, "Takes a tap", NULL, row_tapped, NULL);
zui_node *wifi = zui_item(list, "Wi-Fi", NULL, row_tapped, NULL);
zui_set_icon(wifi, "wifi");
zui_set_detail(wifi, "Home-5G");''',
         cpp='''auto list = page.section("Rows");
list.item("Title only");
list.item("With a second line", "Under the title");
list.item("Takes a tap", "", [&app] { app.toast("Tapped"); });
list.item("Wi-Fi", "", [&app] { app.toast("Tapped"); }).set_icon("wifi").set_detail("Home-5G");''',
         rs='''let list = page.section("Rows");
list.item("Title only", None);
list.item("With a second line", Some("Under the title"));
list.item("Takes a tap", None).on_click(move || app.toast("Tapped"));
list.item("Wi-Fi", None).on_click(move || app.toast("Tapped")).set_icon("wifi").set_detail("Home-5G");''',
         py='''rows = page.section("Rows")
rows.item("Title only")
rows.item("With a second line", "Under the title")
rows.item("Takes a tap", on_click=lambda: app.toast("Tapped"))
rows.item("Wi-Fi", on_click=lambda: app.toast("Tapped"), icon="wifi", detail="Home-5G")'''),

    dict(id="switch", title="Switches", h=340, api="zui_switch, zui_get_on, zui_set_on, zui_set_detail",
         blurb="A row with an on/off control, and On or Off as its second line unless you set one. In C the handler reads <code>zui_get_on</code>; the other languages pass the new state. The block slides over 180 ms. <code>set_detail</code> sets the second line. C++ calls it <code>toggle</code> because <code>switch</code> is a keyword.",
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
         blurb="Give it 0 to 1, or a value below 0 when you cannot say how long it will take. Below 0 it shows the dots crossing by themselves, and the picture is one instant of them.",
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
         blurb="A box to type into. Tapping it asks the shell for the on-screen keyboard. The placeholder is the caption above the box; inside a footer it is a hint in the box. <code>CHANGE</code> fires per edit and <code>SUBMIT</code> on Enter. There is no password mode or multi-line field in this commit.",
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
         blurb="<code>section</code> adds a heading and returns the card under it, so add rows to what it returns. A bare <code>card</code> is the same group with no heading. Cards are flat in both styles: the rows just sit on black, with no dividers drawn.",
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

    dict(id="round", title="Round buttons", h=300, api="zui_button, zui_set_icon",
         blurb="A button with an icon becomes a round button with its word under it, as on an app bar. Put them in a row and share the width with flex.",
         c='''zui_node *bar = zui_row(page);
const char *names[] = { "plus", "search", "send", "more" };
for (int i = 0; i < 4; i++) {
	zui_node *b = zui_button(bar, names[i], NULL, NULL);
	zui_set_icon(b, names[i]);
	zui_set_flex(b, 1);
}''',
         cpp='''auto bar = page.row();
for (const char *name : { "plus", "search", "send", "more" })
	bar.button(name).set_icon(name).set_flex(1);''',
         rs='''let bar = page.row();
for name in ["plus", "search", "send", "more"] {
    bar.button(name).set_icon(name).set_flex(1.0);
}''',
         py='''bar = page.row()
for name in ["plus", "search", "send", "more"]:
    b = bar.button(name)
    b.icon = name
    b.flex = 1'''),

    dict(id="picture", title="Pictures", h=560, api="zui_pixmap_load, zui_pixmap_decode, zui_pixmap_rgba, zui_image, zui_set_image, zui_set_monogram, zui_set_badge, zui_set_emphasis, zui_set_radius, zui_set_image_sharp",
         blurb="Decode a JPEG or PNG on any thread with <code>zui_pixmap_load</code> or <code>zui_pixmap_decode</code>, then show it on the UI thread. Nodes keep their own reference, so you may free yours. An item with a picture or a monogram becomes a thread row: a tile, a title, a line, a time and a count. Under DotMatrix a picture is dots of the palette's main colour. The picture here is made in code.",
         c='''static uint8_t px[64 * 64 * 4];
for (int i = 0; i < 64 * 64; i++) {
	px[i * 4] = i % 64 * 4; px[i * 4 + 1] = i / 64 * 4; px[i * 4 + 2] = 200; px[i * 4 + 3] = 255;
}
zui_pixmap *pix = zui_pixmap_rgba(64, 64, px);  /* or zui_pixmap_load("photo.jpg", 1024) */
zui_image(page, pix, 0, 140);                   /* width 0: all there is */
zui_node *card = zui_section(page, "Thread rows");
zui_node *a = zui_item(card, "Ada", "A picture as the tile", NULL, NULL);
zui_set_image(a, pix);
zui_set_detail(a, "09:41");
zui_node *b = zui_item(card, "Ben", "A monogram, a count, unread", NULL, NULL);
zui_set_monogram(b, "B");
zui_set_tint(b, 0xd9486e);
zui_set_badge(b, "3");
zui_set_emphasis(b, true);
zui_pixmap_free(pix);''',
         cpp='''static uint8_t px[64 * 64 * 4];
for (int i = 0; i < 64 * 64; i++) {
	px[i * 4] = i % 64 * 4; px[i * 4 + 1] = i / 64 * 4; px[i * 4 + 2] = 200; px[i * 4 + 3] = 255;
}
zui_pixmap *pix = zui_pixmap_rgba(64, 64, px);  // or zui_pixmap_load("photo.jpg", 1024)
page.image(pix, 0, 140);
auto card = page.section("Thread rows");
card.item("Ada", "A picture as the tile").set_image(pix).set_detail("09:41");
card.item("Ben", "A monogram, a count, unread").set_monogram("B").set_tint(0xd9486e)
	.set_badge("3").set_emphasis(true);
zui_pixmap_free(pix);'''),

    dict(id="list", title="Long lists", h=560, api="zui_list, zui_list_append, zui_list_prepend, zui_list_refresh, zui_list_set_count, zui_page_scroll_end, zui_page_at_end",
         blurb="Thousands of rows of differing heights. <code>bind</code> fills a row when it comes near the screen, and <code>height</code> is only a guess, corrected once the row is made. The list must be the last thing in its page or tab. Its handler gets <code>CHANGE</code> near the start, which is your chance to <code>zui_list_prepend</code> older rows and then <code>zui_list_allow_more</code>. <code>zui_page_scroll_end</code> keeps a chat at its end as it grows.",
         ctop='''static double row_height(int row, void *data) { return 66; }
static void row_bind(int row, zui_node *node, void *data) {
	char title[32];
	snprintf(title, sizeof(title), "Row %d", row + 1);
	zui_item(node, title, row % 3 ? "Made when it came near" : "Of 5000", NULL, NULL);
}''',
         c='''zui_list(page, 5000, row_height, row_bind, NULL);''',
         cpp='''page.list(5000, [](int) { return 66.0; }, [](int row, zrn::ui::Node node) {
	node.item("Row " + std::to_string(row + 1), row % 3 ? "Made when it came near" : "Of 5000");
});'''),

    dict(id="pivot", title="Pivots", h=520, api="zui_tabs, zui_tab, zui_tabs_select, zui_tabs_current",
         blurb="Tabs under the app's name that swipe. The tab in front has its title white and the next ones run grey off the edge. Each tab is a column with its own scroll place, and the handler of the tabs gets <code>CHANGE</code> when the tab changes.",
         c='''zui_node *tabs = zui_tabs(page);
zui_node *one = zui_tab(tabs, "chats");
zui_item(one, "Ada", "See you soon", NULL, NULL);
zui_item(one, "Ben", "Thanks", NULL, NULL);
zui_item(zui_tab(tabs, "status"), "Nothing yet", NULL, NULL, NULL);
zui_item(zui_tab(tabs, "starred"), "Nothing yet", NULL, NULL, NULL);''',
         cpp='''auto tabs = page.tabs();
auto one = tabs.tab("chats");
one.item("Ada", "See you soon");
one.item("Ben", "Thanks");
tabs.tab("status").item("Nothing yet");
tabs.tab("starred").item("Nothing yet");'''),

    dict(id="bubble", title="Bubbles and compact titles", h=460, api="zui_bubble, zui_page_set_compact, zui_set_subtitle, zui_set_align",
         blurb="A speech bubble is as wide as what is in it, and sits on the end if it is yours. A compact page shows its title as given and smaller, with a line under it, for a person's name. <code>zui_set_align</code> sets text to start (0), end (1) or centre (2).",
         c='''zui_page_set_compact(page, true);
zui_set_subtitle(page, "Last seen today");
zui_node *in = zui_bubble(page, false);
zui_text(in, "Are you coming tonight?");
zui_caption(in, "18:02");
zui_node *me = zui_bubble(page, true);
zui_text(me, "Yes, on my way");
zui_caption(me, "18:03");''',
         cpp='''page.set_compact(true);
page.set_subtitle("Last seen today");
auto in = page.bubble(false);
in.text("Are you coming tonight?");
in.caption("18:02");
auto me = page.bubble(true);
me.text("Yes, on my way");
me.caption("18:03");'''),

    dict(id="footer", title="Footer", h=500, api="zui_footer",
         blurb="A row fixed at the bottom of a page, over its list. A field in it shows its hint inside the box, and asks the shell to lift the window with the keyboard.",
         c='''zui_text(page, "The page scrolls under the bar.");
zui_node *bar = zui_footer(page);
zui_node *field = zui_field(bar, "Type a message", NULL, NULL);
zui_set_flex(field, 1);
zui_button(bar, "Send", NULL, NULL);''',
         cpp='''page.text("The page scrolls under the bar.");
auto bar = page.footer();
bar.field("Type a message").set_flex(1);
bar.button("Send");'''),

    dict(id="icons", title="Icons", h=700, api="zui_set_icon", grid=True, scale=3,
         blurb="Twenty-one icons by name. <b>In Metro these are Segoe MDL2 Assets glyphs from the system's font</b>, the same font the phone has; the site does not host it. Under DotMatrix, or on a system without the font, libzrnui draws its own strokes instead, which land on the lattice as dots. An unknown name draws nothing. You cannot supply your own icon file: use a picture.",
         c='''const char *names[] = { %s };
for (int i = 0; i < 21; i += 4) {
	zui_node *row = zui_row(page);
	for (int k = i; k < i + 4 && k < 21; k++) {
		zui_node *b = zui_button(row, names[k], NULL, NULL);
		zui_set_icon(b, names[k]);
		zui_set_flex(b, 1);
	}
}''' % ", ".join('"%s"' % n for n in ICONS),
         cpp='''const char *names[] = { %s };
for (int i = 0; i < 21; i += 4) {
	auto row = page.row();
	for (int k = i; k < i + 4 && k < 21; k++)
		row.button(names[k]).set_icon(names[k]).set_flex(1);
}''' % ", ".join('"%s"' % n for n in ICONS),
         rs='''for names in [%s].chunks(4) {
    let row = page.row();
    for name in names {
        row.button(name).set_icon(name).set_flex(1.0);
    }
}''' % ", ".join('"%s"' % n for n in ICONS),
         py='''names = [%s]
for i in range(0, 21, 4):
    row = page.row()
    for name in names[i:i + 4]:
        b = row.button(name)
        b.icon = name
        b.flex = 1''' % ", ".join('"%s"' % n for n in ICONS)),
]

LANGS = {
    "c": "C", "cpp": "C++", "rs": "Rust", "py": "Python",
}


def program_c(els):
    out = ['#include <stdio.h>', '#include <stdint.h>', '#include <stddef.h>', '#include <zrnui.h>', '']
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
    out = ['#include <cstdio>', '#include <cstdint>', '#include <string>', '#include <zrnui.hpp>', '']
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
    els = [e for e in els if "rs" in e]
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
    els = [e for e in els if "py" in e]
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
