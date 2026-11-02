# Lull

Calm, neutral themes for [Zed](https://zed.dev), inspired by the macOS look.
Flat gray backgrounds, no colored chrome, and a few soft pastel syntax colors
instead of a rainbow.

## Variants

| Theme | Background |
|---|---|
| Lull Dark | `#1e1e1e` (matches the macOS Terminal default) |
| Lull Dark Deep | `#171717` |
| Lull Light | `#fafafa` |

## Syntax colors

| Token | Dark | Light |
|---|---|---|
| Keywords | `#8fb3e0` soft blue | `#35609c` |
| Functions | `#c5b4ea` lavender | `#6e4fae` |
| Types, classes | `#dcc08f` sand | `#8c6219` |
| Strings, numbers | `#b5c4a1` sage | `#557040` |
| Variables | `#dcdcdc` | `#262626` |
| Comments | `#6e6e73` | `#8e8e93` |
| Inlay hints | `#409cff` | `#0040dd` |

## Install

Open the extensions page in Zed (`cmd-shift-x`), search for **Lull**, and
install it. Then pick a variant with `theme selector: toggle` (`cmd-k cmd-t`).

## Development

The theme file is generated. Edit the palettes in `build.py`, then run:

```sh
python3 build.py
```

This writes `themes/lull.json` and, if `~/.config/zed/themes` exists, installs
a copy there so Zed reloads it.

## License

MIT
