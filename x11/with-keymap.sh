#!/usr/bin/env bash
# Run an X11 client with the KB500U top-row keymap held for the session.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
helper="${X11_KEYMAP_HELPER:-$HOME/bin/x11-keymap}"
keymap="${X11_KEYMAP:-$HOME/.config/kb500u-fkeys/Xmodmap}"

if [ -z "${DISPLAY:-}" ]; then
    echo "with-keymap: DISPLAY is not set (for Termux:X11 use DISPLAY=:0)" >&2
    exit 1
fi
if [ ! -x "$helper" ]; then
    echo "with-keymap: helper not found: $helper" >&2
    echo "build it with: $here/build.sh" >&2
    exit 1
fi
if [ ! -f "$keymap" ]; then
    echo "with-keymap: keymap not found: $keymap" >&2
    echo "copy $here/Xmodmap to $keymap" >&2
    exit 1
fi

"$helper" hold "$keymap" &
holder=$!

cleanup() {
    trap - EXIT INT TERM
    kill "$holder" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

"$@"
