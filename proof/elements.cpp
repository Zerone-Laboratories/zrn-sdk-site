#include <cstdio>
#include <cstdint>
#include <string>
#include <zrnui.hpp>

static void el_text([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	page.heading("A heading");
	page.text("Body text. It wraps at the page's width, and HarfBuzz shapes it, so Sinhala and Tamil come out right.");
	page.caption("A caption: small and quiet.");
}

static void el_button([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	using zrn::ui::Variant;
	page.button("Primary");
	page.button("Tonal").set_variant(Variant::Tonal);
	page.button("Plain").set_variant(Variant::Plain);
	page.button("Danger").set_variant(Variant::Danger);
	page.button("Disabled").set_enabled(false);
}

static void el_item([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	auto list = page.section("Rows");
	list.item("Title only");
	list.item("With a second line", "Under the title");
	list.item("Takes a tap", "", [&app] { app.toast("Tapped"); });
	list.item("Wi-Fi", "", [&app] { app.toast("Tapped"); }).set_icon("wifi").set_detail("Home-5G");
}

static void el_switch([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	auto card = page.section("Connections");
	auto wifi = card.toggle("Wi-Fi", true);
	wifi.on([](zrn::ui::Node sw, int) { sw.set_detail(sw.is_on() ? "Connected" : "Off"); });
	card.toggle("Bluetooth", false);
	card.toggle("Roaming", false).set_enabled(false);
}

static void el_slider([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	auto card = page.section("Display");
	card.slider("Brightness", 0.6, [](double v, bool done) { if (done) printf("saved %.2f\n", v); });
	page.slider("Outside a card", 0.25);
}

static void el_progress([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	page.text("Copying 7 of 10");
	page.progress(0.7);
	page.text("No idea how long");
	page.progress(-1);
}

static void el_field([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	page.field("Search", [](const std::string &t, bool submitted) {
		if (submitted) printf("search: %s\n", t.c_str());
	});
	page.field("Name").set_text("Already filled in");
}

static void el_section([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	page.section("A section").item("In its card");
	auto card = page.card();
	card.text("A card with no heading can hold anything.");
	card.button("Like this");
}

static void el_layout([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	auto row = page.row();
	row.button("1 share").set_flex(1);
	row.button("2 shares").set_variant(zrn::ui::Variant::Tonal).set_flex(2);
	page.space(40);
	auto col = page.column();
	col.text("A column keeps things together");
	col.caption("and can be hidden as one.");
}

static void el_round([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	auto bar = page.row();
	for (const char *name : { "plus", "search", "send", "more" })
		bar.button(name).set_icon(name).set_flex(1);
}

static void el_picture([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	static uint8_t px[64 * 64 * 4];
	for (int i = 0; i < 64 * 64; i++) {
		px[i * 4] = i % 64 * 4; px[i * 4 + 1] = i / 64 * 4; px[i * 4 + 2] = 200; px[i * 4 + 3] = 255;
	}
	zui_pixmap *pix = zui_pixmap_rgba(64, 64, px);  // or zui_pixmap_load("photo.jpg", 1024)
	page.image(pix, 0, 140);
	auto card = page.section("Thread rows");
	card.item("Ada", "A picture as the tile").set_image(pix).set_detail("09:41");
	card.item("Ben", "A monogram, a count, unread").set_monogram("B").set_tint(0xd9486e)
		.set_badge("3").set_emphasis(true);
	zui_pixmap_free(pix);
}

static void el_list([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	page.list(5000, [](int) { return 66.0; }, [](int row, zrn::ui::Node node) {
		node.item("Row " + std::to_string(row + 1), row % 3 ? "Made when it came near" : "Of 5000");
	});
}

static void el_pivot([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	auto tabs = page.tabs();
	auto one = tabs.tab("chats");
	one.item("Ada", "See you soon");
	one.item("Ben", "Thanks");
	tabs.tab("status").item("Nothing yet");
	tabs.tab("starred").item("Nothing yet");
}

static void el_bubble([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	page.set_compact(true);
	page.set_subtitle("Last seen today");
	auto in = page.bubble(false);
	in.text("Are you coming tonight?");
	in.caption("18:02");
	auto me = page.bubble(true);
	me.text("Yes, on my way");
	me.caption("18:03");
}

static void el_footer([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	page.text("The page scrolls under the bar.");
	auto bar = page.footer();
	bar.field("Type a message").set_flex(1);
	bar.button("Send");
}

static void el_icons([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	const char *names[] = { "wifi", "bluetooth", "bell", "moon", "sun", "lock", "volume", "battery", "info", "search", "plus", "check", "close", "more", "back", "chevron", "music", "person", "gear", "phone", "send" };
	for (int i = 0; i < 21; i += 4) {
		auto row = page.row();
		for (int k = i; k < i + 4 && k < 21; k++)
			row.button(names[k]).set_icon(names[k]).set_flex(1);
	}
}

int main() {
	zrn::ui::App app("zrn-sdk-site-proof", "SDK");
	auto p_text = app.page("Text"); el_text(app, p_text);
	auto p_button = app.page("Buttons"); el_button(app, p_button);
	auto p_item = app.page("List rows"); el_item(app, p_item);
	auto p_switch = app.page("Switches"); el_switch(app, p_switch);
	auto p_slider = app.page("Sliders"); el_slider(app, p_slider);
	auto p_progress = app.page("Progress"); el_progress(app, p_progress);
	auto p_field = app.page("Text fields"); el_field(app, p_field);
	auto p_section = app.page("Sections and cards"); el_section(app, p_section);
	auto p_layout = app.page("Rows, columns, space"); el_layout(app, p_layout);
	auto p_round = app.page("Round buttons"); el_round(app, p_round);
	auto p_picture = app.page("Pictures"); el_picture(app, p_picture);
	auto p_list = app.page("Long lists"); el_list(app, p_list);
	auto p_pivot = app.page("Pivots"); el_pivot(app, p_pivot);
	auto p_bubble = app.page("Bubbles and compact titles"); el_bubble(app, p_bubble);
	auto p_footer = app.page("Footer"); el_footer(app, p_footer);
	auto p_icons = app.page("Icons"); el_icons(app, p_icons);
	return app.run(p_text);
}
