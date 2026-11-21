/*
 * Records zrnui's own animations for sdk.ztos.online.
 *
 *   anim <scenario> <dark|light>  >  frames.rgba
 *
 * Draws with the GLES2 renderer offscreen (Mesa, surfaceless EGL), animations on,
 * 360 x 640 points at 2 device pixels a point. Time moves only by Zroot_tick in
 * fixed 1/60 s steps, and every step is read back with Zroot_render and written
 * to stdout as raw RGBA, top row first. gen/render.py encodes that with ffmpeg.
 * Input is injected as a finger would give it (Zroot_inject_pointer).
 *
 * The "frost" scenario needs zrn-frosted-diffusion, which is not in 71a5ace:
 * it is compiled only with -DWITH_FROST against a tree that has it.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zrnui/controls.h>
#include <zrnui/host.h>
#include <zrnui/platform.h>

enum { W = 360, H = 640 };
static constexpr float DENSITY = 2.0f;
static Zid root;
static int frames;

static void frame(void) {
	Zroot_tick(root, 1000.0f / 60.0f);
	ZFrame f = {0};
	Zroot_render(root, &f);
	if (!f.pixels) { fprintf(stderr, "anim: no frame: %s\n", Zget_error_message()); exit(2); }
	for (int y = 0; y < f.height; y++) fwrite(f.pixels + (size_t)y * f.stride, 4, (size_t)f.width, stdout);
	frames++;
}

static void hold(const int n) { for (int i = 0; i < n; i++) frame(); }

/* time passes and frames are drawn, but none is written: lets an entrance settle before a clip starts */
static void settle(const int n) {
	for (int i = 0; i < n; i++) {
		Zroot_tick(root, 1000.0f / 60.0f);
		ZFrame f = {0};
		Zroot_render(root, &f);
	}
}

/* the rectangle of an element in root points */
static ZRect abs_rect(Zid e) {
	ZRect r = Zelement_get_bounds(e);
	for (Zid p = Zelement_get_parent(e); p != Z_INVALID_ID; p = Zelement_get_parent(p)) {
		const ZRect b = Zelement_get_bounds(p);
		r.x += b.x;
		r.y += b.y;
	}
	return r;
}

static void press(const float x, const float y) {
	Zroot_inject_pointer(root, Z_POINTER_MOVE, x, y);
	Zroot_inject_pointer(root, Z_POINTER_DOWN, x, y);
}
static void release(const float x, const float y) { Zroot_inject_pointer(root, Z_POINTER_UP, x, y); }

static void tap(const float x, const float y) {
	press(x, y);
	hold(4);
	release(x, y);
}

static Zid text(const char* s, const ZTextStyle style) {
	const Zid t = Ztext_block_create(s);
	Ztext_block_set_style(t, style);
	return t;
}

static Zid padded_stack(void) {
	const Zid stack = Zstack_panel_create(Z_VERTICAL);
	Zelement_set_margin(stack, Zthickness(19, 12, 19, 0));
	return stack;
}

static const char* const ROWS[] = { "wi-fi", "bluetooth", "airplane mode", "cellular", "location", "battery saver", "lock screen" };

static Zid page_rows(const char* title, int first) {
	const Zid page = Zpage_create();
	const Zid stack = padded_stack();
	Zpanel_add(stack, text("SETTINGS", Z_TEXT_STYLE_PHONE_NORMAL));
	Zpanel_add(stack, text(title, Z_TEXT_STYLE_PHONE_TITLE1));
	for (int i = 0; i < 6; i++) {
		const Zid row = text(ROWS[(first + i) % 7], Z_TEXT_STYLE_PHONE_EXTRA_LARGE);
		Zpanel_add(stack, row);
	}
	Zpage_set_content(page, stack);
	return page;
}

static Zid page_a(const Zid f, void* const p) { (void)f; (void)p; return page_rows("system", 0); }
static Zid page_b(const Zid f, void* const p) { (void)f; (void)p; return page_rows("wi-fi", 3); }

static void turnstile(void) {
	const Zid fr = Zframe_create();
	Zroot_set_visual(root, fr);
	Zframe_navigate(fr, page_a, nullptr);
	settle(60); /* the first page swings in too; start on it standing */
	hold(30);
	Zframe_navigate(fr, page_b, nullptr);
	hold(70);
	hold(30);
	Zframe_go_back(fr);
	hold(70);
	hold(20);
}

static void pivot(void) {
	const Zid page = Zpage_create();
	const Zid pv = Zpivot_create();
	Zpivot_set_title(pv, "MAIL");
	const char* const heads[] = { "all", "unread", "flagged" };
	for (int i = 0; i < 3; i++) {
		const Zid item = Zpivot_item_create(heads[i]);
		const Zid stack = Zstack_panel_create(Z_VERTICAL);
		for (int k = 0; k < 4; k++) {
			char line[48];
			snprintf(line, sizeof line, "%s message %d", heads[i], k + 1);
			Zpanel_add(stack, text(line, Z_TEXT_STYLE_PHONE_TITLE2));
			Zpanel_add(stack, text("a line of the message, in the subtle colour", Z_TEXT_STYLE_PHONE_SUBTLE));
		}
		Zcontent_control_set_content(item, stack);
		Zpivot_add_item(pv, item);
	}
	Zpage_set_content(page, pv);
	Zroot_set_visual(root, page);
	hold(40);
	for (int step = 1; step <= 3; step++) {
		Zroot_update_layout(root);
		const int next = step % 3;
		const ZRect h = Zpivot_get_header_rect(pv, next);
		const ZRect p = abs_rect(pv);
		tap(p.x + h.x + h.width / 2, p.y + h.y + h.height / 2);
		hold(45);
	}
}

static void tilt(void) {
	const Zid page = Zpage_create();
	const Zid stack = padded_stack();
	Zpanel_add(stack, text("people", Z_TEXT_STYLE_PHONE_TITLE1));
	const Zid list = Zlist_view_create();
	const char* const names[] = { "Alice Walker", "Ben Carter", "Chloe Adams", "Daniel Hughes", "Emma Brooks" };
	Zid items[5];
	for (int i = 0; i < 5; i++) {
		items[i] = Zlist_view_item_create(nullptr);
		const Zid t = text(names[i], Z_TEXT_STYLE_PHONE_EXTRA_LARGE);
		Zcontent_control_set_content(items[i], t);
		Zitems_control_add(list, items[i]);
	}
	Zelement_set_height(list, 460);
	Zpanel_add(stack, list);
	Zpage_set_content(page, stack);
	Zroot_set_visual(root, page);
	hold(30);
	const int order[] = { 1, 3 };
	const float xs[] = { 40, 300 };
	for (int k = 0; k < 2; k++) {
		Zroot_update_layout(root);
		const ZRect r = abs_rect(items[order[k]]);
		const float x = r.x + xs[k], y = r.y + r.height / 2;
		press(x, y);
		hold(40);
		release(x, y);
		hold(30);
	}
}

static void appbar(void) {
	const Zid page = Zpage_create();
	const Zid stack = padded_stack();
	Zpanel_add(stack, text("NOTES", Z_TEXT_STYLE_PHONE_NORMAL));
	Zpanel_add(stack, text("shopping", Z_TEXT_STYLE_PHONE_TITLE1));
	const Zid body = text("milk, bread, rice, coconuts, tea", Z_TEXT_STYLE_PHONE_TITLE2);
	Ztext_block_set_text_wrapping(body, Z_WRAP);
	Zpanel_add(stack, body);
	Zpage_set_content(page, stack);
	const Zid bar = Zcommand_bar_create();
	Zcommand_bar_add_primary_command(bar, Zapp_bar_button_create("add", Zsymbol_icon_create(Z_SYMBOL_ADD)));
	Zcommand_bar_add_primary_command(bar, Zapp_bar_button_create("edit", Zsymbol_icon_create(Z_SYMBOL_EDIT)));
	Zcommand_bar_add_primary_command(bar, Zapp_bar_button_create("delete", Zsymbol_icon_create(Z_SYMBOL_DELETE)));
	Zcommand_bar_add_secondary_command(bar, Zapp_bar_button_create("settings", Z_INVALID_ID));
	Zcommand_bar_add_secondary_command(bar, Zapp_bar_button_create("about", Z_INVALID_ID));
	Zpage_set_bottom_app_bar(page, bar);
	Zroot_set_visual(root, page);
	hold(40);
	Zapp_bar_set_is_open(bar, true);
	hold(70);
	Zapp_bar_set_is_open(bar, false);
	hold(40);
}

static void toggle(void) {
	const Zid page = Zpage_create();
	const Zid stack = padded_stack();
	Zpanel_add(stack, text("location", Z_TEXT_STYLE_PHONE_TITLE1));
	const Zid sw = Ztoggle_switch_create();
	Ztoggle_switch_set_header(sw, "Location services");
	Zpanel_add(stack, sw);
	Zpage_set_content(page, stack);
	Zroot_set_visual(root, page);
	hold(30);
	for (int k = 0; k < 4; k++) {
		Zroot_update_layout(root);
		const ZRect r = abs_rect(sw);
		/* the switch box: 77 x 36 at the right edge, at the bottom of the control */
		tap(r.x + r.width - 38, r.y + r.height - 22);
		hold(36);
	}
}

static void theme(void) {
	const Zid page = Zpage_create();
	const Zid stack = padded_stack();
	Zpanel_add(stack, text("theme", Z_TEXT_STYLE_PHONE_TITLE1));
	const Zid cb = Zcheck_box_create("Dark theme");
	Ztoggle_button_set_is_checked(cb, true);
	Zpanel_add(stack, cb);
	const Zid sw = Ztoggle_switch_create();
	Ztoggle_switch_set_header(sw, "Accent on tiles");
	Ztoggle_switch_set_is_on(sw, true);
	Zpanel_add(stack, sw);
	const Zid sl = Zslider_create(Z_HORIZONTAL);
	Zslider_set_header(sl, "Text size");
	Zrange_base_set_value(sl, 60);
	Zpanel_add(stack, sl);
	Zpanel_add(stack, Zbutton_create("apply"));
	Zpage_set_content(page, stack);
	Zroot_set_visual(root, page);
	hold(40);
	const ZTheme now = Zroot_get_theme(root);
	Zroot_set_theme(root, now == Z_THEME_DARK ? Z_THEME_LIGHT : Z_THEME_DARK);
	hold(60);
	Zroot_set_theme(root, now);
	hold(50);
}

static void hub(void) {
	const Zid page = Zpage_create();
	const Zid hb = Zhub_create();
	Zhub_set_header(hb, "music");
	const char* const heads[] = { "recent", "albums", "artists", "playlists" };
	for (int i = 0; i < 4; i++) {
		const Zid s = Zhub_section_create(heads[i]);
		const Zid stack = Zstack_panel_create(Z_VERTICAL);
		for (int k = 0; k < 4; k++) {
			char line[40];
			snprintf(line, sizeof line, "%s %d", heads[i], k + 1);
			Zpanel_add(stack, text(line, Z_TEXT_STYLE_PHONE_TITLE2));
		}
		Zcontent_control_set_content(s, stack);
		Zhub_add_section(hb, s);
	}
	Zpage_set_content(page, hb);
	Zroot_set_visual(root, page);
	hold(30);
	for (int pass = 0; pass < 2; pass++) {
		const float y = 380;
		press(300, y);
		for (int i = 1; i <= 24; i++) {
			Zroot_inject_pointer(root, Z_POINTER_MOVE, 300 - i * 11.0f, y);
			frame();
		}
		release(36, y);
		hold(50);
	}
	Zhub_scroll_to_section(hb, 0);
	hold(50);
}

#ifdef WITH_FROST
static void frost(void) {
	const Zid grid = Zgrid_create();
	Zgrid_add_row(grid, Z_GRID_STAR, 1);
	const Zid viewer = Zscroll_viewer_create();
	const Zid stack = Zstack_panel_create(Z_VERTICAL);
	const uint32_t cols[] = { 0xFFE51400, 0xFFF09609, 0xFF8CBF26, 0xFF00ABA9, 0xFF1BA1E2, 0xFFA200FF, 0xFFE671B8 };
	for (int i = 0; i < 28; i++) {
		const Zid b = Zborder_create();
		Zborder_set_background(b, Zcolor_argb(cols[i % 7]));
		Zelement_set_height(b, 56);
		const Zid t = Ztext_block_create(ROWS[i % 7]);
		Ztext_block_set_font_size(t, 30);
		Ztext_block_set_foreground(t, Zcolor_argb(0xFFFFFFFF));
		Zelement_set_margin(t, Zthickness(19, 8, 0, 0));
		Zborder_set_child(b, t);
		Zpanel_add(stack, b);
	}
	Zscroll_viewer_set_content(viewer, stack);
	Zgrid_place(grid, viewer, 0, 0);
	const Zid bar = Zborder_create();
	Zelement_set_height(bar, 170);
	Zelement_set_vertical_alignment(bar, Z_VALIGN_TOP);
	const Zid label = Ztext_block_create("normal");
	Ztext_block_set_style(label, Z_TEXT_STYLE_PHONE_TITLE1);
	Zborder_set_child(bar, label);
	Zgrid_place(grid, bar, 0, 0);
	Zroot_set_visual(root, grid);
	const ZFrostedDiffusion modes[] = { Z_FROSTED_DIFFUSION_NORMAL, Z_FROSTED_DIFFUSION_ASCENDING, Z_FROSTED_DIFFUSION_DESCENDING };
	const char* const names[] = { "normal", "ascending", "descending" };
	double off = 0;
	for (int m = 0; m < 3; m++) {
		Zelement_set_frosted_diffusion(bar, modes[m], Z_RES_PHONE_CHROME_BRUSH);
		Ztext_block_set_text(label, names[m]);
		for (int i = 0; i < 100; i++) {
			off += (m % 2 ? -1.0 : 1.0) * 2.2;
			if (off < 0) off = 0;
			Zscroll_viewer_scroll_to_vertical_offset(viewer, off);
			frame();
		}
	}
}
#endif

int main(int argc, char** argv) {
	if (argc < 3 || !Zinit()) return 1;
	root = Zroot_create();
	Zroot_set_renderer(root, Z_RENDERER_GPU);
	Zroot_set_animations(root, Z_ANIMATIONS_ON);
	Zroot_set_theme(root, strcmp(argv[2], "light") ? Z_THEME_DARK : Z_THEME_LIGHT);
	Zroot_set_size(root, W, H);
	Zroot_set_density(root, DENSITY);
	/* a new root starts Dark: a Light theme cross-fades in over 250 ms. Let it settle before
	 * the first frame is written, so a clip opens on its own theme (the "theme" clip fades later, on purpose) */
	for (int i = 0; i < 40; i++) {
		Zroot_tick(root, 1000.0f / 60.0f);
		ZFrame f = {0};
		Zroot_render(root, &f);
	}
	const char* s = argv[1];
	if (!strcmp(s, "turnstile")) turnstile();
	else if (!strcmp(s, "pivot")) pivot();
	else if (!strcmp(s, "tilt")) tilt();
	else if (!strcmp(s, "appbar")) appbar();
	else if (!strcmp(s, "toggle")) toggle();
	else if (!strcmp(s, "theme")) theme();
	else if (!strcmp(s, "hub")) hub();
#ifdef WITH_FROST
	else if (!strcmp(s, "frost")) frost();
#endif
	else { fprintf(stderr, "anim: unknown scenario %s\n", s); return 1; }
	fprintf(stderr, "anim %s %s: %d frames, %dx%d, renderer %s\n", s, argv[2], frames,
		(int)(W * DENSITY), (int)(H * DENSITY), Zroot_get_renderer_name(root));
	Zroot_destroy(root);
	Zshutdown();
	return 0;
}
