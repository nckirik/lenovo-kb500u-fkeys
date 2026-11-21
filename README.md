# Lenovo KB500U F-keys

No-root top-row remap for the **Lenovo Yoga Tab Plus (TB520FU)** with the
**KB500U** keyboard cover. The custom top row becomes F1–F12, the AI/App keys
become Home/End, and every original Lenovo action stays available with
**Meta** (the Fn key). Ctrl and Alt are passed through, so Alt+F4 works in
RDP and other apps.

Tested on:

- Lenovo Yoga Tab Plus TB520FU
- Android 17 (API 37)
- KB500U keyboard cover
- Termux

## Features

- F1–F12 on the 12 keys between Esc and Lock
- Home/End on the Lenovo Smart Key (AI) and App to Customize
- Original actions on any Meta combination; modifiers are stripped
- Ctrl and Alt pass through, so Alt+F4, Ctrl+F4, etc. reach the app
- Shift alone is preserved, so Shift+F1 still works
- No root, no Key Mapper, no Shizuku
- EN (US English) and TR (Turkish Q) builds

## Mapping

| Physical key | Plain press | Meta + key |
|---|---|---|
| Silent | F1 | Silent |
| Volume Down | F2 | Volume Down |
| Volume Up | F3 | Volume Up |
| Mic Mute | F4 | Mic Mute |
| Brightness Down | F5 | Brightness Down |
| Brightness Up | F6 | Brightness Up |
| Trackpad | F7 | Trackpad |
| Capture Screen | F8 | Capture Screen |
| Full Screen | F9 | Full Screen |
| Split Screen | F10 | Split Screen |
| Device Collaboration | F11 | Device Collaboration |
| Lock Screen | F12 | Lock Screen |
| Lenovo Smart Key (AI) | Home | Lenovo Smart Key |
| App to Customize | End | App to Customize |

Home/End are `MOVE_HOME`/`MOVE_END` (text editing), not the Android Home screen
button. Escape and Delete are unchanged.

**Meta is the Fn key.** A plain press sends the F-key/Home/End, and Ctrl or Alt
stay on that event. Press Meta (alone or with Ctrl/Alt/Shift) to send the
original Lenovo key instead. For example, Meta+Volume Down changes the volume,
Meta+Lock locks the screen, and Alt+F4 reaches an RDP session as Alt+F4.

## Install

1. Download the latest APK from
   **[Releases](https://github.com/nckirik/lenovo-kb500u-fkeys/releases/latest)**,
   or use the files in `apk/`:
   - EN: [`apk/ExKeyMo-KB500U-Fkeys-EN.apk`](apk/ExKeyMo-KB500U-Fkeys-EN.apk)
   - TR: [`apk/ExKeyMo-KB500U-Fkeys-TR.apk`](apk/ExKeyMo-KB500U-Fkeys-TR.apk)
2. Install it on the tablet. Play Protect may warn because the APK is
   self-signed: tap **More details → Install anyway**.
3. Open **Settings → Pen & keyboard → Lenovo Keyboard Pack for Yoga Tab Plus**.
4. Select the language, then choose **ExKeyMo Layout EN** or
   **ExKeyMo Layout TR** as the layout.

   On builds without the Lenovo menu, use
   **Settings → System → Languages & input → Physical keyboard** instead.

5. Apply it only to the Lenovo keyboard. The overlay also remaps the standard
   volume, brightness, and mute keycodes, so using it on another keyboard would
   turn those keys into F-keys.

Both APKs can be installed at once; Android keeps one layout active per
physical keyboard.

### Termux install note

If `termux-open` returns immediately with no installer, set:

```
allow-external-apps = true
```

in `~/.termux/termux.properties`, run `termux-reload-settings`, and retry.
This lets Termux hand the APK to the package installer.

## Test

In Termux:

```sh
cat -v
```

- **Silent** → F1 escape sequence, not mute.
- **Alt+F4** in an RDP session → reaches the remote.
- **Ctrl+F4** / **Shift+F4** → reach the app unchanged.
- **Meta+Volume Down** → volume goes down (original action).
- **Meta+Lock** → screen locks.
- **AI key** → Home (start of line).
- **App key** → End (end of line).
- **Meta+AI** → original Lenovo Smart Key action.
- **Meta+App** → original App to Customize action.
- In the TR layout, type `ı ş ğ ü ö ç` to confirm Turkish characters.

## How it works

Android physical keyboards use a KCM (Key Character Map) file selected in the
physical-keyboard settings. This project ships a `type OVERLAY` KCM that:

- maps the physical top-row keys to F1–F12 at the scan/usage level
- maps the AI/App keys to `MOVE_HOME`/`MOVE_END` the same way
- maps Meta combinations back to the original Lenovo keycodes

Ctrl and Alt are deliberately left on the target key event. Only Meta is
treated as Fn, which is why Alt+F4 survives.

The KCM is packaged into an APK with the [ExKeyMo](https://github.com/ris58h/exkeymo)
layout template. No root, input injection, or accessibility service is needed.

The TR build uses the AOSP Turkish Q KCM as its base, then appends the KB500U
remap section. The EN build layers that section over the system's generic US
base.

## Repo layout

```
apk/       prebuilt signed APKs
layouts/   KCM sources
tools/     KCM generators
```

## Build

Regenerate the KCMs:

```sh
python3 tools/gen_kcm.py
python3 tools/build-tr.py
```

Package an APK:

1. Open <https://ris58h.github.io/exkeymo/complex.html>.
2. Paste `layouts/kb500u-fkeys-en.kcm` or `layouts/kb500u-fkeys-tr.kcm`.
3. Download the APK, or rebuild it with `apktool` if you need targetSdk 37,
   the EN/TR package names, and the labels used here.

The prebuilt APKs target Android 17 (targetSdk 37), minSdk 24, and are signed
with a project-local key. Rebuilding with a different key requires uninstalling
the old copy first.

## Limitations

- The layout picker applies one KCM per physical keyboard.
- If the Lenovo Keyboard Pack menu is missing, use
  **Settings → System → Languages & input → Physical keyboard**.
- TR uses the AOSP Turkish Q layout; Turkish F is not included.
- Home/End are text-editing keys, not the Android Home button.

## Changelog

- **v1.2** — Meta is the only Fn modifier; Ctrl/Alt pass through, so Alt+F4
  works in RDP.
- **v1.1** — EN and TR builds; AI/App keys become Home/End.
- **v1.0** — initial F1–F12 remap.

## License

Apache-2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

The TR base layout is from the Android Open Source Project
(`packages/InputDevices/res/raw/keyboard_layout_turkish.kcm`, Apache-2.0).
APK packaging uses the ExKeyMo template by ris58h.
