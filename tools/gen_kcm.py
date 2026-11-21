#!/usr/bin/env python3
"""Generate the EN KCM: F1-F12 + Home/End, Meta acts as the Fn modifier."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "layouts" / "kb500u-fkeys-en.kcm"

# target keycode, original Lenovo keycode, label, scan codes, HID usage codes
keys = [
    ("F1",        "LENOVO_VOLUME_MUTE", "Silent",                 [113], []),
    ("F2",        "VOLUME_DOWN",        "Volume Down",             [114], [0x0C00EA]),
    ("F3",        "VOLUME_UP",          "Volume Up",               [115], [0x0C00E9]),
    ("F4",        "MUTE",               "Mic Mute",                [248], [0x0C0391]),
    ("F5",        "BRIGHTNESS_DOWN",    "Brightness Down",         [224], [0x0C0070]),
    ("F6",        "BRIGHTNESS_UP",      "Brightness Up",           [225], [0x0C006F]),
    ("F7",        "TP_MUTE",            "Trackpad",                [],    [0x0C0392]),
    ("F8",        "SYSRQ",              "Capture Screen",          [99],  [0x0C046]),
    ("F9",        "FULL_SCREEN",        "Full Screen",             [],    [0x0C0394]),
    ("F10",       "SPLIT_SCREEN",       "Split Screen",            [],    [0x0C0395]),
    ("F11",       "SUPER_CONNECT",      "Device Collaboration",    [],    [0x0C0397]),
    ("F12",       "SCREEN_LOCK",        "Lock Screen",             [],    [0x0C038E]),
    ("MOVE_HOME", "APP1",               "Lenovo Smart Key (AI)",    [],    [0x0C0398]),
    ("MOVE_END",  "APP2",               "App to Customize",         [],    [0x0C0399]),
]

# Meta is the Fn modifier. Shift variants are listed first so Shift is also
# stripped when Meta is used.
meta_combos = [
    "ctrl+alt+meta+shift",
    "ctrl+meta+shift",
    "alt+meta+shift",
    "meta+shift",
    "ctrl+alt+meta",
    "ctrl+meta",
    "alt+meta",
    "meta",
]

out = [
    "type OVERLAY",
    "",
    "# Lenovo KB500U top row -> F1..F12, plus Home/End for AI/App.",
    "#",
    "# The physical keys are remapped to the target keycode at the scan/usage",
    "# level. Ctrl and Alt are left on the event, so Alt+F4, Ctrl+F4, etc.",
    "# reach the application unchanged (for example an RDP client).",
    "#",
    "# Meta acts as the Fn modifier. Any Meta combination sends the original",
    "# Lenovo key instead, with the modifiers stripped.",
    "#",
    "# Escape and Delete are deliberately left untouched.",
    "",
    "# BEGIN KB500U REMAP",
    "# The TR build appends everything from this marker onward to the AOSP",
    "# Turkish Q base.",
    "",
]

for target, original, label, scan_codes, usage_codes in keys:
    out.append(f"# {label} -> {target}")
    for scan_code in scan_codes:
        out.append(f"map key {scan_code} {target}")
    for usage_code in usage_codes:
        out.append(f"map key usage 0x{usage_code:08x} {target}")
    out.append("")

for target, original, label, _scan_codes, _usage_codes in keys:
    out.append(f"# {label}: Meta acts as Fn")
    out.append(f"key {target} {{")
    for combo in meta_combos:
        out.append(f"    {combo}: replace {original}")
    out.append("}")
    out.append("")

OUT.write_text("\n".join(out))
print(f"wrote {OUT} ({len(keys)} keys)")
