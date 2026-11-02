#!/usr/bin/env python3
"""Generate themes/lull.json from the palettes below.

Edit a palette, run `python3 build.py`, and Zed reloads the theme.
"""

import json
from pathlib import Path

DARK = {
    "appearance": "dark",
    # Neutral grays and system colors matching macOS dark mode.
    "bg": "#171717",  # editor, rgb(23, 23, 23)
    "surface": "#171717",  # panels, tab bar, title bar
    "elevated": "#242424",  # popovers, modals
    "element": "#2a2a2a",
    "border": "#2e2e2e",
    "border_variant": "#222222",
    "black": "#171717",
}

# Same as DARK, but with the background Terminal.app's Basic profile shows.
DARK_TERMINAL = {
    "bg": "#1e1e1e",
    "surface": "#1e1e1e",
    "elevated": "#2a2a2a",
    "element": "#303030",
    "border": "#353535",
    "border_variant": "#282828",
    "black": "#1e1e1e",
}

DARK_SHARED = {
    "fg": "#dcdcdc",  # labelColor
    "muted": "#98989d",  # secondaryLabelColor
    "subtle": "#5f5f63",  # tertiaryLabelColor
    "accent": "#0a84ff",  # controlAccentColor (blue)
    # Increased-contrast system colors, easier to read as syntax.
    "red": "#ff6961",
    "orange": "#ffb340",
    "yellow": "#ffd426",
    "green": "#5fd67a",
    "teal": "#66d4cf",
    "cyan": "#70d7ff",
    "blue": "#409cff",
    "purple": "#da8fff",
    "pink": "#ff6482",
    "white": "#dcdcdc",
    # Code: mostly grayscale, soft hues for keywords, literals and types.
    "code_keyword": "#8fb3e0",
    "code_literal": "#b5c4a1",
    "code_function": "#c5b4ea",
    "code_type": "#dcc08f",
    "code_comment": "#6e6e73",
    "code_punct": "#8e8e93",
}

PALETTES = {
    "Lull Dark": {**DARK, **DARK_SHARED, **DARK_TERMINAL},
    "Lull Dark Deep": {**DARK, **DARK_SHARED},
    "Lull Light": {
        "appearance": "light",
        # Neutral grays and system colors matching macOS light mode.
        "bg": "#fafafa",  # editor
        "surface": "#fafafa",  # panels, tab bar, title bar
        "elevated": "#ffffff",  # popovers, modals
        "element": "#ececec",
        "border": "#dedede",
        "border_variant": "#e8e8e8",
        "fg": "#262626",  # labelColor
        "muted": "#6e6e73",  # secondaryLabelColor
        "subtle": "#aeaeb2",  # tertiaryLabelColor
        "accent": "#007aff",  # controlAccentColor (blue)
        # Increased-contrast system colors, readable on a light background.
        "red": "#d70015",
        "orange": "#c93400",
        "yellow": "#b25000",
        "green": "#248a3d",
        "teal": "#0c817b",
        "cyan": "#0071a4",
        "blue": "#0040dd",
        "purple": "#8944ab",
        "pink": "#d30f45",
        "black": "#262626",
        "white": "#fafafa",
        # Code: same hues as the dark variants, darkened for a light background.
        "code_keyword": "#35609c",
        "code_literal": "#557040",
        "code_function": "#6e4fae",
        "code_type": "#8c6219",
        "code_comment": "#8e8e93",
        "code_punct": "#6e6e73",
    },
}


def a(color, alpha):
    """Append an alpha channel (0-1) to a #rrggbb color."""
    return f"{color}{round(alpha * 255):02x}"


def s(color, italic=False, bold=False):
    return {
        "color": color,
        "font_style": "italic" if italic else None,
        "font_weight": 700 if bold else None,
    }


def build_style(p):
    dark = p["appearance"] == "dark"
    hover = a(p["fg"], 0.06 if dark else 0.05)
    active = a(p["fg"], 0.10 if dark else 0.09)
    selected = a(p["accent"], 0.18 if dark else 0.14)

    style = {
        "accents": [p["blue"], p["purple"], p["teal"], p["orange"], p["pink"], p["yellow"]],
        "background": p["surface"],
        "border": p["border"],
        "border.variant": p["border_variant"],
        "border.focused": a(p["accent"], 0.6),
        "border.selected": a(p["accent"], 0.6),
        "border.transparent": "#00000000",
        "border.disabled": p["border_variant"],
        "elevated_surface.background": p["elevated"],
        "surface.background": p["surface"],
        "element.background": p["element"],
        "element.hover": hover,
        "element.active": active,
        "element.selected": selected,
        "element.disabled": a(p["element"], 0.5),
        "drop_target.background": a(p["accent"], 0.15),
        "ghost_element.background": "#00000000",
        "ghost_element.hover": hover,
        "ghost_element.active": active,
        "ghost_element.selected": selected,
        "ghost_element.disabled": "#00000000",
        "text": p["fg"],
        "text.muted": p["muted"],
        "text.placeholder": p["subtle"],
        "text.disabled": p["subtle"],
        "text.accent": p["accent"],
        "icon": p["fg"],
        "icon.muted": p["muted"],
        "icon.disabled": p["subtle"],
        "icon.placeholder": p["subtle"],
        "icon.accent": p["accent"],
        "status_bar.background": p["surface"],
        "title_bar.background": p["surface"],
        "title_bar.inactive_background": p["surface"],
        "toolbar.background": p["bg"],
        "tab_bar.background": p["surface"],
        "tab.inactive_background": p["surface"],
        "tab.active_background": p["bg"],
        "search.match_background": a(p["yellow"], 0.25),
        "panel.background": p["surface"],
        "panel.focused_border": a(p["accent"], 0.6),
        "panel.indent_guide": a(p["fg"], 0.08),
        "panel.indent_guide_active": a(p["fg"], 0.2),
        "pane.focused_border": a(p["accent"], 0.6),
        "pane_group.border": p["border"],
        "scrollbar.thumb.background": a(p["fg"], 0.12),
        "scrollbar.thumb.hover_background": a(p["fg"], 0.22),
        "scrollbar.thumb.border": "#00000000",
        "scrollbar.track.background": "#00000000",
        "scrollbar.track.border": "#00000000",
        "editor.foreground": p["fg"],
        "editor.background": p["bg"],
        "editor.gutter.background": p["bg"],
        "editor.subheader.background": p["surface"],
        "editor.active_line.background": a(p["fg"], 0.04),
        "editor.highlighted_line.background": a(p["accent"], 0.08),
        "editor.line_number": a(p["muted"], 0.6),
        "editor.active_line_number": p["fg"],
        "editor.invisible": a(p["muted"], 0.4),
        "editor.wrap_guide": a(p["fg"], 0.06),
        "editor.active_wrap_guide": a(p["fg"], 0.12),
        "editor.indent_guide": a(p["fg"], 0.08),
        "editor.indent_guide_active": a(p["fg"], 0.2),
        "editor.document_highlight.read_background": a(p["accent"], 0.12),
        "editor.document_highlight.write_background": a(p["accent"], 0.2),
        "editor.document_highlight.bracket_background": a(p["accent"], 0.2),
        "link_text.hover": p["accent"],
        "terminal.background": p["bg"],
        "terminal.foreground": p["fg"],
        "terminal.bright_foreground": p["fg"],
        "terminal.dim_foreground": p["muted"],
        "version_control.added": p["green"],
        "version_control.modified": p["blue"],
        "version_control.deleted": p["red"],
        "version_control.conflict_marker.ours": a(p["green"], 0.2),
        "version_control.conflict_marker.theirs": a(p["blue"], 0.2),
    }

    ansi = {
        "black": p["black"] if not dark else p["element"],
        "red": p["red"],
        "green": p["green"],
        "yellow": p["yellow"],
        "blue": p["blue"],
        "magenta": p["purple"],
        "cyan": p["cyan"],
        "white": p["white"] if dark else p["muted"],
    }
    for name, color in ansi.items():
        style[f"terminal.ansi.{name}"] = color
        style[f"terminal.ansi.bright_{name}"] = color
        style[f"terminal.ansi.dim_{name}"] = a(color, 0.7)
    style["terminal.ansi.bright_black"] = p["subtle"]

    statuses = {
        "conflict": p["orange"],
        "created": p["green"],
        "deleted": p["red"],
        "error": p["red"],
        "hidden": p["subtle"],
        "hint": p["blue"],  # inlay hints
        "ignored": p["subtle"],
        "info": p["blue"],
        "modified": p["blue"],
        "predictive": p["subtle"],
        "renamed": p["teal"],
        "success": p["green"],
        "unreachable": p["muted"],
        "warning": p["yellow"],
    }
    for name, color in statuses.items():
        style[name] = color
        style[f"{name}.background"] = a(color, 0.12)
        style[f"{name}.border"] = a(color, 0.4)

    player_colors = [p["accent"], p["pink"], p["green"], p["orange"],
                     p["purple"], p["teal"], p["yellow"], p["red"]]
    style["players"] = [
        {"cursor": c, "background": c, "selection": a(c, 0.25 if dark else 0.2)}
        for c in player_colors
    ]

    kw, lit, fn = p["code_keyword"], p["code_literal"], p["code_function"]
    ty, cm, pu = p["code_type"], p["code_comment"], p["code_punct"]
    style["syntax"] = {
        "attribute": s(pu),
        "boolean": s(lit),
        "comment": s(cm),
        "comment.doc": s(cm),
        "constant": s(lit),
        "constructor": s(ty),
        "embedded": s(p["fg"]),
        "emphasis": s(p["fg"], italic=True),
        "emphasis.strong": s(fn, bold=True),
        "enum": s(ty),
        "function": s(fn),
        "hint": s(p["blue"]),  # inlay hints: types, parameter names
        "keyword": s(kw),
        "label": s(pu),
        "link_text": s(kw),
        "link_uri": s(pu),
        "number": s(lit),
        "operator": s(pu),
        "predictive": s(p["subtle"], italic=True),
        "preproc": s(kw),
        "primary": s(p["fg"]),
        "property": s(p["fg"]),
        "punctuation": s(pu),
        "punctuation.bracket": s(pu),
        "punctuation.delimiter": s(pu),
        "punctuation.list_marker": s(pu),
        "punctuation.special": s(pu),
        "string": s(lit),
        "string.escape": s(kw),
        "string.regex": s(lit),
        "string.special": s(lit),
        "string.special.symbol": s(lit),
        "tag": s(kw),
        "text.literal": s(lit),
        "title": s(fn, bold=True),
        "type": s(ty),
        "variable": s(p["fg"]),
        "variable.special": s(kw, italic=True),
        "variant": s(ty),
    }
    return style


def main():
    family = {
        "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
        "name": "Lull",
        "author": "Ihor Manzii",
        "themes": [
            {"name": name, "appearance": p["appearance"], "style": build_style(p)}
            for name, p in PALETTES.items()
        ],
    }
    out = Path(__file__).parent / "themes" / "lull.json"
    out.parent.mkdir(exist_ok=True)
    text = json.dumps(family, indent=2) + "\n"
    out.write_text(text)
    print(f"wrote {out}")

    # Zed only notices edits to real files in its themes folder, not to symlink targets.
    zed_themes = Path.home() / ".config" / "zed" / "themes"
    if zed_themes.is_dir():
        installed = zed_themes / out.name
        if installed.is_symlink():
            installed.unlink()
        installed.write_text(text)
        print(f"installed {installed}")


if __name__ == "__main__":
    main()
