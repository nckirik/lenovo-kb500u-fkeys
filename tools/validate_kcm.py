#!/usr/bin/env python3
"""Validate every KCM referenced by layouts/manifest.json."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "layouts/manifest.json"


def validate(path: Path) -> tuple[int, int, list[str]]:
    errors: list[str] = []
    text = path.read_text()
    if text.count("type OVERLAY") != 1:
        errors.append("expected exactly one 'type OVERLAY'")

    scan_codes: set[int] = set()
    usage_codes: set[int] = set()
    map_count = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^map key (usage )?(\S+) (\S+)$", line)
        if line.startswith("map key") and not match:
            errors.append(f"line {lineno}: malformed map key: {line}")
            continue
        if not match:
            continue
        map_count += 1
        code = int(match.group(2), 0)
        target = usage_codes if match.group(1) else scan_codes
        if code in target:
            errors.append(f"line {lineno}: duplicate map key {match.group(2)}")
        target.add(code)

    key_labels: set[str] = set()
    key_count = 0
    for match in re.finditer(r"^key (\S+) \{\n(.*?)^\}", text, re.M | re.S):
        label, body = match.group(1), match.group(2)
        key_count += 1
        if label in key_labels:
            errors.append(f"duplicate key block: {label}")
        key_labels.add(label)
        if ":" not in body:
            errors.append(f"key {label}: no behaviors")

    if key_count == 0:
        errors.append("no key blocks found")
    return key_count, map_count, errors


def main() -> int:
    settings = json.loads(MANIFEST.read_text())
    failed = False
    for layout in settings["layouts"]:
        path = ROOT / layout["kcm"]
        if not path.is_file():
            print(f"FAIL {layout['id']}: missing {path}")
            failed = True
            continue
        keys, maps, errors = validate(path)
        if errors:
            failed = True
            print(f"FAIL {layout['id']}: {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {layout['id']}: {path} ({keys} keys, {maps} maps)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
