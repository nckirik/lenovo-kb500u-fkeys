#!/usr/bin/env python3
"""Generate the EN KCM (F1-F12 + Home/End with modifier fallbacks)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "layouts" / "kb500u-fkeys-en.kcm"

keys = [
    ("LENOVO_VOLUME_MUTE", "F1",  "Silent"),
    ("VOLUME_DOWN",        "F2",  "Volume Down"),
    ("VOLUME_UP",          "F3",  "Volume Up"),
    ("MUTE",               "F4",  "Mic Mute"),
    ("BRIGHTNESS_DOWN",    "F5",  "Brightness Down"),
    ("BRIGHTNESS_UP",      "F6",  "Brightness Up"),
    ("TP_MUTE",            "F7",  "Trackpad"),
    ("SYSRQ",              "F8",  "Capture Screen"),
    ("FULL_SCREEN",        "F9",  "Full Screen"),
    ("SPLIT_SCREEN",       "F10", "Split Screen"),
    ("SUPER_CONNECT",      "F11", "Device Collaboration"),
    ("SCREEN_LOCK",        "F12", "Lock Screen"),
    ("APP1",               "MOVE_HOME", "Lenovo Smart Key (AI)"),
    ("APP2",               "MOVE_END",  "App to Customize"),
]

# Most-specific first. Shift variants must precede their non-shift
# counterparts because Android ignores Shift when matching Ctrl/Alt/Meta.
combos = [
    "ctrl+alt+meta+shift",
    "ctrl+alt+shift",
    "ctrl+meta+shift",
    "alt+meta+shift",
    "ctrl+shift",
    "alt+shift",
    "meta+shift",
    "ctrl+alt+meta",
    "ctrl+alt",
    "ctrl+meta",
    "alt+meta",
    "ctrl",
    "alt",
    "meta",
]

out = [
    "type OVERLAY",
    "",
    "# Lenovo KB500U top row -> F1..F12, plus Home/End for AI/App.",
    "#",
    "# Plain press (with or without Shift) sends the F key, or Home/End",
    "# for the AI and App keys. Home/End means MOVE_HOME/MOVE_END, the",
    "# text-editing keys, not the Android Home button.",
    "#",
    "# Any press containing Ctrl, Alt or Meta sends the original Lenovo",
    "# key instead, with every modifier in the combination stripped,",
    "# including Shift. This keeps the original action available on",
    "# combinations such as Ctrl+Meta+Alt+key.",
    "#",
    "# Escape and Delete are deliberately left untouched.",
    "",
]

for name, fkey, label in keys:
    out.append(f"# {label}")
    out.append(f"key {name} {{")
    out.append(f"    base: replace {fkey}")
    for c in combos:
        out.append(f"    {c}: replace {name}")
    out.append("}")
    out.append("")

OUT.write_text("\n".join(out))
print(f"wrote {OUT} ({len(keys)} keys)")
