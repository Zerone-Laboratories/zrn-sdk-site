import zrnui

def el_text(app, page):
    page.heading("A heading")
    page.text("Body text. It wraps at the page's width, and HarfBuzz shapes it, so Sinhala and Tamil come out right.")
    page.caption("A caption: small and quiet.")


def el_button(app, page):
    page.button("Primary")
    page.button("Tonal", variant=zrnui.TONAL)
    page.button("Plain", variant=zrnui.PLAIN)
    page.button("Danger", variant=zrnui.DANGER)
    page.button("Disabled").enabled = False


def el_item(app, page):
    rows = page.section("Rows")
    rows.item("Title only")
    rows.item("With a second line", "Under the title")
    rows.item("Goes somewhere", on_click=lambda: app.toast("Tapped"))
    rows.item("Wi-Fi", on_click=lambda: app.toast("Tapped"), icon="wifi", detail="Home-5G")
    rows.item("Tinted icon", "zrnCoolStyle only", icon="music", tint=0xd9486e)


def el_switch(app, page):
    card = page.section("Connections")
    wifi = card.switch("Wi-Fi", True)
    wifi.on_event(lambda sw, event: setattr(wifi, "detail", "Connected" if wifi.on else "Off"))
    card.switch("Bluetooth", False)
    card.switch("Roaming", False).enabled = False


def el_slider(app, page):
    card = page.section("Display")
    card.slider("Brightness", 0.6, on_release=lambda v: print("saved %.2f" % v))
    page.slider("Outside a card", 0.25)


def el_progress(app, page):
    page.text("Copying 7 of 10")
    page.progress(0.7)
    page.text("No idea how long")
    page.progress(-1)


def el_field(app, page):
    page.field("Search", on_submit=lambda t: print("search:", t))
    page.field("Name").set_text("Already filled in")


def el_section(app, page):
    page.section("A section").item("In its card")
    card = page.card()
    card.text("A card with no heading can hold anything.")
    card.button("Like this")


def el_layout(app, page):
    row = page.row()
    row.button("1 share").flex = 1
    row.button("2 shares", variant=zrnui.TONAL).flex = 2
    page.space(40)
    col = page.column()
    col.text("A column keeps things together")
    col.caption("and can be hidden as one.")


def el_icons(app, page):
    card = page.card()
    for name in ["wifi", "bluetooth", "bell", "moon", "sun", "lock", "volume", "battery", "info", "search", "plus", "check", "close", "more", "back", "chevron", "music", "person", "gear", "phone"]:
        card.item(name, icon=name)


app = zrnui.App("zrn-sdk-site-proof", "SDK")
p_text = app.page("Text"); el_text(app, p_text)
p_button = app.page("Buttons"); el_button(app, p_button)
p_item = app.page("List rows"); el_item(app, p_item)
p_switch = app.page("Switches"); el_switch(app, p_switch)
p_slider = app.page("Sliders"); el_slider(app, p_slider)
p_progress = app.page("Progress"); el_progress(app, p_progress)
p_field = app.page("Text fields"); el_field(app, p_field)
p_section = app.page("Sections and cards"); el_section(app, p_section)
p_layout = app.page("Rows, columns, space"); el_layout(app, p_layout)
p_icons = app.page("Icons"); el_icons(app, p_icons)
app.run(p_text)
