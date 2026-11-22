# X11 F-key mapping

The Android KCM in this repository only applies to apps that consume Android
key events. Lenovo/Yoga keyboards often intercept shortcuts through an OEM
service; accessibility/direct access is frequently the only way to capture the
Meta key and its combinations, Alt+Tab, and other classic shortcuts, as well as
the top row. That layer — used by X11/Termux:X11 or any X server — bypasses the
Android KCM for the whole keyboard.

This helper remaps the top row on the local X server, so any X11 client sees
F1–F8. Meta, Alt+Tab, and other classic shortcuts are handled by the X11/WM
layer, not by this helper or the Android KCM.

This is a layer bypass, not a keycode difference. It is separate from the APK
and does not affect native Android apps; the KCM remains active where the normal
Android input pipeline is used.

## What it maps

These are the local X server keycodes on the tested device; they are not the
cause of the bypass:

| Physical key | X keycode | Keysym |
|---|---|---|
| Silent | 121 | F1 |
| Volume Down | 122 | F2 |
| Volume Up | 123 | F3 |
| Mic Mute | 248 | F4 |
| Brightness Down | 232 | F5 |
| Brightness Up | 233 | F6 |
| Trackpad | 199 | F7 |
| Capture Screen | 107 | F8 |

F9–F12 / Home / End were already present in the tested X11 keymap and are not
remapped here. This is not guaranteed on every X server; verify them with `xev`
and add the keycodes if needed (see below).

## Build

`x11-keymap` is a small Xlib helper:

```sh
x11/build.sh                 # installs to ~/bin/x11-keymap
```

Or build manually:

```sh
clang -O2 -Wall -o ~/bin/x11-keymap x11/x11-keymap.c -lX11
```

## Install the keymap

```sh
mkdir -p ~/.config/kb500u-fkeys
cp x11/Xmodmap ~/.config/kb500u-fkeys/Xmodmap
```

## Run any X11 client with the keymap

```sh
DISPLAY=:0 x11/with-keymap.sh <x11-client> [args...]
```

The wrapper starts a holder, applies the map, runs the client, and kills the
holder when the client exits.

For manual use:

```sh
DISPLAY=:0 ~/bin/x11-keymap hold ~/.config/kb500u-fkeys/Xmodmap &
```

## Verify

```sh
DISPLAY=:0 ~/bin/x11-keymap dump |
  grep -E '^keycode (121|122|123|248|232|233|199|107) '
```

`XChangeKeyboardMapping()` returns `0` on Termux:X11 even when the change
succeeds, so the helper verifies the mapping by reading it back. Termux:X11 also
drops a mapping when the client that changed it disconnects, so `hold` keeps the
X connection open. On a regular X server, the mapping normally persists for the
session and `xmodmap` can be used at startup instead.

## Checking the remaining keys

The helper intentionally leaves F9–F12 / Home / End untouched. Verify them on
the X11 display:

```sh
xev -event keyboard
```

Press **Full Screen**, **Split Screen**, **Device Collaboration**, **Lock
Screen**, **AI**, and **App**. If they already produce F9–F12/Home/End, no
change is needed. If not, add the keycodes reported by `xev` to `Xmodmap`:

```
keycode N = F9  F9  F9  F9    # Full Screen
keycode N = F10 F10 F10 F10   # Split Screen
keycode N = F11 F11 F11 F11   # Device Collaboration
keycode N = F12 F12 F12 F12   # Lock Screen
keycode N = Home Home Home Home
keycode N = End End End End
```

## Notes

- If your keycodes differ, run `x11-keymap dump` and adjust `Xmodmap`.
- The map is per X session. Re-run the wrapper or holder after the X server
  restarts.
- X11 window managers may reserve Alt+F4 for **Close Window** (KDE/GNOME).
  That is a window-manager shortcut, independent of this helper; rebind it if
  you need Alt+F4 inside an X11 client.
- The `#` comments in `Xmodmap` are for `x11-keymap`; `xmodmap(1)` uses `!`
  comments if you want to reuse the file on another X server.
