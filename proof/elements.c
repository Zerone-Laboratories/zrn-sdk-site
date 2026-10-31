#include <stdio.h>
#include <stdint.h>
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
	zui_item(list, "Takes a tap", NULL, row_tapped, NULL);
	zui_node *wifi = zui_item(list, "Wi-Fi", NULL, row_tapped, NULL);
	zui_set_icon(wifi, "wifi");
	zui_set_detail(wifi, "Home-5G");
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

static void el_round(zui_app *app, zui_node *page) {
	(void)app;
	zui_node *bar = zui_row(page);
	const char *names[] = { "plus", "search", "send", "more" };
	for (int i = 0; i < 4; i++) {
		zui_node *b = zui_button(bar, names[i], NULL, NULL);
		zui_set_icon(b, names[i]);
		zui_set_flex(b, 1);
	}
}

static void el_picture(zui_app *app, zui_node *page) {
	(void)app;
	static uint8_t px[64 * 64 * 4];
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
	zui_pixmap_free(pix);
}

static double row_height(int row, void *data) { return 66; }
static void row_bind(int row, zui_node *node, void *data) {
	char title[32];
	snprintf(title, sizeof(title), "Row %d", row + 1);
	zui_item(node, title, row % 3 ? "Made when it came near" : "Of 5000", NULL, NULL);
}

static void el_list(zui_app *app, zui_node *page) {
	(void)app;
	zui_list(page, 5000, row_height, row_bind, NULL);
}

static void el_pivot(zui_app *app, zui_node *page) {
	(void)app;
	zui_node *tabs = zui_tabs(page);
	zui_node *one = zui_tab(tabs, "chats");
	zui_item(one, "Ada", "See you soon", NULL, NULL);
	zui_item(one, "Ben", "Thanks", NULL, NULL);
	zui_item(zui_tab(tabs, "status"), "Nothing yet", NULL, NULL, NULL);
	zui_item(zui_tab(tabs, "starred"), "Nothing yet", NULL, NULL, NULL);
}

static void el_bubble(zui_app *app, zui_node *page) {
	(void)app;
	zui_page_set_compact(page, true);
	zui_set_subtitle(page, "Last seen today");
	zui_node *in = zui_bubble(page, false);
	zui_text(in, "Are you coming tonight?");
	zui_caption(in, "18:02");
	zui_node *me = zui_bubble(page, true);
	zui_text(me, "Yes, on my way");
	zui_caption(me, "18:03");
}

static void el_footer(zui_app *app, zui_node *page) {
	(void)app;
	zui_text(page, "The page scrolls under the bar.");
	zui_node *bar = zui_footer(page);
	zui_node *field = zui_field(bar, "Type a message", NULL, NULL);
	zui_set_flex(field, 1);
	zui_button(bar, "Send", NULL, NULL);
}

static void el_icons(zui_app *app, zui_node *page) {
	(void)app;
	const char *names[] = { "wifi", "bluetooth", "bell", "moon", "sun", "lock", "volume", "battery", "info", "search", "plus", "check", "close", "more", "back", "chevron", "music", "person", "gear", "phone", "send" };
	for (int i = 0; i < 21; i += 4) {
		zui_node *row = zui_row(page);
		for (int k = i; k < i + 4 && k < 21; k++) {
			zui_node *b = zui_button(row, names[k], NULL, NULL);
			zui_set_icon(b, names[k]);
			zui_set_flex(b, 1);
		}
	}
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
	zui_node *p_section = zui_page(app, "Sections"); el_section(app, p_section);
	zui_node *p_layout = zui_page(app, "Rows"); el_layout(app, p_layout);
	zui_node *p_round = zui_page(app, "Round"); el_round(app, p_round);
	zui_node *p_picture = zui_page(app, "Pictures"); el_picture(app, p_picture);
	zui_node *p_list = zui_page(app, "Long lists"); el_list(app, p_list);
	zui_node *p_pivot = zui_page(app, "Pivots"); el_pivot(app, p_pivot);
	zui_node *p_bubble = zui_page(app, "Ada Lane"); el_bubble(app, p_bubble);
	zui_node *p_footer = zui_page(app, "Footer"); el_footer(app, p_footer);
	zui_node *p_icons = zui_page(app, "Icons"); el_icons(app, p_icons);
	return zui_run(app, p_text);
}
