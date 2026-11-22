#!/usr/bin/env bash
# Build the small Xlib keymap helper.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
cc="${CC:-clang}"
out="${1:-$HOME/bin/x11-keymap}"

mkdir -p "$(dirname "$out")"
"$cc" -O2 -Wall -o "$out" "$here/x11-keymap.c" -lX11
echo "built $out"
