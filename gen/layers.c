/*
 * The layers of a ztMETRO frame, one picture each, for "How the shell draws".
 *
 *   layers OUT_DIR <dark|light>
 *
 * Writes OUT_DIR/<layer>-<theme>.png, each 360 x 640 points at 3 device pixels
 * a point (the S9 as ztOS lays it out), drawn by zrnui's GLES2 renderer
 * offscreen (Mesa, surfaceless EGL). Every layer is built from zrnui elements
 * at the place and size ztmetro gives it (STATUS_H 28, NAV_BAR_H 40,
 * TOAST_H 58 points). Each layer is drawn twice, over black and over white
 * (<layer>-<theme>-b.png, -w.png): gen/layers.py takes its coverage from the
 * difference, so the parts of the screen it does not cover are transparent. Demo content only: made-up
 * names, generic tiles, no screenshots.
 *
 * These are pictures of the shell's layers drawn with the SDK's controls, not
 * the shell's own Cairo code: the shell is not in this repository.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <zrnui/controls.h>
#include <zrnui/host.h>
#include <zrnui/platform.h>
#include "writepng.h"

enum { W = 360, H = 640, STATUS = 28, NAV = 40, TOAST = 58 };
static bool light;
static const uint32_t ACCENT = 0xFF0050EF;	/* Cobalt, the default accent */

static uint32_t fg(void) { return light ? 0xFF000000 : 0xFFFFFFFF; }
static uint32_t bg(void) { return light ? 0xFFFFFFFF : 0xFF000000; }
static uint32_t chrome(void) { return light ? 0xFFDDDDDD : 0xFF1F1F1F; }

static Zid text(const char* s, const float size, const ZFontFamily face, const uint32_t color) {
	const Zid t = Ztext_block_create(s);
	Ztext_block_set_font_size(t, size);
	Ztext_block_set_font_family(t, face);
	Ztext_block_set_foreground(t, Zcolor_argb(color));
	return t;
}

static Zid box(const float w, const float h, const uint32_t color) {
	const Zid b = Zborder_create();
	Zelement_set_width(b, w);
	Zelement_set_height(b, h);
	Zborder_set_background(b, Zcolor_argb(color));
	return b;
}

static Zid symbol(const ZSymbol s, const float size, const uint32_t color) {
	const Zid i = Zsymbol_icon_create(s);
	Zelement_set_width(i, size);
	Zelement_set_height(i, size);
	Zicon_element_set_foreground(i, Zcolor_argb(color));
	return i;
}

/* a text centred in a box */
static Zid label_box(const float w, const float h, const uint32_t color, const char* s, const float size, const uint32_t ink) {
	const Zid b = box(w, h, color);
	const Zid t = text(s, size, Z_FONT_NORMAL, ink);
	Zelement_set_horizontal_alignment(t, Z_HALIGN_CENTER);
	Zelement_set_vertical_alignment(t, Z_VALIGN_CENTER);
	Zborder_set_child(b, t);
	return b;
}

/* a tile: colour, a label in its lower left corner */
static void tile(const Zid c, const float x, const float y, const float w, const float h, const uint32_t color, const char* name, const ZSymbol icon) {
	const Zid b = box(w, h, color);
	const Zid g = Zgrid_create();
	Zgrid_add_row(g, Z_GRID_STAR, 1);
	if (icon) {
		const Zid i = symbol(icon, h > 100 ? 44 : 30, 0xFFFFFFFF);
		Zelement_set_horizontal_alignment(i, Z_HALIGN_CENTER);
		Zelement_set_vertical_alignment(i, Z_VALIGN_CENTER);
		Zgrid_place(g, i, 0, 0);
	}
	if (name) {
		const Zid t = text(name, 13, Z_FONT_NORMAL, 0xFFFFFFFF);
		Zelement_set_vertical_alignment(t, Z_VALIGN_BOTTOM);
		Zelement_set_margin(t, Zthickness(8, 0, 0, 5));
		Zgrid_place(g, t, 0, 0);
	}
	Zborder_set_child(b, g);
	Zcanvas_place(c, b, x, y);
}

/* Start: the tiles on the shell background, from under the status bar to the nav bar */
static void start(const Zid c) {
	Zcanvas_place(c, box(W, H, bg()), 0, 0);
	const float m = 12, gap = 8, s = (W - 2 * m - 3 * gap) / 4, med = 2 * s + gap, wide = 4 * s + 3 * gap;
	float y = STATUS + 14;
	tile(c, m, y, med, med, ACCENT, "Phone", Z_SYMBOL_PHONE);
	tile(c, m + med + gap, y, med, med, ACCENT, "People", Z_SYMBOL_PEOPLE);
	y += med + gap;
	tile(c, m, y, s, s, ACCENT, NULL, Z_SYMBOL_MAIL);
	tile(c, m + s + gap, y, s, s, ACCENT, NULL, Z_SYMBOL_CAMERA);
	tile(c, m + med + gap, y, med, med, ACCENT, "Messaging", Z_SYMBOL_COMMENT);
	tile(c, m, y + s + gap, s, s, ACCENT, NULL, Z_SYMBOL_CLOCK);
	tile(c, m + s + gap, y + s + gap, s, s, ACCENT, NULL, Z_SYMBOL_SETTING);
	y += med + gap;
	tile(c, m, y, wide, med, ACCENT, "Calendar", 0);
	const Zid cal = text("Lunch with Alex\n12:30, the usual place", 18, Z_FONT_NORMAL, 0xFFFFFFFF);
	Zcanvas_place(c, cal, m + 10, y + 12);
	y += med + gap;
	tile(c, m, y, med, med, ACCENT, "Music", Z_SYMBOL_PLAY);
	tile(c, m + med + gap, y, med, med, ACCENT, "Store", Z_SYMBOL_SHOP);
}

/* the app: a window between the bars, its page and its own app bar (zrnui draws both) */
static void app(const Zid root) {
	const Zid page = Zpage_create();
	const Zid stack = Zstack_panel_create(Z_VERTICAL);
	Zelement_set_margin(stack, Zthickness(19, 12, 19, 0));
	const Zid t = text("NOTES", 14, Z_FONT_SEMIBOLD, fg());
	Zpanel_add(stack, t);
	const Zid h = Ztext_block_create("today");
	Ztext_block_set_style(h, Z_TEXT_STYLE_PHONE_TITLE1);
	Zelement_set_margin(h, Zthickness(-3, -2, 0, 14));
	Zpanel_add(stack, h);
	const char* rows[][2] = { { "Shopping list", "milk, bread, a lemon" }, { "Ideas", "a tile that shows the tide" },
		{ "Call Alex back", "about Saturday" }, { "Book the train", "the 8:15, two seats" } };
	for (int i = 0; i < 4; i++) {
		const Zid a = text(rows[i][0], 26, Z_FONT_SEMILIGHT, fg());
		const Zid b = text(rows[i][1], 15, Z_FONT_NORMAL, light ? 0xFF6E6E6E : 0xFF9A9A9A);
		Zelement_set_margin(b, Zthickness(0, 0, 0, 14));
		Zpanel_add(stack, a);
		Zpanel_add(stack, b);
	}
	Zpage_set_content(page, stack);
	const Zid bar = Zcommand_bar_create();
	Zcommand_bar_add_primary_command(bar, Zapp_bar_button_create("new", Zsymbol_icon_create(Z_SYMBOL_ADD)));
	Zcommand_bar_add_primary_command(bar, Zapp_bar_button_create("find", Zsymbol_icon_create(Z_SYMBOL_FIND)));
	Zcommand_bar_add_primary_command(bar, Zapp_bar_button_create("sync", Zsymbol_icon_create(Z_SYMBOL_SYNC)));
	Zcommand_bar_add_secondary_command(bar, Zapp_bar_button_create("settings", Z_INVALID_ID));
	Zpage_set_bottom_app_bar(page, bar);
	Zroot_set_visual(root, page);
}

/* the shell's keyboard: four rows of keys above the nav bar */
static void keyboard(const Zid c) {
	const float kh = 46, top = H - NAV - 4 * kh - 8;
	Zcanvas_place(c, box(W, H - NAV - top, chrome()), 0, top);
	const char* rows[] = { "qwertyuiop", "asdfghjkl", "zxcvbnm" };
	const float kw = W / 10.0f;
	const uint32_t key = light ? 0xFFFFFFFF : 0xFF3A3A3A, ink = fg();
	for (int r = 0; r < 3; r++) {
		const int n = (int)strlen(rows[r]);
		const float x0 = (W - n * kw) / 2;
		for (int i = 0; i < n; i++) {
			char s[2] = { rows[r][i], 0 };
			Zcanvas_place(c, label_box(kw - 4, kh - 6, key, s, 20, ink), x0 + i * kw + 2, top + 4 + r * kh);
		}
	}
	Zcanvas_place(c, label_box(kw * 1.5f - 4, kh - 6, key, "&123", 15, ink), 2, top + 4 + 3 * kh);
	Zcanvas_place(c, label_box(kw * 6 - 4, kh - 6, key, "space", 15, ink), kw * 1.5f + 2, top + 4 + 3 * kh);
	Zcanvas_place(c, label_box(kw * 2.5f - 4, kh - 6, ACCENT, "enter", 15, 0xFFFFFFFF), kw * 7.5f + 2, top + 4 + 3 * kh);
}

/* the status bar: signal and Wi-Fi on the left, battery and the clock on the right */
static void status(const Zid c) {
	Zcanvas_place(c, box(W, STATUS, bg()), 0, 0);
	for (int i = 0; i < 4; i++) {
		const float h = 5 + i * 3;
		Zcanvas_place(c, box(3, h, fg()), 10 + i * 5, STATUS - 8 - h);
	}
	Zcanvas_place(c, text("LTE", 11, Z_FONT_SEMIBOLD, fg()), 34, 7);
	const Zid bat = Zborder_create();
	Zelement_set_width(bat, 22);
	Zelement_set_height(bat, 11);
	Zborder_set_border_brush(bat, Zcolor_argb(fg()));
	Zborder_set_border_thickness(bat, Zthickness(1, 1, 1, 1));
	Zcanvas_place(c, bat, W - 70, 9);
	Zcanvas_place(c, box(14, 7, fg()), W - 68, 11);
	Zcanvas_place(c, text("12:45", 13, Z_FONT_NORMAL, fg()), W - 42, 6);
}

/* the action centre: four quick actions and a notification, pulled down over everything below */
static void shade(const Zid c) {
	const float h = 250;
	Zcanvas_place(c, box(W, h, light ? 0xFFF2F2F2 : 0xFF101010), 0, 0);
	Zcanvas_place(c, text("Saturday, 21 November", 15, Z_FONT_NORMAL, fg()), 14, STATUS + 6);
	const char* names[] = { "Wi-Fi", "Bluetooth", "rotation", "camera" };
	const ZSymbol icons[] = { Z_SYMBOL_WORLD, Z_SYMBOL_REMOTE, Z_SYMBOL_ROTATE, Z_SYMBOL_CAMERA };
	const float tw = (W - 14 * 2 - 3 * 8) / 4;
	for (int i = 0; i < 4; i++) {
		tile(c, 14 + i * (tw + 8), STATUS + 34, tw, 62, i < 2 ? ACCENT : (light ? 0xFFBDBDBD : 0xFF3A3A3A), names[i], icons[i]);
	}
	Zcanvas_place(c, text("Messaging", 13, Z_FONT_SEMIBOLD, fg()), 14, STATUS + 112);
	Zcanvas_place(c, text("Alex", 20, Z_FONT_SEMILIGHT, fg()), 14, STATUS + 132);
	Zcanvas_place(c, text("Running ten minutes late, save me a seat", 14, Z_FONT_NORMAL, light ? 0xFF6E6E6E : 0xFF9A9A9A), 14, STATUS + 160);
	Zcanvas_place(c, box(W - 28, 1, light ? 0xFFBDBDBD : 0xFF3A3A3A), 14, STATUS + 190);
	Zcanvas_place(c, box(48, 4, light ? 0xFF9A9A9A : 0xFF6E6E6E), W / 2 - 24, h - 12);
}

/* the nav bar: back, Start, search */
static void nav(const Zid c) {
	Zcanvas_place(c, box(W, NAV, bg()), 0, H - NAV);
	const ZSymbol s[] = { Z_SYMBOL_BACK, Z_SYMBOL_HOME, Z_SYMBOL_FIND };
	for (int i = 0; i < 3; i++) {
		Zcanvas_place(c, symbol(s[i], 24, fg()), W / 6.0f * (2 * i + 1) - 12, H - NAV + 8);
	}
}

/* the lock screen: an opaque picture of its own, clock and date */
static void lock(const Zid c) {
	const uint32_t bands[] = { 0xFF0A2A5C, 0xFF0E3A78, 0xFF13508F, 0xFF1A68A6, 0xFF2484BC, 0xFF35A0CF };
	for (int i = 0; i < 6; i++) Zcanvas_place(c, box(W, H / 6.0f + 1, bands[i]), 0, i * H / 6.0f);
	Zcanvas_place(c, text("7:24", 96, Z_FONT_LIGHT, 0xFFFFFFFF), 18, 380);
	Zcanvas_place(c, text("Saturday", 26, Z_FONT_SEMILIGHT, 0xFFFFFFFF), 22, 494);
	Zcanvas_place(c, text("21 November", 26, Z_FONT_SEMILIGHT, 0xFFFFFFFF), 22, 526);
}

/* the call: an app of its own (ztphone), drawn over the lock with the status row over it */
static void call(const Zid c) {
	Zcanvas_place(c, box(W, H - STATUS, light ? 0xFFFFFFFF : 0xFF1A1A1A), 0, STATUS);
	Zcanvas_place(c, text("incoming call", 16, Z_FONT_NORMAL, fg()), 19, STATUS + 24);
	Zcanvas_place(c, text("Alex", 56, Z_FONT_LIGHT, fg()), 16, STATUS + 46);
	Zcanvas_place(c, text("mobile", 18, Z_FONT_NORMAL, light ? 0xFF6E6E6E : 0xFF9A9A9A), 19, STATUS + 118);
	const Zid face = box(150, 150, ACCENT);
	Zborder_set_child(face, symbol(Z_SYMBOL_CONTACT, 64, 0xFFFFFFFF));
	Zcanvas_place(c, face, W - 150 - 19, STATUS + 170);
	Zcanvas_place(c, label_box(155, 52, 0xFF2E9E3E, "answer", 18, 0xFFFFFFFF), 19, H - 100);
	Zcanvas_place(c, label_box(155, 52, 0xFFC8231E, "ignore", 18, 0xFFFFFFFF), W - 155 - 19, H - 100);
}

/* the banners: the volume's along the top, a toast in the same place when it comes */
static void volume(const Zid c) {
	Zcanvas_place(c, box(W, TOAST, ACCENT), 0, 0);
	Zcanvas_place(c, symbol(Z_SYMBOL_MUSIC_INFO, 22, 0xFFFFFFFF), 14, 18);
	Zcanvas_place(c, text("ringer", 13, Z_FONT_NORMAL, 0xFFFFFFFF), 46, 8);
	Zcanvas_place(c, box(240, 4, 0x66FFFFFF), 46, 34);
	Zcanvas_place(c, box(150, 4, 0xFFFFFFFF), 46, 34);
	Zcanvas_place(c, box(8, 16, 0xFFFFFFFF), 192, 28);
	Zcanvas_place(c, text("12", 22, Z_FONT_SEMILIGHT, 0xFFFFFFFF), W - 40, 16);
}

static void toast(const Zid c) {
	Zcanvas_place(c, box(W, TOAST, ACCENT), 0, 0);
	Zcanvas_place(c, symbol(Z_SYMBOL_COMMENT, 22, 0xFFFFFFFF), 14, 18);
	Zcanvas_place(c, text("Alex", 15, Z_FONT_SEMIBOLD, 0xFFFFFFFF), 46, 10);
	Zcanvas_place(c, text("See you at six by the station", 15, Z_FONT_NORMAL, 0xFFFFFFFF), 46, 30);
}

/* the frost: Start under two bars with zrn-frosted-diffusion; layers.py keeps only the bars' strips */
static void frost(const Zid c) {
	start(c);
	const float reach[2][2] = { { 0, STATUS + 10 }, { H - NAV - 10, H } };
	for (int k = 0; k < 2; k++) {
		const Zid b = Zborder_create();
		Zelement_set_width(b, W);
		Zelement_set_height(b, reach[k][1] - reach[k][0]);
		Zelement_set_frosted_diffusion(b, Z_FROSTED_DIFFUSION_NORMAL, Z_RES_PHONE_CHROME_BRUSH);
		Zcanvas_place(c, b, 0, reach[k][0]);
	}
}

static int draw(const char* dir, const char* name, const char* theme, void (*fill)(Zid), const bool page, const int pass) {
	const Zid root = Zroot_create();
	Zroot_set_renderer(root, Z_RENDERER_GPU);
	Zroot_set_animations(root, Z_ANIMATIONS_OFF);
	Zroot_set_theme(root, light ? Z_THEME_LIGHT : Z_THEME_DARK);
	Zroot_set_density(root, 3.0f);
	if (page) {
		Zroot_set_size(root, W, H - STATUS - NAV);	/* the app's area: between the bars */
		app(root);
	} else {
		Zroot_set_size(root, W, H);
		Zroot_set_background(root, Zcolor_argb(pass ? 0xFFFFFFFF : 0xFF000000));
		const Zid c = Zcanvas_create();
		Zroot_set_visual(root, c);
		fill(c);
	}
	for (int i = 0; i < 40; i++) Zroot_tick(root, 16);
	ZFrame f = {0};
	if (!Zroot_render(root, &f) || !f.pixels) {
		fprintf(stderr, "layers: %s: %s\n", name, Zget_error_message());
		return 0;
	}
	char path[1024];
	snprintf(path, sizeof path, "%s/%s-%s%s.png", dir, name, theme, page ? "" : pass ? "-w" : "-b");
	const int ok = write_png(path, f.pixels, f.width, f.height, f.stride);
	fprintf(stderr, "layers %s %s: renderer %s, %dx%d\n", name, theme, Zroot_get_renderer_name(root), f.width, f.height);
	Zroot_destroy(root);
	return ok;
}

int main(int argc, char** argv) {
	if (argc < 3 || !Zinit()) return 1;
	light = !strcmp(argv[2], "light");
	const struct { const char* name; void (*fill)(Zid); } L[] = {
		{ "start", start }, { "frost", frost }, { "keyboard", keyboard }, { "status", status }, { "shade", shade },
		{ "nav", nav }, { "lock", lock }, { "call", call }, { "volume", volume }, { "toast", toast },
	};
	int ok = draw(argv[1], "app", argv[2], NULL, true, 0);
	/* each layer twice, on black and on white: layers.py takes its coverage from the difference */
	for (size_t i = 0; i < sizeof L / sizeof L[0]; i++) {
		for (int pass = 0; pass < 2; pass++) ok &= draw(argv[1], L[i].name, argv[2], L[i].fill, false, pass);
	}
	Zshutdown();
	return ok ? 0 : 1;
}
