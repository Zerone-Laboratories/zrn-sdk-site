#include <stdio.h>
#include <stddef.h>
#include <zrnui.h>

static void el_text(zui_app *app, zui_node *page) {
	(void)app;
	zui_heading(page, "A heading");
	zui_text(page, "Body text. It wraps at the page's width, and HarfBuzz shapes it, so Sinhala and Tamil come out right.");
	zui_caption(page, "A caption: small and quiet.");
}

static void el_button(zui_app *app, zui_node *page) {
	(void)app;
	zui_button(page, "Primary", NULL, NULL);
	zui_set_variant(zui_button(page, "Tonal", NULL, NULL), ZUI_TONAL);
	zui_set_variant(zui_button(page, "Plain", NULL, NULL), ZUI_PLAIN);
	zui_set_variant(zui_button(page, "Danger", NULL, NULL), ZUI_DANGER);
	zui_set_enabled(zui_button(page, "Disabled", NULL, NULL), false);
}

static void row_tapped(zui_node *row, void *data) { zui_toast(zui_node_app(row), "Tapped"); }

static void el_item(zui_app *app, zui_node *page) {
	(void)app;
	zui_node *list = zui_section(page, "Rows");
	zui_item(list, "Title only", NULL, NULL, NULL);
	zui_item(list, "With a second line", "Under the title", NULL, NULL);
	zui_item(list, "Goes somewhere", NULL, row_tapped, NULL);
	zui_node *wifi = zui_item(list, "Wi-Fi", NULL, row_tapped, NULL);
	zui_set_icon(wifi, "wifi");
	zui_set_detail(wifi, "Home-5G");
	zui_node *tinted = zui_item(list, "Tinted icon", "zrnCoolStyle only", NULL, NULL);
	zui_set_icon(tinted, "music");
	zui_set_tint(tinted, 0xd9486e);
}

static void wifi_changed(zui_node *sw, void *data) {
	zui_set_detail(sw, zui_get_on(sw) ? "Connected" : "Off");
}

static void el_switch(zui_app *app, zui_node *page) {
	(void)app;
	zui_node *card = zui_section(page, "Connections");
	zui_switch(card, "Wi-Fi", true, wifi_changed, NULL);
	zui_switch(card, "Bluetooth", false, NULL, NULL);
	zui_set_enabled(zui_switch(card, "Roaming", false, NULL, NULL), false);
}

static void level_moved(zui_node *s, void *data) {
	if (zui_event(s) == ZUI_EVENT_SUBMIT) printf("saved %.2f\n", zui_get_value(s));
}

static void el_slider(zui_app *app, zui_node *page) {
	(void)app;
	zui_node *card = zui_section(page, "Display");
	zui_slider(card, "Brightness", 0.6, level_moved, NULL);
	zui_slider(page, "Outside a card", 0.25, NULL, NULL);
}

static void el_progress(zui_app *app, zui_node *page) {
	(void)app;
	zui_text(page, "Copying 7 of 10");
	zui_progress(page, 0.7);
	zui_text(page, "No idea how long");
	zui_progress(page, -1);
}

static void search_typed(zui_node *f, void *data) {
	if (zui_event(f) == ZUI_EVENT_SUBMIT) printf("search: %s\n", zui_get_text(f));
}

static void el_field(zui_app *app, zui_node *page) {
	(void)app;
	zui_field(page, "Search", search_typed, NULL);
	zui_set_text(zui_field(page, "Name", NULL, NULL), "Already filled in");
}

static void el_section(zui_app *app, zui_node *page) {
	(void)app;
	zui_item(zui_section(page, "A section"), "In its card", NULL, NULL, NULL);
	zui_node *card = zui_card(page);
	zui_text(card, "A card with no heading can hold anything.");
	zui_button(card, "Like this", NULL, NULL);
}

static void el_layout(zui_app *app, zui_node *page) {
	(void)app;
	zui_node *row = zui_row(page);
	zui_set_flex(zui_button(row, "1 share", NULL, NULL), 1);
	zui_node *wide = zui_button(row, "2 shares", NULL, NULL);
	zui_set_variant(wide, ZUI_TONAL);
	zui_set_flex(wide, 2);
	zui_space(page, 40);
	zui_node *col = zui_column(page);
	zui_text(col, "A column keeps things together");
	zui_caption(col, "and can be hidden as one.");
}

static void el_icons(zui_app *app, zui_node *page) {
	(void)app;
	const char *names[] = { "wifi", "bluetooth", "bell", "moon", "sun", "lock", "volume", "battery", "info", "search", "plus", "check", "close", "more", "back", "chevron", "music", "person", "gear", "phone" };
	zui_node *card = zui_card(page);
	for (size_t i = 0; i < sizeof(names) / sizeof(*names); i++)
		zui_set_icon(zui_item(card, names[i], NULL, NULL, NULL), names[i]);
}

int main(void) {
	zui_app *app = zui_app_new("zrn-sdk-site-proof", "SDK");
	zui_node *p_text = zui_page(app, "Text"); el_text(app, p_text);
	zui_node *p_button = zui_page(app, "Buttons"); el_button(app, p_button);
	zui_node *p_item = zui_page(app, "List rows"); el_item(app, p_item);
	zui_node *p_switch = zui_page(app, "Switches"); el_switch(app, p_switch);
	zui_node *p_slider = zui_page(app, "Sliders"); el_slider(app, p_slider);
	zui_node *p_progress = zui_page(app, "Progress"); el_progress(app, p_progress);
	zui_node *p_field = zui_page(app, "Text fields"); el_field(app, p_field);
	zui_node *p_section = zui_page(app, "Sections and cards"); el_section(app, p_section);
	zui_node *p_layout = zui_page(app, "Rows, columns, space"); el_layout(app, p_layout);
	zui_node *p_icons = zui_page(app, "Icons"); el_icons(app, p_icons);
	return zui_run(app, p_text);
}
