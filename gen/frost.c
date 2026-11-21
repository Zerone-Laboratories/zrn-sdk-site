#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <zrnui/controls.h>
#include <zrnui/host.h>
#include "writepng.h"

/* A colourful list under a bar laid over its top, with the given diffusion. */
int main(int argc, char** argv) {
	if (argc < 4 || !Zinit()) return 1;
	const int mode = atoi(argv[2]);
	const int light = atoi(argv[3]);
	const Zid root = Zroot_create();
	Zroot_set_renderer(root, Z_RENDERER_GPU);
	Zroot_set_theme(root, light ? Z_THEME_LIGHT : Z_THEME_DARK);
	Zroot_set_size(root, 480, 300);
	const Zid grid = Zgrid_create();
	Zgrid_add_row(grid, Z_GRID_STAR, 1);
	const Zid stack = Zstack_panel_create(Z_VERTICAL);
	const uint32_t cols[] = { 0xFFE51400, 0xFFF09609, 0xFF8CBF26, 0xFF00ABA9, 0xFF1BA1E2, 0xFFA200FF, 0xFFE671B8 };
	for (int i = 0; i < 7; i++) {
		const Zid b = Zborder_create();
		Zborder_set_background(b, Zcolor_argb(cols[i]));
		Zelement_set_height(b, 44);
		Zelement_set_margin(b, Zthickness(0, 0, 0, 0));
		const Zid t = Ztext_block_create("A ROW BEHIND THE BAR");
		Ztext_block_set_font_size(t, 26);
		Ztext_block_set_foreground(t, Zcolor_argb(0xFFFFFFFF));
		Zelement_set_margin(t, Zthickness(19, 6, 0, 0));
		Zborder_set_child(b, t);
		Zpanel_add(stack, b);
	}
	Zgrid_place(grid, stack, 0, 0);
	const Zid bar = Zborder_create();
	Zelement_set_height(bar, 150);
	Zelement_set_vertical_alignment(bar, Z_VALIGN_TOP);
	const Zid title = Ztext_block_create("frosted");
	Ztext_block_set_style(title, Z_TEXT_STYLE_PHONE_TITLE1);
	Zborder_set_child(bar, title);
	Zelement_set_frosted_diffusion(bar, (ZFrostedDiffusion)mode, Z_RES_PHONE_CHROME_BRUSH);
	Zgrid_place(grid, bar, 0, 0);
	Zroot_set_visual(root, grid);
	for (int i = 0; i < 30; i++) Zroot_tick(root, 16);
	ZFrame f = {0};
	if (!Zroot_render(root, &f)) { fprintf(stderr, "render: %s\n", Zget_error_message()); }
	if (!f.pixels) return 2;
	const int ok = write_png(argv[1], f.pixels, f.width, f.height, f.stride);
	fprintf(stderr, "renderer %s\n", Zroot_get_renderer_name(root));
	return ok ? 0 : 1;
}
