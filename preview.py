#!/usr/bin/env python3
"""Render README preview images from themes/lull.json.

Writes images/<theme>.svg (an editor mockup per theme) and images/palette.svg,
then renders each to a 2x PNG with headless Google Chrome, if it is installed.
Run `python3 build.py` first so the theme file is current.
"""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).parent
FONT = "'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
UI_FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

# Tags: k keyword, f function, t type, s string, n literal, c comment,
# p property, h inlay hint. Untagged words are variables, symbols punctuation.
CODE = """\
<k>package</k> notes

<k>import</k> <s>"fmt"</s>

<c>// Note is a short piece of text with a title.</c>
<k>type</k> <t>Note</t> <k>struct</k> {
    <p>Title</p>  <t>string</t>
    <p>Body</p>   <t>string</t>
    <p>Pinned</p> <t>bool</t>
}

<c>// Pinned opens a notebook and returns its pinned notes.</c>
<k>func</k> <f>Pinned</f>(path <t>string</t>, limit <t>int</t>) ([]*<t>Note</t>, <t>error</t>) {
    notes, err<h>: []*Note, error</h> := <f>openNotebook</f>(<h>name: </h>path)
    <k>if</k> err != <n>nil</n> {
        <k>return</k> <n>nil</n>, fmt.<f>Errorf</f>(<s>"open %s: %w"</s>, path, err)
    }
    pinned := <f>filter</f>(notes, <k>func</k>(n *<t>Note</t>) <t>bool</t> {
        <k>return</k> n.<p>Pinned</p> && n.<p>Title</p> != <s>""</s>
    })
    <k>return</k> pinned[:<f>min</f>(limit, <f>len</f>(pinned))], <n>nil</n>
}"""

KINDS = {
    "k": "keyword", "f": "function", "t": "type", "s": "string",
    "n": "boolean", "c": "comment", "p": "property", "h": "hint",
}

FILES = ["cmd", "internal", "  notes.go", "  notes_test.go", "  notebook.go",
         "go.mod", "README.md"]


def color(value):
    """Split #rrggbbaa into an SVG color and opacity."""
    if len(value) == 9:
        return value[:7], round(int(value[7:], 16) / 255, 3)
    return value, 1


def fill(value):
    c, o = color(value)
    return f'fill="{c}"' + (f' fill-opacity="{o}"' if o < 1 else "")


def tokens(line):
    for m in re.finditer(r"<(\w)>(.*?)</\1>|([A-Za-z_]\w*)|(\s+)|(.)", line):
        tag, tagged, word, space, sym = m.groups()
        if tag:
            yield KINDS[tag], tagged
        elif word:
            yield "variable", word
        elif space:
            yield None, space
        else:
            yield "punctuation", sym


def editor_svg(theme):
    s = theme["style"]
    syn = s["syntax"]
    w, h = 1200, 720
    title_h, tab_h, status_h, side_w = 38, 36, 28, 232
    line_h, char_w, top = 23, 8.4, title_h + tab_h + 14
    gutter_x, code_x = side_w + 24, side_w + 72
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect width="{w}" height="{h}" rx="12" {fill(s["background"])}/>',
        f'<rect x="{side_w}" y="{title_h}" width="{w - side_w}" height="{h - title_h - status_h}" {fill(s["editor.background"])}/>',
    ]
    # Title bar with window buttons.
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        out.append(f'<circle cx="{20 + i * 20}" cy="{title_h / 2}" r="6" fill="{c}"/>')
    out.append(f'<text x="90" y="{title_h / 2 + 5}" font-family="{UI_FONT}" font-size="13" {fill(s["text"])}>notes</text>')
    out.append(f'<text x="150" y="{title_h / 2 + 5}" font-family="{UI_FONT}" font-size="13" {fill(s["text.muted"])}>main</text>')
    out.append(f'<rect y="{title_h - 1}" width="{w}" height="1" {fill(s["border"])}/>')
    # Project panel.
    out.append(f'<rect x="{side_w - 1}" y="{title_h}" width="1" height="{h - title_h - status_h}" {fill(s["border"])}/>')
    for i, name in enumerate(FILES):
        y = title_h + 28 + i * 26
        if name.strip() == "notes.go":
            out.append(f'<rect x="8" y="{y - 17}" width="{side_w - 16}" height="24" rx="5" {fill(s["ghost_element.selected"])}/>')
        out.append(f'<text x="{20 + (16 if name.startswith("  ") else 0)}" y="{y}" font-family="{UI_FONT}" font-size="13" {fill(s["text"] if "." in name else s["text.muted"])}>{escape(name.strip())}</text>')
    # Tab bar.
    out.append(f'<rect x="{side_w}" y="{title_h}" width="{w - side_w}" height="{tab_h}" {fill(s["tab_bar.background"])}/>')
    out.append(f'<rect x="{side_w}" y="{title_h}" width="150" height="{tab_h}" {fill(s["tab.active_background"])}/>')
    out.append(f'<text x="{side_w + 18}" y="{title_h + 23}" font-family="{UI_FONT}" font-size="13" {fill(s["text"])}>notes.go</text>')
    out.append(f'<text x="{side_w + 162}" y="{title_h + 23}" font-family="{UI_FONT}" font-size="13" {fill(s["text.muted"])}>notebook.go</text>')
    out.append(f'<rect x="{side_w + 150}" y="{title_h + tab_h - 1}" width="{w - side_w - 150}" height="1" {fill(s["border"])}/>')
    # Code.
    active_line = 14
    for n, line in enumerate(CODE.split("\n"), 1):
        y = top + n * line_h
        if n == active_line:
            out.append(f'<rect x="{side_w}" y="{y - 16}" width="{w - side_w}" height="{line_h}" {fill(s["editor.active_line.background"])}/>')
        num = s["editor.active_line_number"] if n == active_line else s["editor.line_number"]
        out.append(f'<text x="{gutter_x + 24}" y="{y}" text-anchor="end" font-family="{FONT}" font-size="13" {fill(num)}>{n}</text>')
        spans = []
        for kind, text in tokens(line):
            if kind:
                style = syn.get(kind, syn["variable"])
                extra = ' font-style="italic"' if style.get("font_style") == "italic" else ""
                spans.append(f"<tspan {fill(style['color'])}{extra}>{escape(text)}</tspan>")
            else:
                spans.append(text)
        out.append(f'<text x="{code_x}" y="{y}" font-family="{FONT}" font-size="14" font-variant-ligatures="none" style="font-variant-ligatures: none" xml:space="preserve">{"".join(spans)}</text>')
        if n == active_line:
            out.append(f'<rect x="{code_x + 4 * char_w:.1f}" y="{y - 15}" width="2" height="19" {fill(s["players"][0]["cursor"])}/>')
    # Status bar.
    out.append(f'<rect y="{h - status_h}" width="{w}" height="{status_h}" {fill(s["status_bar.background"])}/>')
    out.append(f'<rect y="{h - status_h}" width="{w}" height="1" {fill(s["border"])}/>')
    out.append(f'<text x="16" y="{h - 9}" font-family="{UI_FONT}" font-size="12" {fill(s["text.muted"])}>{escape(theme["name"])}</text>')
    out.append(f'<text x="{w - 16}" y="{h - 9}" text-anchor="end" font-family="{UI_FONT}" font-size="12" {fill(s["text.muted"])}>14:5   Go</text>')
    out.append("</svg>")
    return "\n".join(out)


SWATCHES = [
    ("Background", lambda s: s["editor.background"]),
    ("Text", lambda s: s["text"]),
    ("Keyword", lambda s: s["syntax"]["keyword"]["color"]),
    ("Function", lambda s: s["syntax"]["function"]["color"]),
    ("Type", lambda s: s["syntax"]["type"]["color"]),
    ("String", lambda s: s["syntax"]["string"]["color"]),
    ("Punctuation", lambda s: s["syntax"]["punctuation"]["color"]),
    ("Comment", lambda s: s["syntax"]["comment"]["color"]),
    ("Inlay hint", lambda s: s["syntax"]["hint"]["color"]),
    ("Accent", lambda s: s["text.accent"]),
]


def palette_svg(themes):
    sw, gap, left, row_h = 92, 8, 24, 150
    w = left * 2 + len(SWATCHES) * sw + (len(SWATCHES) - 1) * gap
    h = 24 + len(themes) * row_h
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           f'<rect width="{w}" height="{h}" rx="12" fill="#ffffff"/>']
    for r, theme in enumerate(themes):
        s = theme["style"]
        y = 24 + r * row_h
        out.append(f'<text x="{left}" y="{y + 14}" font-family="{UI_FONT}" font-size="15" font-weight="600" fill="#1d1d1f">{escape(theme["name"])}</text>')
        for i, (label, get) in enumerate(SWATCHES):
            x = left + i * (sw + gap)
            c, _ = color(get(s))
            out.append(f'<rect x="{x}" y="{y + 26}" width="{sw}" height="56" rx="8" fill="{s["editor.background"]}" stroke="#d2d2d7"/>')
            out.append(f'<rect x="{x + 10}" y="{y + 36}" width="{sw - 20}" height="36" rx="5" fill="{c}"/>')
            out.append(f'<text x="{x}" y="{y + 100}" font-family="{UI_FONT}" font-size="12" fill="#1d1d1f">{label}</text>')
            out.append(f'<text x="{x}" y="{y + 116}" font-family="{FONT}" font-size="12" fill="#6e6e73">{c}</text>')
    out.append("</svg>")
    return "\n".join(out)


def render_png(svg_path):
    """Screenshot the SVG at its own size with headless Chrome."""
    width, height = re.search(r'width="(\d+)" height="(\d+)"', svg_path.read_text()).groups()
    png_path = svg_path.with_suffix(".png")
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--user-data-dir={profile}", "--force-device-scale-factor=2",
             "--default-background-color=00000000", f"--window-size={width},{height}",
             f"--screenshot={png_path}", svg_path.resolve().as_uri()],
            check=True, capture_output=True,
        )
    print(f"wrote {png_path}")


def main():
    themes = json.loads((ROOT / "themes" / "lull.json").read_text())["themes"]
    images = ROOT / "images"
    images.mkdir(exist_ok=True)
    svgs = []
    for theme in themes:
        svgs.append((images / (theme["name"].lower().replace(" ", "-") + ".svg"), editor_svg(theme)))
    svgs.append((images / "palette.svg", palette_svg(themes)))
    for path, svg in svgs:
        path.write_text(svg + "\n")
        print(f"wrote {path}")
    if not shutil.which(CHROME):
        print("Google Chrome not found; skipping PNG rendering")
        return
    for path, _ in svgs:
        render_png(path)


if __name__ == "__main__":
    main()
