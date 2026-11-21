"""The wiki's words. Everything here was checked against zrn-sdk at COMMIT (SDK v2)."""
COMMIT = "71a5ace"

SHELL = """<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#121212">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ztOS SDK">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://ztos.online/og.jpg">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<div class="layout">
<aside class="sidebar">
<a class="wordmark" href="/">ztOS <span>SDK</span></a>
<nav class="desk" aria-label="Pages"><ul>{links}</ul></nav>
<details class="menu"><summary>Pages</summary><nav aria-label="Pages"><ul>{links}</ul></nav></details>
<div class="side-foot"><a href="https://ztos.online">ztos.online</a><a href="https://github.com/Zerone-Laboratories/zrn-sdk">zrn-sdk on GitHub</a><a href="https://github.com/Zerone-Laboratories/zrn-sdk-site">This site's source</a></div>
</aside>
<main>
{body}
<p class="foot">Checked against zrn-sdk commit <a href="https://github.com/Zerone-Laboratories/zrn-sdk/tree/{commit}"><code>{commit}</code></a> (SDK v2). Pictures and clips are drawn by zrnui's GLES2 renderer, offscreen, from code that compiled, against the zrn-sdk working tree on top of that commit (it adds the app bar measured on a Windows Phone 8.1 phone and the Segoe WP font lookup), in Segoe WP. <a href="https://github.com/Zerone-Laboratories/zrn-sdk-site">Source and proof</a>.</p>
</main>
</div>
</body>
</html>
"""


PAGES = {
"index": ("ztOS SDK wiki", "How to make apps for ztOS with zrnSDK v2: Windows Phone 8.1 controls in C23, every element rendered in Dark and Light, and how to build and run on a phone.", """
<h1>Make apps for ztOS</h1>
<p class="lead">ztOS apps are written in <b>C</b> against <b>zrnSDK v2</b>. It gives you the controls of Windows Phone 8.1: pages, a Pivot and a Hub, buttons, lists, pickers, app bars and dialogs. C++ apps include the same headers.</p>
<div class="gap"><b>This site documents SDK v2</b><p>SDK v1 (<code>zui_*</code>, <code>zrn render</code>, four languages) is gone. Nothing here works with v1, and v1 code does not build against v2. What is not committed yet is on <a href="/next">Coming next</a>.</p></div>
<pre><code>git clone https://github.com/Zerone-Laboratories/zrn-sdk
cd zrn-sdk/examples/helloworld
cmake --preset host-debug
cmake --build --preset host-debug
./build/host-debug/helloworld          <span class="c"># inside a Wayland session</span></code></pre>
{{SHOTS:pivot}}
<div class="cards">
<a href="/start"><b>Getting started</b><span>Build, first app, the life cycle</span></a>
<a href="/apps"><b>Ways to make an app</b><span>C, C++, or zrnui inside your own shell</span></a>
<a href="/project"><b>Project layout</b><span>CMake, presets, app id, licences</span></a>
<a href="/elements"><b>UI elements</b><span>Each one, rendered, with its code</span></a>
<a href="/layout"><b>Layout and theme</b><span>Panels, Dark and Light, accents, fonts</span></a>
<a href="/animations"><b>Animations</b><span>Turnstile, pivot slide, tilt, easing</span></a>
<a href="/shipping"><b>Build and ship</b><span>Phone builds, tools/zrn run, packages</span></a>
<a href="/publish"><b>Publish to the store</b><span>zrnapp.toml, submitting, updates</span></a>
<a href="/troubleshooting"><b>Troubleshooting</b><span>Real errors and their fixes</span></a>
<a href="/status"><b>Status and gaps</b><span>What is missing or unproven</span></a>
<a href="/next"><b>Coming next</b><span>Work that is not committed yet</span></a>
</div>
<h2>How the code on this site was checked</h2>
<p>Each element's snippet is put into a small C program and <b>compiled against zrnui: the pinned commit plus the uncommitted working tree</b> (app bar measurements, Segoe WP lookup), with <code>-Wall -Wextra -Werror</code>. The program draws it with zrnui's <b>GLES2 renderer</b> (<code>Z_RENDERER_GPU</code>), offscreen through Mesa, once in Dark and once in Light, with the default Cobalt accent, in Segoe WP from a Windows Phone 8.1 firmware (read at render time; the font is Microsoft's and is not served by this site). The page is 360 points wide, as ztOS lays an app out on the S9, and shown here at that size.</p>
<p>The <a href="/animations">animation clips</a> are recorded the same way: <code>Zroot_tick</code> in steps of 1/60 s, each frame read back. Nothing is drawn by hand. The generator and its report are in <a href="https://github.com/Zerone-Laboratories/zrn-sdk-site">this site's repository</a>.</p>
"""),

"start": ("Getting started: ztOS SDK", "Build zrnSDK v2 with CMake, run the hello world, and learn handles, the root, pages, events and time.", """
<h1>Getting started</h1>
<p class="lead">You can write and run an app on a Linux computer with a Wayland session. A phone is only needed to check touch, scale and speed.</p>
<h2 id="need">What you need</h2>
<ul>
<li>A C23 compiler: GCC 13 or newer, or Clang 19 or newer.</li>
<li><code>cmake</code> 3.21 or newer (for presets), <code>ninja</code>, <code>pkgconf</code>, <code>freetype2</code>, <code>libpng</code>.</li>
<li>For the window: <code>wayland</code>, <code>libxkbcommon</code>, <code>wayland-protocols</code>. For the GPU renderer: <code>mesa</code> (EGL, GLES2).</li>
<li><code>fontconfig</code>, optional. Without it only the Latin letters of the bundled Selawik fonts are drawn.</li>
</ul>
<pre><code>sudo pacman -S --needed base-devel cmake ninja pkgconf freetype2 libpng fontconfig mesa wayland libxkbcommon wayland-protocols</code></pre>
<h2 id="first">Your first app</h2>
<p>There is no top-level <code>CMakeLists.txt</code>. Each part is its own CMake project. An example pulls in <code>../../zrnapp</code>, and zrnapp pulls in <code>../zrnui</code>.</p>
<pre><code>git clone https://github.com/Zerone-Laboratories/zrn-sdk
cd zrn-sdk/examples/helloworld
cmake --preset host-debug             <span class="c"># configure first</span>
cmake --build --preset host-debug
./build/host-debug/helloworld</code></pre>
<p>This is <code>examples/helloworld/hello.c</code>:</p>
<pre><code>{{HELLO}}</code></pre>
<p><code>examples/demoapp</code> is a tour of the controls, with pages for buttons, text, a Pivot and a Hub.</p>
<h2 id="handles">Handles</h2>
<p>Every object is a <code>Zid</code>, a 32-bit handle. A handle holds an index and a generation, so a handle of a destroyed object is caught and reported, not a crash. <code>Z_INVALID_ID</code> (0) is never valid. A create function returns it on failure. The reason is in <code>Zget_error()</code> and <code>Zget_error_message()</code>.</p>
<p>A parent owns its children. <code>Zelement_destroy</code> destroys an element and everything under it. Nothing in the library is thread-safe: use it from one thread.</p>
<h2 id="life">The life cycle</h2>
<pre><code>if (!Zinit()) return 1;           <span class="c">// fonts, theme, $ZRNUI_* settings</span>
Zid root = Zroot_create();        <span class="c">// a root hosts one visual tree</span>
Zroot_set_visual(root, frame);    <span class="c">// the root owns it</span>
Zwindow_run_ex(root, &amp;options);   <span class="c">// zrnapp: window and event loop</span>
Zroot_destroy(root);
Zshutdown();</code></pre>
<p><code>Zinit</code> returns false when the fonts cannot be loaded. <code>Zinit</code> and <code>Zshutdown</code> are counted. A root has a size, a theme, an accent and a renderer.</p>
<h2 id="tree">Building a tree</h2>
<p>Create with <code>Z&lt;class&gt;_create</code>, set properties with <code>Z&lt;class&gt;_set_&lt;property&gt;</code>, and add to a parent.</p>
<div class="table-wrap"><table>
<tr><th>Parent</th><th>How to add a child</th></tr>
<tr><td>A panel: StackPanel, Grid, Canvas</td><td><code>Zpanel_add(panel, child)</code></td></tr>
<tr><td>A content control: Button, Page, ScrollViewer</td><td><code>Z..._set_content(control, child)</code></td></tr>
<tr><td>An items control: ListView, ComboBox</td><td><code>Zitems_control_add</code>, <code>Zitems_control_add_text</code></td></tr>
</table></div>
<p>Sizes are logical pixels on a 480 x 800 grid. The shell's scale enlarges the picture, not the grid.</p>
<h2 id="pages">Pages and Back</h2>
<p>An app is normally a <code>Frame</code> that shows <code>Page</code>s. A page is made by a factory function, so the frame can build it again on the way back: <code>Zframe_navigate(frame, factory, parameter)</code>, then <code>Zframe_go_back(frame)</code>. The shell already places the window below its status bar, so a Frame starts at the top (set <code>ZRNUI_SAFE_AREA_TOP</code> to reserve room yourself).</p>
<p>Back (Escape on a keyboard) closes the top popup, flyout or dialog, else an open app bar, else goes back in the Frame. On the first page zrnapp closes the window.</p>
<h2 id="events">Events</h2>
<p>Use the typed helper when there is one, such as <code>Zbutton_on_click</code>, or <code>Zelement_on(element, Z_EVENT_..., callback, user_data)</code>. A callback is <code>void callback(Zid sender, void* user_data)</code>. Read the new state from the sender. A handler may destroy its own control or navigate away.</p>
<pre><code>static void on_click(const Zid sender, void* const user_data) {
    Zroot_back((Zid)(uintptr_t)user_data);
}
Zbutton_on_click(button, on_click, (void*)(uintptr_t)root);</code></pre>
<h2 id="time">Time</h2>
<p>Animations, the caret, repeat buttons, scrolling inertia and tooltips move only through <code>Zroot_tick(root, dt_ms)</code>. zrnapp calls it about every 16 ms.</p>
<h2 id="next">Next</h2>
<p><a href="/elements">UI elements</a> shows what you can put on a page. <a href="/shipping">Build and ship</a> shows how to run it on a phone.</p>
"""),

"apps": ("Ways to make an app: ztOS SDK", "C, C++, or zrnui embedded in your own shell: the ways to use zrnSDK v2, and the older Python and Qt SDK.", """
<h1>Ways to make an app</h1>
<p class="lead"><b>Write C against zrnui and zrnapp.</b> That is the only supported way in SDK v2.</p>
<div class="table-wrap"><table>
<tr><th>Way</th><th>Links</th><th>Status</th></tr>
<tr><td>C23, an ordinary Wayland app</td><td>zrnui and zrnapp</td><td>Supported. Runs on a laptop and on a phone</td></tr>
<tr><td>C++, including the C headers</td><td>zrnui and zrnapp</td><td>Works. No C++ wrapper</td></tr>
<tr><td>zrnui inside your own shell</td><td>zrnui only</td><td>Supported. You drive input, time and frames</td></tr>
<tr><td>Python, Rust</td><td>-</td><td>No bindings in v2</td></tr>
<tr><td>Older Python SDK, <code>ztos</code></td><td>Qt</td><td>Older. Part of the ztOS tree, not of zrn-sdk</td></tr>
</table></div>
<h2 id="libs">The two libraries</h2>
<div class="table-wrap"><table>
<tr><th>Library</th><th>What it is</th></tr>
<tr><td><b>zrnui</b></td><td>The element tree, layout, every control, theme, text, and two painters: software and OpenGL ES 2. It opens no window and has no event loop.</td></tr>
<tr><td><b>zrnapp</b></td><td>A Wayland window on top of zrnui: the event loop, pointer, touch and keyboard, the shell's scale, and frames to the compositor.</td></tr>
<tr><td><b>zrnkit</b></td><td>A metapackage that installs both.</td></tr>
</table></div>
<p>There is no umbrella <code>zrnui.h</code>. Include what you use: <code>zrnui/controls.h</code>, <code>zrnui/host.h</code>, and <code>zrnapp.h</code>. Each header includes the one it builds on.</p>
<h2 id="cpp">From C++</h2>
<p>The headers are plain C. A C++ program includes them as they are. C23 <code>nullptr</code> and <code>constexpr</code> are inside the library, not in the headers you call.</p>
<pre><code>#include &lt;zrnapp.h&gt;
#include &lt;zrnui/controls.h&gt;
#include &lt;zrnui/host.h&gt;</code></pre>
<p>A callback is a plain function pointer. A capturing lambda does not convert to one: pass state through <code>user_data</code>.</p>
<h2 id="embed">Inside your own shell</h2>
<p>Link zrnui alone. Your loop injects input, ticks time and takes frames.</p>
<pre><code>ZConfig config;
Zconfig_default(&amp;config);
config.font_directory = "/usr/share/fonts/zrnui/selawik";
if (!Zinit_ex(&amp;config)) return 1;

const Zid root = Zroot_create();
Zroot_set_size(root, 480, 800);
Zroot_set_visual(root, page);

for (;;) {
    Zroot_inject_pointer(root, Z_POINTER_DOWN, x, y);
    Zroot_tick(root, dt_ms);
    ZFrame frame = {0};
    if (Zroot_render(root, &amp;frame)) present(frame.pixels, frame.width, frame.height, frame.stride);
}</code></pre>
<p>A frame is 8-bit RGBA, top row first, owned by the root until the next render. This is how the pictures on this site are made. <code>zrnui/docs/embedding.md</code> has the GPU target and input details.</p>
<h2 id="old">The older Python SDK <span class="tag dashed">older</span></h2>
<p>In the ztOS repository at <code>sdk/</code>: Python with Qt (PySide6), Metro look only, run with <code>ztos-sdk run</code> and put on the phone with <code>ztos-sdk deploy</code>. It is not part of zrn-sdk and is not covered here.</p>
"""),

"project": ("Project layout: ztOS SDK", "How a zrnSDK v2 app is laid out: CMake, the four presets, the app id, installing, and the licences.", """
<h1>Project layout</h1>
<p class="lead">An app is <b>a CMake project</b> with a <code>CMakePresets.json</code>. The store reads <code>zrnapp.toml</code> (app id, version, permissions, <code>[build] sdk = 2</code>); see <a href="/publish">Publish to the store</a>.</p>
<h2 id="cmake">CMakeLists.txt</h2>
<p>This is the whole of <code>examples/helloworld/CMakeLists.txt</code>:</p>
<pre><code>cmake_minimum_required(VERSION 3.16)
project(helloworld C)

set(CMAKE_C_STANDARD 23)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

add_subdirectory(../../zrnapp ${CMAKE_BINARY_DIR}/zrnapp)

add_executable(helloworld hello.c)
target_link_libraries(helloworld PRIVATE zrnapp::zrnapp zrnui::zrnui)</code></pre>
<p>Outside the checkout, point <code>add_subdirectory</code> at your copy of <code>zrn-sdk/zrnapp</code>. With an installed SDK use pkg-config instead:</p>
<pre><code>cc -std=c23 app.c $(pkg-config --cflags --libs zrnapp zrnui) -o app</code></pre>
<p>Or in CMake: <code>pkg_check_modules(ZRN REQUIRED IMPORTED_TARGET zrnapp zrnui)</code> and link <code>PkgConfig::ZRN</code>. There is no CMake package file.</p>
<h2 id="presets">Presets</h2>
<div class="table-wrap"><table>
<tr><th>Preset</th><th>For</th><th>Build directory</th></tr>
<tr><td><code>host-debug</code>, <code>host-release</code></td><td>This computer</td><td><code>build/host-&lt;type&gt;</code></td></tr>
<tr><td><code>phone-debug</code>, <code>phone-release</code></td><td>A phone (aarch64 Arch Linux ARM), cross build with clang and a sysroot. zrnui and zrnapp are linked statically, no tests</td><td><code>build/phone-&lt;type&gt;</code></td></tr>
</table></div>
<p>Copy <code>CMakePresets.json</code> from an example. Its phone presets point at <code>../../cmake/toolchain-aarch64.cmake</code>, so fix that path if your app lives elsewhere. Your own presets go in <code>CMakeUserPresets.json</code>. CLion, VS Code, Qt Creator and Visual Studio read the presets.</p>
<h2 id="id">The app id</h2>
<p>The shell matches a window to its <code>.desktop</code> file by app id. zrnapp takes it from <code>ZWindowOptions.app_id</code>, else <code>$ZRNAPP_APP_ID</code>, else the file name of the executable. The title in <code>ZWindowOptions.title</code> is for people.</p>
<pre><code>const ZWindowOptions window = { .title = "Notes", .app_id = "zrn-notes" };
Zwindow_run_ex(root, &amp;window);</code></pre>
<h2 id="install">Installing the SDK</h2>
<pre><code>cmake --install zrnui/build --prefix /usr/local
cmake --install zrnapp/build --prefix /usr/local     <span class="c"># configured with -DZRNAPP_SYSTEM_ZRNUI=ON</span></code></pre>
<p>On Arch Linux each part has a <code>PKGBUILD</code>. Build <code>zrnui</code> first, then <code>zrnapp</code>.</p>
<h2 id="licence">Licences</h2>
<div class="table-wrap"><table>
<tr><th>What</th><th>Licence</th></tr>
<tr><td>zrnui, zrnapp, zrnkit</td><td>LGPL-2.1-or-later: apps under any licence can link them</td></tr>
<tr><td><code>tools/</code></td><td>GPL-2.0-or-later</td></tr>
<tr><td><code>examples/</code></td><td>MIT: copy them into your app</td></tr>
<tr><td>Selawik fonts</td><td>SIL Open Font License 1.1</td></tr>
</table></div>
"""),

"elements": ("UI elements: ztOS SDK", "Every zrnSDK v2 control on this site, drawn by zrnui's GLES2 renderer at phone size in Dark and Light, with the C that drew it.", """
<h1>UI elements</h1>
<p class="lead">Each picture below was drawn by the C under it. It ran against zrnui (the pinned commit plus the uncommitted working tree), with the GLES2 renderer, on a page 360 points wide: the S9's width under the ztOS shell. Each picture is shown at that size.</p>
<p>The snippets are the body of <code>build(root, page, stack)</code>. <code>stack</code> is a vertical StackPanel, already the page's content, with the margin 19, 32, 19, 0. The full programs are in <a href="https://github.com/Zerone-Laboratories/zrn-sdk-site/tree/main/proof">proof/</a>.</p>
<p>The pictures are still: motion is on <a href="/animations">Animations</a>. Pictures are cut below the content. More controls exist than are pictured: RichTextBlock, Image, RepeatButton, AutoSuggestBox, GridView, FlipView, SemanticZoom, Flyout, MenuFlyout, ToolTip, ScrollViewer and the panels. Their pages are in <code>zrnui/docs/</code>.</p>
{{ELEMENTS}}
"""),

"layout": ("Layout and theme: ztOS SDK", "zrnui's XAML layout, panels, Dark and Light themes, the 20 accents, theme.ini, theme resources, fonts and renderers.", """
<h1>Layout and theme</h1>
<p class="lead">Layout is the one of XAML: <b>measure, then arrange</b>. Colours come from the theme and the accent, as on Windows Phone 8.1.</p>
<h2 id="layout">Layout</h2>
<p>Every element has <code>Margin</code>, <code>Width</code>, <code>Height</code>, minimum and maximum sizes, and horizontal and vertical alignment. <code>Zthickness(left, top, right, bottom)</code> makes a margin.</p>
<div class="table-wrap"><table>
<tr><th>Panel</th><th>What it does</th></tr>
<tr><td>StackPanel</td><td>One child after another, vertical or horizontal</td></tr>
<tr><td>VirtualizingStackPanel, ItemsWrapGrid</td><td>The panels of long lists and grids</td></tr>
<tr><td>WrapPanel</td><td>Children in lines that wrap</td></tr>
<tr><td>Grid</td><td>Rows and columns: Auto, pixels, or star shares</td></tr>
<tr><td>Canvas</td><td>Children at fixed positions</td></tr>
<tr><td>Border</td><td>A background, an edge and padding around one child</td></tr>
<tr><td>Viewbox</td><td>Scales one child to fit</td></tr>
<tr><td>Popup</td><td>Shows above the tree</td></tr>
</table></div>
<p>The actual size of an element is known after a layout. Call <code>Zroot_update_layout(root)</code> if you need it before the first frame.</p>
<h2 id="theme">Theme and accent</h2>
{{SHOTS:toggles}}
<pre><code>Zroot_set_theme(root, Z_THEME_LIGHT);
Zroot_set_accent(root, Z_ACCENT_ORANGE);
Zroot_set_accent_color(root, Zcolor_argb(0xFF1BA1E2));   <span class="c">// or any colour</span></code></pre>
<p>Dark is the default. The 20 accents are Lime, Green, Emerald, Teal, Cyan, <b>Cobalt</b> (the default), Indigo, Violet, Pink, Magenta, Crimson, Red, Orange, Amber, Yellow, Brown, Olive, Steel, Mauve and Taupe. A theme change cross-fades over a quarter of a second when animations run.</p>
<h2 id="ini">theme.ini</h2>
<p>The colours of both themes live in <code>zrnui/theme/theme.ini</code>, as <code>Name = #AARRGGBB</code> in the sections <code>[accent]</code>, <code>[dark]</code> and <code>[light]</code>. A missing key keeps the built-in value. The file is looked for in <code>ZConfig.theme_file</code> or <code>$ZRNUI_THEME</code>, then next to the binary, then the compiled-in path.</p>
<h2 id="res">Theme resources</h2>
<p><code>resources.h</code> lists the 491 keys of Windows Phone 8.1's <code>themeresources.xaml</code>, such as <code>Z_RES_PHONE_FOREGROUND_BRUSH</code>. Read them with <code>Zroot_get_theme_color</code> and friends. Override one with <code>Zroot_set_resource_color</code>. Make a property follow a key with a <code>_bind_</code> call, so it changes with the theme.</p>
<pre><code>Zborder_bind_background(tile, Z_RES_PHONE_ACCENT_BRUSH);   <span class="c">// follows the accent</span></code></pre>
<h2 id="fonts">Fonts</h2>
<p>The bundled Selawik fonts stand in for Segoe WP. They hold Latin only. With fontconfig, other scripts are drawn with a system font that has the character. The font directory is <code>ZConfig.font_directory</code> or <code>$ZRNUI_FONT_DIR</code>, then <code>Zset_font_directory</code>, then the compiled-in path.</p>
<h2 id="renderer">Renderers</h2>
<div class="table-wrap"><table>
<tr><th>Setting</th><th>Values</th><th>Notes</th></tr>
<tr><td><code>Zroot_set_renderer</code>, <code>$ZRNUI_RENDERER</code></td><td>auto, software, gpu</td><td>Auto uses OpenGL ES 2 when it can. Software never touches the GPU</td></tr>
<tr><td><code>Zroot_set_animations</code>, <code>$ZRNUI_ANIMATIONS</code></td><td>auto, on, off</td><td>Auto runs animations only with the GPU renderer</td></tr>
<tr><td><code>$ZRNUI_ANIMATION_SPEED</code></td><td>a number</td><td>0.5 is half as fast, 2 twice as fast</td></tr>
<tr><td><code>Zroot_set_scale</code>, <code>$ZRNAPP_SCALE</code></td><td>a number</td><td>720 x 1280 at 1.5 is laid out as 480 x 800</td></tr>
</table></div>
<p>Only <code>Zinit</code> reads the <code>ZRNUI_*</code> variables. <code>Zinit_ex</code> with your own <code>ZConfig</code> ignores them.</p>
"""),

"animations": ("Animations: ztOS SDK", "The animations in zrnSDK v2: the turnstile page transition, the pivot slide, tilt, app bar and switch motion, and Zelement_animate with its easing curves.", """
<h1>Animations</h1>
<p class="lead">Animations run only with the <b>GPU renderer</b>, unless <code>Zroot_set_animations</code> forces them. With the software renderer every change happens at once. Time moves only through <code>Zroot_tick</code>.</p>
<p>Each clip below is a <b>recording of zrnui itself</b>, from the working tree on top of the pinned commit: the GLES2 renderer offscreen, time moved by <code>Zroot_tick</code> in steps of 1/60 s, every frame read back, input injected as a finger. The program is <code>gen/anim.c</code>. Clips loop with a short pause.</p>
<h2 id="turnstile">Turnstile: forward, then back</h2>
{{CLIP:turnstile}}
<h2 id="pivot">Pivot slide</h2>
<p>Taps on the headers. Each slide takes 300 ms.</p>
{{CLIP:pivot}}
<h2 id="tilt">Tilt</h2>
<p>A finger held on a list item near its left edge, then near its right edge. The item leans toward it.</p>
{{CLIP:tilt}}
<h2 id="appbar">App bar</h2>
{{CLIP:appbar}}
<h2 id="toggle">Toggle switch</h2>
{{CLIP:toggle}}
<h2 id="theme-change">Theme change</h2>
<p><code>Zroot_set_theme</code> to the other theme and back. The colours cross-fade.</p>
{{CLIP:theme}}
<h2 id="hub">Hub parallax</h2>
<p>Two drags to the left, then <code>Zhub_scroll_to_section(hub, 0)</code>. The header moves at half the speed of the sections.</p>
{{CLIP:hub}}
<h2 id="frost">zrn-frosted-diffusion <span class="tag dashed">uncommitted</span></h2>
<p>Recorded from the uncommitted zrn-sdk working tree, like the other clips; the pinned commit does not have it. A frosted bar over scrolling rows, in NORMAL, then ASCENDING, then DESCENDING. See <a href="/next#frost">Coming next</a>.</p>
{{CLIP:frost}}
<p>Continuum and slide-up transitions are not in the pinned commit, so there is no clip of them.</p>
<h2 id="numbers">The numbers</h2>
<div class="table-wrap"><table>
<tr><th>Animation</th><th>What it does</th><th>Numbers</th><th>Where</th></tr>
<tr><td>Turnstile</td><td>The leaving page's rows turn away round the left edge, one after another. Then the new page's rows swing in</td><td>706 ms in all. The old page goes at about 330 ms</td><td><code>zrnui/docs/navigation.md</code></td></tr>
<tr><td>Pivot slide</td><td>Pages and headers move together. Release past a fifth of a page, or a flick, goes on</td><td>300 ms</td><td><code>zrnui/docs/navigation.md</code></td></tr>
<tr><td>Tilt</td><td>A pressed element leans toward the finger</td><td>14 degrees, in 90 ms, out 160 ms</td><td><code>zrnui/src/anim.c</code></td></tr>
<tr><td>App bar</td><td>Opens over the page and shows labels</td><td>167 ms</td><td><code>zrnui/docs/app-bars-and-icons.md</code></td></tr>
<tr><td>Toggle switch</td><td>The knob slides</td><td>180 ms</td><td><code>zrnui/docs/buttons.md</code></td></tr>
<tr><td>Theme change</td><td>Colours cross-fade</td><td>A quarter of a second</td><td><code>zrnui/include/zrnui/host.h</code></td></tr>
<tr><td>Hub</td><td>The header moves at half the speed of the sections</td><td>Parallax 0.5</td><td><code>zrnui/include/zrnui/controls.h</code></td></tr>
</table></div>
<h2 id="frame">Page transitions</h2>
<pre><code>Zframe_set_transition(frame, Z_TRANSITION_TURNSTILE);   <span class="c">// the default</span>
Zframe_set_transition(frame, Z_TRANSITION_NONE);</code></pre>
<p>It takes effect from the next navigation. A Navigate or GoBack during a transition ends it at once. <code>Zframe_is_transitioning</code> says whether one runs.</p>
<h2 id="animate">Animate an element</h2>
<pre><code>void fade_in(Zid element) {
    Zelement_set_opacity(element, 0.0f);
    Zelement_animate(element, Z_PROP_OPACITY, 1.0f, 300.0f, Z_EASE_OUT, 0.0f);
}</code></pre>
<p><code>Zelement_animate(element, property, to, duration_ms, easing, delay_ms)</code> moves a property from where it is now. A new animation of the same property replaces the running one. With animations off, the property jumps.</p>
<p>Properties: <code>Z_PROP_OPACITY</code>, <code>Z_PROP_ROTATION_X</code>, <code>Z_PROP_ROTATION_Y</code> (degrees), <code>Z_PROP_SCALE</code>, <code>Z_PROP_TRANSLATE_X</code>, <code>Z_PROP_TRANSLATE_Y</code>.</p>
<div class="table-wrap"><table>
<tr><th>Easing</th><th>Curve</th></tr>
<tr><td><code>Z_EASE_LINEAR</code></td><td>Linear</td></tr>
<tr><td><code>Z_EASE_OUT</code></td><td>Cubic: quick start, soft end</td></tr>
<tr><td><code>Z_EASE_IN</code></td><td>Cubic: slow start</td></tr>
<tr><td><code>Z_EASE_EMPHASIZED</code></td><td>Cubic Bezier (0.2, 0.8, 0.2, 1): quick start, long soft settle</td></tr>
</table></div>
<h2 id="transform">Render transforms</h2>
<p><code>Zelement_set_projection</code> (a PlaneProjection), <code>Zelement_set_render_scale</code> and <code>Zelement_set_translate</code> change how an element is drawn, not its layout. Only the GPU renderer draws them. A transformed element is still hit where layout put it.</p>
<p><code>Zelement_set_tilt(element, on)</code> turns tilt on or off. It is on by default for list and grid items, group headers, hyperlinks, check boxes, radio buttons and menu items. It is off for Button.</p>
"""),

"shell": ("How the shell draws: ztOS SDK", "How ztMETRO, the ztOS Mobile shell, puts a frame together: ten layers drawn bottom to top on the GPU, the order that keeps calls and volume on top, and what it means for your app.", """
<h1>How the shell draws</h1>
<p class="lead">ztMETRO is the shell and the Wayland compositor in one. Every frame it draws the whole screen in <b>one GLES2 pass</b>, layer by layer, <b>bottom to top</b>, in a fixed order. Your app is one of those layers. Below, layer 01 is in front, because it is painted first, and each later layer stands further back.</p>
{{STACK}}
<h2 id="picture">The picture</h2>
<p>The same layers as one picture, with what they mean. Open it for the full size.</p>
{{LAYERS}}
<p class="note">The layers are screenshots of ztMETRO on a Galaxy S9, cut apart along the shell's own lines (status bar 28 points, nav bar 40). Wi-Fi network and carrier names are covered, and the notification in the action centre is replaced with a demo one. The call screen is not a capture: it is drawn with zrnui by <code>gen/layers.c</code>, because we do not place a real call for a picture. The order and the names come from <code>render_frame</code> in <code>ztmetro/ztmetro.c</code> (ztOSMobile, read on 21 November 2026).</p>
<h2 id="clip">Apart and back</h2>
<p>The frame you see comes apart into its ten layers and folds back. Start is built from its tiles, each its own texture in the shell, laid in their places. The clip starts with every layer stacked flat, 01 in front.</p>
{{LAYERCLIP}}
<h2 id="order">The order, bottom to top</h2>
<p>This is the order <code>render_frame</code> draws in; a later layer covers an earlier one. The numbers are the picture's; a dash marks a step that is not in it.</p>
<div class="table-wrap"><table>
<tr><th>#</th><th>Layer</th><th>What the shell draws</th><th>In the code</th></tr>
<tr><td>–</td><td>Background</td><td>The screen is cleared to the shell background (white in Light, black in Dark). Only the gaps between Start's tiles show it</td><td><code>glClear</code>, <code>shell_bg_color</code></td></tr>
<tr><td>01</td><td>Start and the app list</td><td>The tiles, each its own texture, and the list beside them. In the turnstile each tile moves on its own clock. Not drawn at all while an app at rest or the lock screen covers them</td><td><code>tiles</code>, <code>items</code>; skipped when <code>app_covers</code> or <code>lock_covers</code></td></tr>
<tr><td>02</td><td>Frost strips</td><td>What of Start and the list passes under the status bar and the nav bar, blurred into two strips right after Start is drawn, and blurred again only when what is under them changes. Each strip is laid on the screen just under its own bar (step 05 and 07), as the bar's backing. Over an app the bars are opaque and there is no frost</td><td><code>frost_prepare</code>, <code>frost[0]</code>, <code>frost[1]</code></td></tr>
<tr><td>03</td><td>App window</td><td>Your window, between the bars. The app's buffer is already a GPU texture; the shell draws it as a quad. Or the switcher's cards, or the launch flip in landscape</td><td><code>draw_app_surface</code>, <code>wlr_surface_get_texture</code></td></tr>
<tr><td>–</td><td>Hyperscan</td><td>The shell's search page, when it is up (not in the picture)</td><td><code>hyper_layer</code></td></tr>
<tr><td>04</td><td>Keyboard</td><td>The on-screen keyboard, sliding up from the nav bar</td><td><code>osk_layer</code></td></tr>
<tr><td>–</td><td>The turn</td><td>While the screen rotates, a picture of the old layout over the new one (not in the picture)</td><td><code>rot_snapshot_draw</code></td></tr>
<tr><td>05</td><td>Status bar</td><td>Signal, battery, clock; the charging plug and the taller row you get by holding it</td><td><code>status_layer</code>, <code>plug_layer</code>, <code>peek_layer</code></td></tr>
<tr><td>06</td><td>Action centre</td><td>The panel pulled down from the top: quick actions and notifications</td><td><code>shade_layer</code></td></tr>
<tr><td>07</td><td>Nav bar</td><td>Back, Start, search. Drawn after the action centre, so the panel comes down behind it</td><td><code>nav_layer</code></td></tr>
<tr><td>08</td><td>Lock screen</td><td>Its picture, clock and notification row. Opaque: while it is fully down, Start and the apps under it are not drawn, and while it slides only the strip below it is</td><td><code>lock_layer</code>, <code>lock_clock_layer</code></td></tr>
<tr><td>09</td><td>Call</td><td>The phone app's window (<code>ztphone</code>) drawn again here, over the lock, with the status row over it</td><td><code>call_over_lock</code></td></tr>
<tr><td>10</td><td>Volume, toasts, dialogs</td><td>The volume banner and a notification toast in the same place at the top, and the shell's dialogs</td><td><code>volume_layer</code>, <code>toast_layer</code>, <code>dialog_layer</code></td></tr>
</table></div>
<p>The boot splash is left out too. One exception to "one pass": when your app is at rest and fills its area, the shell may put its buffer straight on a display plane (<code>plane_pick</code>) instead of drawing it, if the display hardware accepts it.</p>
<h2 id="textures">Textures and what is drawn each frame</h2>
<ul>
<li><b>App windows</b> are textures already: the shell gets your buffer from Wayland and draws it, it does not copy it.</li>
<li><b>The shell's own layers</b> (the bars, the keyboard, the action centre, the lock screen, the banners, each tile) are painted once into a texture and uploaded again only when what they show changes.</li>
<li><b>Each frame</b> the shell only places those textures: a quad each, with the position, turn and fade of the moment. The frost strips are blurred on the GPU only when what is under the bars has changed (every frame only during the turn); the call's frosted backdrop is the other blur.</li>
</ul>
<h2 id="transitions">The shell moves the apps</h2>
<p>Because every app is a layer of the same frame, the shell, not the app, animates going between them: Start's tiles turning away and an app swinging in (the turnstile), an app swinging out on Back, the switcher's cards, the launch flip in landscape, and the turn of the screen. Every app arrives and leaves the same way, and an app needs no code for it.</p>
<h2 id="for-apps">What it means for your app</h2>
<ul>
<li><b>Your window is one textured layer.</b> Draw your whole page into it, at 60 frames a second when it moves. The shell does not draw anything inside it.</li>
<li><b>Your app bar is yours; the keyboard is the shell's.</b> zrnui draws the app bar inside your window, at the bottom of your page. The on-screen keyboard is a shell layer over your window: zrnui gives your page the room it takes (the keyboard inset, see <a href="/next">Coming next</a>).</li>
<li><b>Frost samples what is under it.</b> The shell's frost blurs only Start and the list under its bars; over your app the bars are opaque. A frosted element in your app (<code>Zelement_set_frosted_diffusion</code>) blurs what your own page drew under it, never other apps or the shell.</li>
<li><b>Calls, the nav bar and the volume are always on top.</b> Nothing your app draws can cover them, and you do not need to leave room for the volume banner or a toast: they come and go over you.</li>
<li><b>You do not animate your arrival.</b> Launch, Back and the turn are drawn by the shell. Page transitions inside your app (the turnstile between pages, the pivot) are zrnui's, see <a href="/animations">Animations</a>.</li>
</ul>
"""),

"shipping": ("Build and ship: ztOS SDK", "Cross build a zrnSDK v2 app for an aarch64 phone with the phone-release preset, run it with tools/zrn, and install it. The store's .zexec format 2 is coming.", """
<h1>Build and ship</h1>
<p class="lead">Build on your computer for aarch64, then upload and run on the phone with one script, <b><code>tools/zrn</code></b>. It is <code>cmake</code>, <code>podman</code>, <code>rsync</code> and <code>ssh</code>, nothing more.</p>
<div class="gap"><b>Store packages are coming</b><p>The store's <code>.zexec</code> format 2 for v2 apps is <b>not committed yet</b>. v1's <code>zrn pack</code>, <code>zrn submit</code> and <code>zrn verify</code> are gone. Today a v2 app reaches a phone through <code>tools/zrn run</code>, or as a system package. How the store will take it: <a href="/publish">Publish to the store</a>.</p></div>
<h2 id="once">One time on the computer</h2>
<p>Needs <code>podman</code>, <code>qemu-user-static</code> with binfmt for aarch64, <code>clang</code>, <code>lld</code>, <code>cmake</code>, <code>ninja</code>, <code>rsync</code> and <code>ssh</code>.</p>
<pre><code>tools/zrn sysroot          <span class="c"># an Arch Linux ARM container, exported to ~/.cache/zrn/sysroot</span></code></pre>
<p>It takes some minutes, because the container runs under qemu. The cross build links against this sysroot, so the libraries match the phone's.</p>
<h2 id="key">One time per phone</h2>
<pre><code>tools/zrn -p - setup-key 192.168.7.2     <span class="c"># asks for the password, copies your ssh key</span></code></pre>
<p>The user is <code>alarm</code> unless you give <code>-u</code>. <code>-i</code> picks a key. Nothing is stored: not the password, the user or the host. Use <code>-p -</code> or <code>ZRN_PASSWORD</code>, not a password on the command line.</p>
<h2 id="run">Every time</h2>
<pre><code>tools/zrn run 192.168.7.2 examples/helloworld</code></pre>
<p>This builds with the <code>phone-release</code> preset, uploads the changed bytes, and starts the app over ssh with its output in your terminal. <code>Ctrl-C</code> stops it.</p>
<div class="table-wrap"><table>
<tr><th>Command</th><th>What it does</th></tr>
<tr><td><code>tools/zrn build &lt;dir&gt;</code></td><td>Cross build into <code>&lt;dir&gt;/build/phone-release/</code></td></tr>
<tr><td><code>tools/zrn push &lt;host&gt; &lt;dir&gt;</code></td><td>Upload to <code>~/zrn-dev/&lt;name&gt;/</code>, with the fonts and theme in <code>~/zrn-dev/share/</code></td></tr>
<tr><td><code>tools/zrn run &lt;host&gt; &lt;dir&gt; [args]</code></td><td>Build, push and run. Arguments after the directory go to the app</td></tr>
<tr><td><code>tools/zrn watch &lt;host&gt; &lt;dir&gt;</code></td><td>Run again when a source changes. Needs <code>inotify-tools</code></td></tr>
</table></div>
<p><code>ZRN_HOST</code> makes the host optional. <code>ZRN_PRESET=phone-debug</code> builds a debug binary.</p>
<h2 id="static">Static linking</h2>
<p>The <code>phone-*</code> presets turn off the shared libraries. The app is linked <b>statically</b> with zrnui and zrnapp, so one file goes up. The phone needs only its system libraries: wayland, freetype, mesa. The fonts and <code>theme.ini</code> are passed with <code>ZRNUI_FONT_DIR</code> and <code>ZRNUI_THEME</code>.</p>
<h2 id="pkg">As a system package</h2>
<p>zrnui, zrnapp, zrnkit and demoapp each have a <code>PKGBUILD</code>. <code>makepkg -si</code> in <code>zrnui</code>, then <code>zrnapp</code>, installs the libraries. An app can follow the demoapp <code>PKGBUILD</code>.</p>
<h2 id="zexec">.zexec format 2 <span class="tag dashed">coming</span></h2>
<p>A signed store package for v2 apps. Its layout, signing and submission flow are not in the pinned commit, so this site does not describe them yet.</p>
"""),

"publish": ("Publish to the store: ztOS SDK", "Put a zrnSDK v2 app in the ztOS store: zrnapp.toml, the store's CMake build, submitting on Discord, what CI checks and signs, updates, and what people see.", """
<h1>Publish to the store</h1>
<p class="lead">You never build, sign or upload a package. The store <b>builds your app from your public source</b> at the commit you name, signs it with the store's key and lists it. Nobody merges a pull request to add an app.</p>
<div class="gap"><b>Not live for v2 apps yet</b><p>This page follows the store's working tree (<a href="https://github.com/Zerone-Laboratories/ztOS-apprepo">ztOS-apprepo</a>), not a pinned commit. The store builds v2 apps only once zrn-sdk's v2 work is committed and pinned as <code>commit_v2</code> in its <code>sdk.lock</code>. Today that is all zeros, and a v2 build stops with <code>sdk.lock: no SDK v2 pinned yet</code>.</p></div>
<p>You need <b>no signing key</b>. <code>tools/zrn setup-key</code> copies your <b>ssh</b> key to a phone for <code>tools/zrn run</code>. It has nothing to do with the store.</p>
<h2 id="run">1. Make it work on the phone</h2>
<pre><code>tools/zrn sysroot                              <span class="c"># one time</span>
tools/zrn -p - setup-key 192.168.7.2           <span class="c"># one time per phone: your ssh key</span>
tools/zrn run 192.168.7.2 path/to/your-app     <span class="c"># phone-release build, upload, run</span></code></pre>
<p>See <a href="/shipping">Build and ship</a>. The <code>phone-release</code> preset links zrnui and zrnapp statically.</p>
<h2 id="cmake">2. Let the store build it</h2>
<p>The store does not use the presets. On arm64, inside Arch Linux ARM with only the ztOS image's packages, it runs:</p>
<pre><code>cmake -S &lt;app&gt; -B &lt;app&gt;/build/store -G Ninja -DCMAKE_BUILD_TYPE=Release \\
      -DZRN_SDK_DIR=&lt;zrn-sdk at sdk.lock commit_v2&gt; \\
      -DZRNUI_BUILD_SHARED=OFF -DZRNAPP_BUILD_SHARED=OFF \\
      -DZRNUI_BUILD_TESTS=OFF -DZRNAPP_BUILD_TESTS=OFF
cmake --build &lt;app&gt;/build/store</code></pre>
<ol>
<li>Take the SDK from <code>ZRN_SDK_DIR</code>. The examples use a fixed <code>../../zrnapp</code>. A store app does this instead (below).</li>
<li>Put the program at the top of the build folder, named as <code>[build] target</code> says.</li>
<li>Link only what the image has. <code>ci/check-linkage.py</code> fails on any library <code>ldd</code> cannot find, and on a shared <code>libzrnui</code> or <code>libzrnapp</code>.</li>
<li>Download nothing during the build.</li>
</ol>
<pre><code>set(ZRN_SDK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../zrn-sdk" CACHE PATH "zrn-sdk checkout")
add_subdirectory(${ZRN_SDK_DIR}/zrnapp ${CMAKE_BINARY_DIR}/zrnapp)
add_executable(notes main.c)
target_link_libraries(notes PRIVATE zrnapp::zrnapp zrnui::zrnui)</code></pre>
<h2 id="toml">3. Write zrnapp.toml</h2>
<p>In the app folder. The store reads it at the commit you submit.</p>
<pre><code>[app]
id = "io.github.alice.notes"     <span class="c"># never changes</span>
name = "Notes"
version = "1.0.0"                <span class="c"># semantic, higher than any listed</span>
summary = "Short notes"
author = "Alice"
licence = "MIT"                  <span class="c"># an SPDX id</span>
icon = "icon.svg"
categories = ["Utility"]
permissions = ["network"]
data_dirs = ["notes"]            <span class="c"># optional: removed on uninstall</span>

[build]
sdk = 2
target = "notes"                 <span class="c"># default: the id</span>
data = ["data/*.png"]            <span class="c"># optional, packed under share/</span></code></pre>
<p><b>The id</b> is reverse DNS you control, at least three parts, lower case. <code>zrn-</code> ids are for Zerone Laboratories' own repositories. The app list matches your window by <code>StartupWMClass=&lt;id&gt;</code>, so give the window the same id: <code>{ .title = "Notes", .app_id = "io.github.alice.notes" }</code>.</p>
<p><b>Permissions</b>: <code>network</code>, <code>audio</code>, <code>camera</code>, <code>location</code>, <code>notifications</code>, <code>bluetooth</code>, <code>phone</code>, <code>contacts</code>, <code>messages</code>, <code>background</code>, <code>files.music</code>, <code>files.pictures</code>, <code>files.documents</code>, <code>files.downloads</code>. Ask for what you use, nothing else. Login services are <code>[[service]]</code> tables and need <code>background</code>. Never write systemd units yourself.</p>
<h2 id="version">4. Raise the version</h2>
<p>Each submission needs a version that is not in the store yet. The relay refuses a version it already has. The build stops if <code>zrnapp.toml</code> at the commit names another id or version.</p>
<h2 id="check">5. Check the package (optional)</h2>
<p>Run the store's own build with a ledger entry of your own, from a checkout of ztOS-apprepo. Write <code>/tmp/ledger/io.github.alice.notes.toml</code>:</p>
<pre><code>id = "io.github.alice.notes"
source = "https://github.com/alice/notes"
subdir = ""
[[release]]
version = "1.0.0"
commit = "&lt;the 40-hex SHA&gt;"
status = "approved"
approved_by = "discord:0"
approved_at = "2026-01-01T00:00:00Z"</code></pre>
<p>Then build and look at the package:</p>
<pre><code>STORE_LEDGER=/tmp/ledger ZRN_SDK2=/path/to/zrn-sdk \\
  python3 tools/store.py build --id io.github.alice.notes --version 1.0.0 --out out \\
  --source-override "https://github.com/alice/notes=/path/to/your/clone"
python3 client/zrn info out/*.zexec      <span class="c"># manifest and files</span>
python3 client/zrn verify out/*.zexec    <span class="c"># structure; no signature is expected</span></code></pre>
<p>The package is built for your CPU (x86_64 on a laptop; the store builds aarch64) and is <b>not signed</b>, so the phone's <code>zrn install</code> refuses it. Test on the phone with <code>tools/zrn run</code>.</p>
<h2 id="submit">6. Submit</h2>
<ol>
<li>Commit and push to a <b>public GitHub repository</b>.</li>
<li>On the ztOS Mobile Discord: <code>/submit-app repo:https://github.com/alice/notes commit:&lt;40-hex SHA&gt; [subdir:app]</code>. The relay checks the repository is public, the commit exists and <code>zrnapp.toml</code> agrees, then opens a post in <b>#ztos-app-submissions</b>. SDK v1's <code>zrn submit</code> is not in v2.</li>
<li>A moderator reads the source at that commit and presses <b>Accept</b> or <b>Reject</b>.</li>
</ol>
<h2 id="ci">7. After Accept</h2>
<ol>
<li>The bot adds an approved <code>[[release]]</code> to <code>ledger/&lt;id&gt;.toml</code> and starts <code>publish.yml</code>.</li>
<li><b>plan</b>: approved releases with nothing published.</li>
<li><b>build</b>, on arm64, with no secrets: your exact commit, zrn-sdk at <code>sdk.lock</code>, the CMake build, the linkage check.</li>
<li><b>publish</b>, the only job with the store key: checks each package against the ledger, signs it (<code>.zexec.minisig</code>), uploads both to the release <code>&lt;id&gt;-&lt;version&gt;</code>, and writes a signed <code>index.json</code> on the <code>store-index</code> branch.</li>
</ol>
<p>A failed build leaves that release out and fails the run.</p>
<h2 id="updates">8. Updates</h2>
<p>Raise <code>version</code>, commit, push, <code>/submit-app</code> the new commit. Moderators see a compare link from your last approved commit. The store never follows a branch.</p>
<h2 id="users">9. What people see</h2>
<ul>
<li>The store lists the app from the signed index. A higher listed version shows as an update.</li>
<li>Install or update checks the signature, the sha256 and the id, version and arch, then puts the package at <code>~/.local/share/zrn/apps/&lt;id&gt;/&lt;id&gt;.zexec</code> and adds the app to the list. <b>An update never deletes the app's data.</b></li>
<li>Uninstall asks first, then removes the app, its services and its data, unless <code>--keep-data</code>.</li>
<li>A revoked release is disabled on phones, with the reason shown.</li>
</ul>
<p>The full write-up, with file references, is <code>docs/publishing.md</code> in zrn-sdk.</p>
"""),
"troubleshooting": ("Troubleshooting: ztOS SDK", "Real zrnSDK v2 build and run errors and what to do about them.", """
<h1>Troubleshooting</h1>
<p class="lead">Errors as the tools print them, and the fix.</p>
<div class="table-wrap"><table>
<tr><th>You see</th><th>Do this</th></tr>
<tr><td><code>cmake --build --preset ...</code> says the build directory does not exist</td><td>Configure first: <code>cmake --preset host-debug</code></td></tr>
<tr><td>Errors about <code>nullptr</code>, <code>constexpr</code> or <code>auto</code></td><td>The compiler is too old for C23. Use GCC 13+ or Clang 19+</td></tr>
<tr><td><code>zrn: which project? e.g. examples/helloworld</code></td><td>Give the project folder after the host</td></tr>
<tr><td><code>zrn: ... has no CMakePresets.json</code></td><td>Copy <code>CMakePresets.json</code> from an example into your project</td></tr>
<tr><td><code>zrn: which device? ...</code></td><td>Give the phone's address, or set <code>ZRN_HOST</code></td></tr>
<tr><td><code>no aarch64 sysroot at ...</code></td><td>Run <code>tools/zrn sysroot</code></td></tr>
<tr><td><code>exec format error</code> while the sysroot builds</td><td>Register binfmt for aarch64 (<code>qemu-user-static-binfmt</code>)</td></tr>
<tr><td><code>Permission denied (publickey)</code></td><td><code>tools/zrn -p - setup-key &lt;host&gt;</code></td></tr>
<tr><td><code>REMOTE HOST IDENTIFICATION HAS CHANGED</code></td><td>The phone was reflashed: <code>ssh-keygen -R &lt;host&gt;</code></td></tr>
<tr><td><code>Permission denied</code> when the app starts on the phone</td><td>Home is mounted <code>noexec</code>: set <code>ZRN_REMOTE_DIR</code> elsewhere</td></tr>
<tr><td><code>no Wayland socket in /run/user/...</code></td><td>Log in on the phone, or set <code>ZRN_WAYLAND_DISPLAY</code></td></tr>
<tr><td>Text shows as boxes</td><td>The fonts were not found. Check <code>ZRNUI_FONT_DIR</code>, or <code>~/zrn-dev/share/fonts</code> on the phone</td></tr>
<tr><td>Only Latin letters draw</td><td>Build with fontconfig</td></tr>
<tr><td><code>Zinit</code> returns false</td><td>The fonts could not load. Print <code>Zget_error_message()</code></td></tr>
<tr><td><code>Zwindow_run_ex</code> returns false at once</td><td>No Wayland session, or an invalid root. Print <code>Zget_error_message()</code></td></tr>
<tr><td>Nothing animates</td><td>The software renderer is in use. Animations need the GPU renderer, or <code>ZRNUI_ANIMATIONS=on</code></td></tr>
<tr><td>A rotation or slide is ignored</td><td>Render transforms are drawn only by the GPU renderer</td></tr>
</table></div>
"""),

"status": ("Status and gaps: ztOS SDK", "What zrnSDK v2 does not do yet, and what this site has not proven.", """
<h1>Status and gaps</h1>
<p class="lead">What v2 does not do at the pinned commit, and what this site did not check.</p>
<h2 id="sdk">The SDK</h2>
<ul>
<li><b>C only.</b> No Python or Rust bindings, no C++ wrapper.</li>
<li><b>No store package yet.</b> <code>.zexec</code> format 2 is coming. There is no <code>zrn pack</code>, <code>verify</code>, <code>install</code> or <code>submit</code>.</li>
<li><b>No picture tool.</b> v1's <code>zrn render</code> is gone. Draw offscreen with <code>Zroot_render</code>, as this site does.</li>
<li>Not included from WP 8.1, as the headers list them: dialog Closing, FullSizeDesired, TitleTemplate; hub background parallax, section header templates, DefaultSectionIndex.</li>
<li>Selawik is Latin only. Other scripts need fontconfig and a system font.</li>
</ul>
<h2 id="site">This site</h2>
<ul>
<li>The pictures and clips come from zrnui's GLES2 renderer through <b>Mesa on a laptop</b>, not from a phone's GPU. Small differences are possible.</li>
<li>Pictures are drawn at 3 device pixels a point, clips at 2. The S9 draws at 4.</li>
<li>The table of animation numbers is read from source and docs, not measured on a phone.</li>
<li><code>tools/zrn run</code> was not run for this site: no phone was used.</li>
</ul>
"""),

"next": ("Coming next: ztOS SDK", "Work on zrnSDK that is not committed yet: live theme following, Holding and flyouts, new transitions, keyboard inset, cached rows, colour emoji and more.", """
<h1>Coming next</h1>
<p class="lead">This work is in progress in zrn-sdk but <b>not in the pinned commit</b>. Names and behaviour may change. Nothing on this page is documented elsewhere on the site.</p>
<div class="table-wrap"><table>
<tr><th>What</th><th>In short</th></tr>
<tr><td>Live theme following</td><td>Apps follow the system's Dark or Light theme and accent while they run</td></tr>
<tr><td>Holding and flyouts</td><td>A press and hold raises Holding, and can open a flyout</td></tr>
<tr><td>Continuum and slide-up transitions</td><td>More page transitions beside the turnstile</td></tr>
<tr><td>Keyboard inset</td><td>Pages make room for the on-screen keyboard</td></tr>
<tr><td>Cached rows, <code>Z_CACHE_BITMAP</code></td><td>List rows drawn once and reused while scrolling</td></tr>
<tr><td>Colour emoji</td><td>Emoji drawn in colour</td></tr>
<tr><td>Scroll anchoring</td><td>The view stays put when content above it changes</td></tr>
<tr><td>Swipes</td><td>Swipe gestures on list items</td></tr>
<tr><td>zrn-frosted-diffusion</td><td>A frosted, blurred backdrop: NONE, NORMAL, ASCENDING, DESCENDING, and a system-wide switch. <a href="#frost">Pictures below</a></td></tr>
<tr><td><code>.zexec</code> format 2</td><td>Signed store packages for v2 apps</td></tr>
</table></div>
<h2 id="frost">zrn-frosted-diffusion</h2>
<p>What lies behind an element shows through it, blurred and grainy, under a theme tint at 75 %. The element's own text and icons stay sharp on top. App bars, headers and composers are the use.</p>
<pre><code>Zelement_set_frosted_diffusion(bar, Z_FROSTED_DIFFUSION_NORMAL, Z_RES_PHONE_CHROME_BRUSH);
Zset_frosted_diffusion_enabled(false);   <span class="c">// the system-wide switch</span></code></pre>
<p>A <a href="/animations#frost">clip of it over scrolling content</a> is on Animations. These pictures were drawn by zrnui's <b>GLES2 renderer</b>, offscreen through Mesa on a laptop, from the <b>uncommitted working tree</b> on top of 71a5ace. The program is <code>gen/frost.c</code>. A bar 150 px tall lies over the top of coloured rows.</p>
{{FROST}}
<p>The software renderer does not blur: it fills the element with the tint. When the system-wide switch is off (ztOS Settings, theme, frosted diffusion, or <code>frost = 0</code> in <code>~/.config/ztmetro/config</code>), every frosted element paints only its tint, opaque, and nothing is blurred. zrnapp windows follow that switch live. At most 16 elements have the effect at a time.</p>
"""),

"404": ("Not found: ztOS SDK", "That page does not exist.", """
<h1>Not here</h1>
<p class="lead">That page does not exist. Try <a href="/">the overview</a>.</p>
"""),
}
