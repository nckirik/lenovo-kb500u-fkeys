#!/usr/bin/env python3
"""Build the TR KCM: AOSP Turkish Q base + the KB500U remap section."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "layouts" / "turkish-q-aosp.kcm"
EN = ROOT / "layouts" / "kb500u-fkeys-en.kcm"
OUT = ROOT / "layouts" / "kb500u-fkeys-tr.kcm"

base = BASE.read_text()
en = EN.read_text()

marker = "# BEGIN KB500U REMAP"
index = en.find(marker)
if index < 0:
    raise SystemExit(f"marker {marker!r} not found in {EN}")

out = base.rstrip("\n") + "\n\n" + en[index:]
OUT.write_text(out)
print(f"wrote {OUT} ({len(out.splitlines())} lines)")
