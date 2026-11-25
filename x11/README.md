# X11 F-key mapping

The Android KCM in this repository only applies to apps that consume Android
key events. Lenovo/Yoga keyboards often intercept shortcuts through an OEM
service; accessibility/direct access is frequently the only way to capture the
Meta key and its combinations, Alt+Tab, and other classic shortcuts, as well as
the top row. That layer — used by X11/Termux:X11 or any X server — bypasses the
Android KCM for the whole keyboard.

This helper remaps the top row on the local X server, so any X11 client sees
F1–F8. Meta, Alt+Tab, and other classic shortcuts are handled by the X11/WM
layer, not by this helper or the Android KCM. It assumes the client reads keys
through the X server keymap; if keycode capture is enabled, the client sees raw
keycodes and this map is bypassed.

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

## If keycode capture is enabled

Raw keycode/scancode capture sits below the X server keymap. Both `xmodmap` and
`x11-keymap` are invisible in that mode; the capturing layer must map the raw
keycodes. Disable keycode capture to use this helper, or map the top row on the
remote X server (below). This is separate from the Android KCM/accessibility
bypass.

## If keycode capture is enabled (remote X server)

If scancode capture is required for the Turkish layout, map the top row on the
remote X server. With scancode capture, the capture layer reads scancodes
directly; the remote X server is where they are interpreted.

1. Copy `x11/Xmodmap.xmodmap` to the remote as `~/.Xmodmap`.
2. Apply it:

   ```sh
   xmodmap ~/.Xmodmap
   ```

3. Add an autostart entry so KDE reapplies it after login:

   ```ini
   # ~/.config/autostart/kb500u-fkeys.desktop
   [Desktop Entry]
   Type=Application
   Name=KB500U F-keys
   Exec=sh -c 'sleep 5; xmodmap "$HOME/.Xmodmap"'
   X-GNOME-Autostart-enabled=true
   ```

4. If `xmodmap` is missing, install `x11-xserver-utils`
   (Debian/Ubuntu/Neon).
5. Clear the remote WM's Alt+F4 shortcut if needed.

This only remaps the top-row media keycodes; the remote Turkish XKB layout
continues to handle the letters. The local X11 helper is not used in this mode.

## Turkish layout in X11

Use exactly one Turkish layer. The TR APK layout is a full Turkish Q character
map for native Android. If the X server/XKB is also Turkish Q, Turkish is
applied twice.

A useful test is the soft/on-screen keyboard: it usually sends the underlying US
positions, so the remote Turkish Q layout translates once. If the soft keyboard
gives `.`→ç and `/`→`.`, the remote layout is correct. The physical TR APK
layout, by contrast, remaps punctuation keycodes before X11 sees them, so the
remote translates a second time. Use the EN APK layout for X11.

For X11:

- Select the **EN** APK layout on Android; it still maps the top row.
- Set the X server to Turkish Q: `setxkbmap tr` (empty variant is Q; `tr f` is
  Turkish F). Verify with `setxkbmap -query`.
- In Turkish Q, the physical I key is ı; the dotted i is on the apostrophe key.
- If keycode capture is on, use the remote xmodmap above; if off, use the local
  x11 helper.

If the Turkish keys still fail, check that the remote is Q and not F, and that
the Android layout is EN (not TR) while the X server is Turkish.

## Client-side remap / Unicode options

Some X11 clients can send Unicode keyboard events for printable keys or remap
known scancodes. Unicode mode can make the physical keyboard behave like a soft
keyboard; test shortcuts separately. Scancode remapping only covers keys the
client knows; vendor media keys may not have a scancode. The remote xmodmap above
is the complete top-row workaround; the local helper works when keycode capture
is off.

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
