"""Every UI element the site documents, as real C against zrnui (SDK v2).

gen/render.py puts each snippet into a small program, compiles it against
zrnui, draws it with zrnui's GLES2 renderer offscreen (Mesa, surfaceless
EGL) in Dark and in Light, crops it to the content, and saves the pictures. What the site shows is what compiled.

Each snippet is the body of

    static void build(Zid root, Zid page, Zid stack)

where `page` is a Page and `stack` is a vertical StackPanel that is already
the page's content, with the margin 19, 32, 19, 0. A snippet may replace the
page's content (a Pivot, a Hub). `h` is the height of the picture in logical
pixels before the crop; the width is 360 points, the S9's
logical width under the ztOS shell (1440 px at scale 4).
"""

ELEMENTS = [
    dict(id="text", title="Text", h=420,
         api="Ztext_block_create, Ztext_block_set_style, Ztext_block_set_text_wrapping",
         blurb="A TextBlock is one run of text. The styles are the ones of Windows Phone 8.1: <code>Z_TEXT_STYLE_TITLE</code>, <code>_BODY</code>, the <code>Z_TEXT_STYLE_PHONE_*</code> set and more. Wrapping is off until you turn it on.",
         c='''const Zid title = Ztext_block_create("settings");
Ztext_block_set_style(title, Z_TEXT_STYLE_PHONE_TITLE1);
Zpanel_add(stack, title);

const Zid body = Ztext_block_create("Body text wraps at the width of its parent when wrapping is on.");
Ztext_block_set_style(body, Z_TEXT_STYLE_BODY);
Ztext_block_set_text_wrapping(body, Z_WRAP);
Zpanel_add(stack, body);

const Zid subtle = Ztext_block_create("A subtle line");
Ztext_block_set_style(subtle, Z_TEXT_STYLE_PHONE_SUBTLE);
Zpanel_add(stack, subtle);

const Zid accent = Ztext_block_create("In the accent colour");
Ztext_block_set_style(accent, Z_TEXT_STYLE_PHONE_ACCENT);
Zpanel_add(stack, accent);'''),

    dict(id="button", title="Buttons", h=360,
         api="Zbutton_create, Zbutton_on_click, Zhyperlink_button_create, Zelement_set_enabled",
         blurb="A Button is a white-edged rectangle. It fills with the accent while pressed. A HyperlinkButton is text in the accent colour. Both raise Click.",
         ctop='static void clicked(const Zid sender, void* const user_data) { (void)sender; (void)user_data; }',
         c='''const Zid ok = Zbutton_create("save");
Zbutton_on_click(ok, clicked, nullptr);
Zpanel_add(stack, ok);

const Zid off = Zbutton_create("disabled");
Zelement_set_enabled(off, false);
Zpanel_add(stack, off);

const Zid link = Zhyperlink_button_create("open the website");
Zhyperlink_button_set_uri(link, "https://ztos.online");
Zpanel_add(stack, link);'''),

    dict(id="toggles", title="Check boxes and radio buttons", h=380,
         api="Zcheck_box_create, Zradio_button_create, Ztoggle_button_create, Ztoggle_button_set_is_checked",
         blurb="CheckBox, RadioButton and ToggleButton share the ToggleButton calls. Radio buttons with the same group name exclude each other.",
         c='''const Zid wifi = Zcheck_box_create("Wi-Fi");
Ztoggle_button_set_is_checked(wifi, true);
Zpanel_add(stack, wifi);
Zpanel_add(stack, Zcheck_box_create("Bluetooth"));

const Zid dark = Zradio_button_create("dark", "theme");
Ztoggle_button_set_is_checked(dark, true);
Zpanel_add(stack, dark);
Zpanel_add(stack, Zradio_button_create("light", "theme"));

const Zid bold = Ztoggle_button_create("bold");
Ztoggle_button_set_is_checked(bold, true);
Zpanel_add(stack, bold);'''),

    dict(id="switch", title="Toggle switch", h=260,
         api="Ztoggle_switch_create, Ztoggle_switch_set_header, Ztoggle_switch_set_is_on, Ztoggle_switch_on_toggled",
         blurb="A header, the On or Off text, and the switch at the right. The knob slides for 180 ms when animations run.",
         c='''const Zid on = Ztoggle_switch_create();
Ztoggle_switch_set_header(on, "Location");
Ztoggle_switch_set_is_on(on, true);
Zpanel_add(stack, on);

const Zid off = Ztoggle_switch_create();
Ztoggle_switch_set_header(off, "Airplane mode");
Zpanel_add(stack, off);'''),

    dict(id="range", title="Slider and progress", h=380,
         api="Zslider_create, Zrange_base_set_range, Zrange_base_set_value, Zprogress_bar_create, Zprogress_ring_create",
         blurb="Slider and ProgressBar are RangeBase controls: a minimum, a maximum and a value. A ProgressBar can be indeterminate, and a ProgressRing spins while it is active. The moving dots only move with <code>Zroot_tick</code>.",
         c='''const Zid volume = Zslider_create(Z_HORIZONTAL);
Zslider_set_header(volume, "Ringer volume");
Zrange_base_set_range(volume, 0, 10);
Zrange_base_set_value(volume, 6);
Zpanel_add(stack, volume);

const Zid bar = Zprogress_bar_create();
Zrange_base_set_value(bar, 40);
Zpanel_add(stack, bar);

const Zid ring = Zprogress_ring_create();
Zprogress_ring_set_is_active(ring, true);
Zpanel_add(stack, ring);'''),

    dict(id="input", title="Text input", h=420,
         api="Ztext_box_create, Ztext_box_set_header, Ztext_box_set_placeholder_text, Zpassword_box_create",
         blurb="A TextBox takes text from the keyboard through <code>Zroot_inject_text</code>. A PasswordBox shows dots. Both have a header and a placeholder. AutoSuggestBox adds a list of suggestions.",
         c='''const Zid name = Ztext_box_create("");
Ztext_box_set_header(name, "Name");
Ztext_box_set_placeholder_text(name, "your name");
Zpanel_add(stack, name);

const Zid city = Ztext_box_create("London");
Ztext_box_set_header(city, "City");
Zpanel_add(stack, city);

const Zid pass = Zpassword_box_create();
Zpassword_box_set_header(pass, "Password");
Zpassword_box_set_password(pass, "secret");
Zpanel_add(stack, pass);'''),

    dict(id="list", title="List view", h=460,
         api="Zlist_view_create, Zlist_view_item_create, Zitems_control_add, Zlist_view_add_group_header",
         blurb="A ListView shows its items in a ScrollViewer. Items tilt under the finger. Group headers split the list. A GridView does the same in a grid.",
         ctop='''static void add_row(const Zid list, const char* const name) {
	const Zid row = Zlist_view_item_create(nullptr);
	const Zid text = Ztext_block_create(name);
	Ztext_block_set_style(text, Z_TEXT_STYLE_PHONE_EXTRA_LARGE);
	Zcontent_control_set_content(row, text);
	Zitems_control_add(list, row);
}''',
         c='''const Zid list = Zlist_view_create();
Zlist_view_add_group_header(list, "a");
add_row(list, "Alice");
add_row(list, "Amy");
Zlist_view_add_group_header(list, "b");
add_row(list, "Ben");
add_row(list, "Bob");
Zelement_set_height(list, 400);
Zpanel_add(stack, list);'''),

    dict(id="combo", title="Combo box", h=260,
         api="Zcombo_box_create, Zcombo_box_set_header, Zitems_control_add_text, Zselector_set_selected_index",
         blurb="A header over the chosen item. A tap opens the list in place, or a full-screen picker when there are many items.",
         c='''const Zid level = Zcombo_box_create();
Zcombo_box_set_header(level, "Brightness");
Zitems_control_add_text(level, "low");
Zitems_control_add_text(level, "medium");
Zitems_control_add_text(level, "high");
Zselector_set_selected_index(level, 1);
Zpanel_add(stack, level);'''),

    dict(id="pickers", title="Date and time pickers", h=300,
         api="Zdate_picker_create, Zdate_picker_set_date, Ztime_picker_create, Ztime_picker_set_time",
         blurb="A header over a button with the value. A tap shows a full-screen flyout of looping selectors, with done and cancel.",
         c='''const Zid date = Zdate_picker_create();
Zdate_picker_set_header(date, "Date");
Zdate_picker_set_date(date, (ZDate){ 2026, 11, 20 });
Zpanel_add(stack, date);

const Zid time = Ztime_picker_create();
Ztime_picker_set_header(time, "Alarm");
Ztime_picker_set_time(time, (ZTimeOfDay){ 7, 30 });
Zpanel_add(stack, time);'''),

    dict(id="pivot", title="Pivot", h=300, crop=False,
         api="Zpivot_create, Zpivot_set_title, Zpivot_item_create, Zpivot_add_item",
         blurb="A title over a strip of big headers, with one page under each. A finger drags pages and headers together. The slide takes 300 ms with animations.",
         c='''const Zid pivot = Zpivot_create();
Zpivot_set_title(pivot, "SETTINGS");

const Zid sound = Zpivot_item_create("sound");
const Zid ring = Ztoggle_switch_create();
Ztoggle_switch_set_header(ring, "Vibrate");
Zcontent_control_set_content(sound, ring);
Zpivot_add_item(pivot, sound);

const Zid display = Zpivot_item_create("display");
Zcontent_control_set_text(display, "Brightness and colour");
Zpivot_add_item(pivot, display);

Zpage_set_content(page, pivot);'''),

    dict(id="hub", title="Hub", h=420,
         api="Zhub_create, Zhub_set_header, Zhub_section_create, Zhub_add_section",
         blurb="A big header over sections side by side. Sections scroll sideways with the finger. The header moves at half their speed.",
         c='''const Zid hub = Zhub_create();
Zhub_set_header(hub, "music");

const Zid recent = Zhub_section_create("recent");
const Zid lines = Zstack_panel_create(Z_VERTICAL);
const Zid a = Ztext_block_create("Morning");
Ztext_block_set_style(a, Z_TEXT_STYLE_PHONE_TITLE2);
Zpanel_add(lines, a);
const Zid b = Ztext_block_create("Drive home");
Ztext_block_set_style(b, Z_TEXT_STYLE_PHONE_TITLE2);
Zpanel_add(lines, b);
Zcontent_control_set_content(recent, lines);
Zhub_add_section(hub, recent);

const Zid albums = Zhub_section_create("albums");
Zcontent_control_set_text(albums, "12 albums");
Zhub_add_section(hub, albums);

Zpage_set_content(page, hub);'''),

    dict(id="appbar", title="App bar", h=300, crop=False,
         api="Zcommand_bar_create, Zapp_bar_button_create, Zsymbol_icon_create, Zcommand_bar_add_primary_command, Zpage_set_bottom_app_bar",
         blurb="A CommandBar at the bottom of a page: round icon buttons, and a menu of secondary commands behind the three dots. Open, it grows over the page in 167 ms.",
         c='''const Zid bar = Zcommand_bar_create();
Zcommand_bar_add_primary_command(bar, Zapp_bar_button_create("add", Zsymbol_icon_create(Z_SYMBOL_ADD)));
Zcommand_bar_add_primary_command(bar, Zapp_bar_button_create("edit", Zsymbol_icon_create(Z_SYMBOL_EDIT)));
Zcommand_bar_add_primary_command(bar, Zapp_bar_button_create("delete", Zsymbol_icon_create(Z_SYMBOL_DELETE)));
Zcommand_bar_add_secondary_command(bar, Zapp_bar_button_create("settings", Z_INVALID_ID));
Zpage_set_bottom_app_bar(page, bar);

const Zid title = Ztext_block_create("notes");
Ztext_block_set_style(title, Z_TEXT_STYLE_PHONE_TITLE1);
Zpanel_add(stack, title);'''),

    dict(id="dialog", title="Content dialog", h=300, crop=False,
         api="Zcontent_dialog_create, Zcontent_dialog_set_title, Zcontent_dialog_set_primary_button_text, Zcontent_dialog_show",
         blurb="A dialog at the top of the screen with up to two buttons. What is under it is dimmed and takes no input. Back closes it. There is no await in C: the result comes to a callback.",
         ctop='static void done(const Zid dialog, const ZContentDialogResult result, void* const user_data) { (void)dialog; (void)result; (void)user_data; }',
         c='''const Zid text = Ztext_block_create("A page under the dialog");
Ztext_block_set_style(text, Z_TEXT_STYLE_BODY);
Zpanel_add(stack, text);

const Zid dialog = Zcontent_dialog_create();
Zcontent_dialog_set_title(dialog, "Delete this note?");
Zcontent_control_set_text(dialog, "It will be gone from every device.");
Zcontent_dialog_set_primary_button_text(dialog, "delete");
Zcontent_dialog_set_secondary_button_text(dialog, "cancel");
Zcontent_dialog_show(dialog, root, done, nullptr);'''),

    dict(id="layout", title="Grid and border", h=300,
         api="Zgrid_create, Zgrid_add_column, Zgrid_place, Zborder_create, Zborder_set_child",
         blurb="Layout is the one of XAML: measure, then arrange. A Grid has Auto, pixel and star rows and columns. A Border draws a background and an edge around one child.",
         c='''const Zid grid = Zgrid_create();
Zgrid_add_column(grid, Z_GRID_STAR, 1);
Zgrid_add_column(grid, Z_GRID_STAR, 1);
Zgrid_add_row(grid, Z_GRID_PIXEL, 100);

const Zid left = Zborder_create();
Zborder_bind_background(left, Z_RES_PHONE_ACCENT_BRUSH);
Zborder_set_child(left, Ztext_block_create("one star"));
Zgrid_place(grid, left, 0, 0);

const Zid right = Zborder_create();
Zborder_set_border_thickness(right, Zthickness_uniform(2));
Zborder_bind_border_brush(right, Z_RES_PHONE_FOREGROUND_BRUSH);
Zborder_set_child(right, Ztext_block_create("one star"));
Zgrid_place(grid, right, 1, 0);

Zpanel_add(stack, grid);'''),
]


def program_c(e, theme):
    """A whole program that draws one element in one theme and writes a PNG."""
    return '''#include <stdio.h>
#include <stdint.h>
#include <zrnui/controls.h>
#include <zrnui/host.h>
#include <zrnui/platform.h>
#include "writepng.h"

%s

static void build(const Zid root, const Zid page, const Zid stack) {
	(void)root; (void)page; (void)stack;
%s
}

int main(int argc, char** argv) {
	if (argc < 2 || !Zinit()) return 1;
	const Zid root = Zroot_create();
	Zroot_set_renderer(root, Z_RENDERER_GPU);
	Zroot_set_animations(root, Z_ANIMATIONS_OFF);
	Zroot_set_theme(root, %s);
	/* the S9 as ztOS lays an app out: 360 points across, drawn here at 3 device pixels a point */
	Zroot_set_size(root, 360, %d);
	Zroot_set_density(root, 3.0f);
	const Zid page = Zpage_create();
	const Zid stack = Zstack_panel_create(Z_VERTICAL);
	Zelement_set_margin(stack, Zthickness(19, 32, 19, 0));
	Zpage_set_content(page, stack);
	Zroot_set_visual(root, page);
	build(root, page, stack);
	for (int i = 0; i < 60; i++) Zroot_tick(root, 16);
	ZFrame frame = {0};
	Zroot_render(root, &frame);
	const int ok = write_png(argv[1], frame.pixels, frame.width, frame.height, frame.stride);
	fprintf(stderr, "renderer %%s, %%dx%%d\\n", Zroot_get_renderer_name(root), frame.width, frame.height);
	Zroot_destroy(root);
	Zshutdown();
	return ok ? 0 : 1;
}
''' % (e.get("ctop", ""), "\n".join("\t" + l for l in e["c"].splitlines()), theme, e["h"])
