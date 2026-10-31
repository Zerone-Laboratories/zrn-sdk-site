#include <cstdio>
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
	list.item("Goes somewhere", "", [&app] { app.toast("Tapped"); });
	list.item("Wi-Fi", "", [&app] { app.toast("Tapped"); }).set_icon("wifi").set_detail("Home-5G");
	list.item("Tinted icon", "zrnCoolStyle only").set_icon("music").set_tint(0xd9486e);
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

static void el_icons([[maybe_unused]] zrn::ui::App &app, zrn::ui::Node page) {
	auto card = page.card();
	for (const char *name : { "wifi", "bluetooth", "bell", "moon", "sun", "lock", "volume", "battery", "info", "search", "plus", "check", "close", "more", "back", "chevron", "music", "person", "gear", "phone" })
		card.item(name).set_icon(name);
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
	auto p_icons = app.page("Icons"); el_icons(app, p_icons);
	return app.run(p_text);
}
