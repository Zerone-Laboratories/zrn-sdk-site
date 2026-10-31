#![allow(unused_variables)]

fn el_text<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    page.heading("A heading");
    page.text("Body text. It wraps at the page's width, and HarfBuzz shapes it, so Sinhala and Tamil come out right.");
    page.caption("A caption: small and quiet.");
}

fn el_button<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    use zrnui::Variant;
    page.button("Primary");
    page.button("Tonal").set_variant(Variant::Tonal);
    page.button("Plain").set_variant(Variant::Plain);
    page.button("Danger").set_variant(Variant::Danger);
    page.button("Disabled").set_enabled(false);
}

fn el_item<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    let list = page.section("Rows");
    list.item("Title only", None);
    list.item("With a second line", Some("Under the title"));
    list.item("Takes a tap", None).on_click(move || app.toast("Tapped"));
    list.item("Wi-Fi", None).on_click(move || app.toast("Tapped")).set_icon("wifi").set_detail("Home-5G");
}

fn el_switch<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    let card = page.section("Connections");
    let wifi = card.switch("Wi-Fi", true);
    wifi.on_change(move |on| { wifi.set_detail(if on { "Connected" } else { "Off" }); });
    card.switch("Bluetooth", false);
    card.switch("Roaming", false).set_enabled(false);
}

fn el_slider<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    let card = page.section("Display");
    card.slider("Brightness", 0.6).on_slide(|v, done| { if done { println!("saved {v:.2}"); } });
    page.slider("Outside a card", 0.25);
}

fn el_progress<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    page.text("Copying 7 of 10");
    page.progress(0.7);
    page.text("No idea how long");
    page.progress(-1.0);
}

fn el_field<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    page.field("Search").on_edit(|t, submitted| { if submitted { println!("search: {t}"); } });
    page.field("Name").set_text("Already filled in");
}

fn el_section<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    page.section("A section").item("In its card", None);
    let card = page.card();
    card.text("A card with no heading can hold anything.");
    card.button("Like this");
}

fn el_layout<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    let row = page.row();
    row.button("1 share").set_flex(1.0);
    row.button("2 shares").set_variant(zrnui::Variant::Tonal).set_flex(2.0);
    page.space(40.0);
    let col = page.column();
    col.text("A column keeps things together");
    col.caption("and can be hidden as one.");
}

fn el_round<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    let bar = page.row();
    for name in ["plus", "search", "send", "more"] {
        bar.button(name).set_icon(name).set_flex(1.0);
    }
}

fn el_icons<'a>(app: &'a zrnui::App, page: zrnui::Node<'a>) {
    for names in ["wifi", "bluetooth", "bell", "moon", "sun", "lock", "volume", "battery", "info", "search", "plus", "check", "close", "more", "back", "chevron", "music", "person", "gear", "phone", "send"].chunks(4) {
        let row = page.row();
        for name in names {
            row.button(name).set_icon(name).set_flex(1.0);
        }
    }
}

fn main() {
    let app = zrnui::App::new("zrn-sdk-site-proof", "SDK");
    let p_text = app.page("Text"); el_text(&app, p_text);
    let p_button = app.page("Buttons"); el_button(&app, p_button);
    let p_item = app.page("List rows"); el_item(&app, p_item);
    let p_switch = app.page("Switches"); el_switch(&app, p_switch);
    let p_slider = app.page("Sliders"); el_slider(&app, p_slider);
    let p_progress = app.page("Progress"); el_progress(&app, p_progress);
    let p_field = app.page("Text fields"); el_field(&app, p_field);
    let p_section = app.page("Sections and cards"); el_section(&app, p_section);
    let p_layout = app.page("Rows, columns, space"); el_layout(&app, p_layout);
    let p_round = app.page("Round buttons"); el_round(&app, p_round);
    let p_icons = app.page("Icons"); el_icons(&app, p_icons);
    std::process::exit(app.run(p_text));
}
