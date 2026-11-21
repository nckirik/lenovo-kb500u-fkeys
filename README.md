# Lenovo KB500U F-keys

No-root top-row remap for the **Lenovo Yoga Tab Plus (TB520FU)** with the
**KB500U** keyboard cover. The custom top row becomes F1–F12, the AI/App keys
become Home/End, and every original Lenovo action stays available with
Ctrl/Alt/Meta.

Tested on:

- Lenovo Yoga Tab Plus TB520FU
- Android 17 (API 37)
- KB500U keyboard cover
- Termux

## Features

- F1–F12 on the 12 keys between Esc and Lock
- Home/End on the Lenovo Smart Key (AI) and App to Customize
- Original actions on any Ctrl/Alt/Meta combination; modifiers are stripped
- Shift alone is preserved, so Shift+F1 still works
- No root, no Key Mapper, no Shizuku
- EN (US English) and TR (Turkish Q) builds

## Mapping

| Physical key | Plain press | Ctrl / Alt / Meta + key |
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

## Install

1. Download the APK for the layout you want:
   - EN: [`apk/ExKeyMo-KB500U-Fkeys-EN.apk`](apk/ExKeyMo-KB500U-Fkeys-EN.apk)
   - TR: [`apk/ExKeyMo-KB500U-Fkeys-TR.apk`](apk/ExKeyMo-KB500U-Fkeys-TR.apk)
2. Install it on the tablet. Play Protect may warn because the APK is
   self-signed: tap **More details → Install anyway**.
3. Open **Settings → System → Languages & input → Physical keyboard**.
4. Select the Lenovo keyboard and choose **ExKeyMo Layout EN** or
   **ExKeyMo Layout TR**.
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
- **Ctrl+Alt+Volume Up** → volume goes up.
- **Ctrl+Alt+Lock** → screen locks.
- **AI key** → Home (start of line).
- **App key** → End (end of line).
- **Ctrl+Alt+AI** → original Lenovo Smart Key action.
- **Ctrl+Alt+App** → original App to Customize action.
- In the TR layout, type `ı ş ğ ü ö ç` to confirm Turkish characters.

## How it works

Android physical keyboards use a KCM (Key Character Map) file selected in the
physical-keyboard settings. This project ships a `type OVERLAY` KCM that:

- maps the 12 top-row keycodes to F1–F12
- maps APP1/APP2 to `MOVE_HOME`/`MOVE_END`
- maps Ctrl/Alt/Meta combinations back to the original keycodes

The KCM is packaged into an APK with the [ExKeyMo](https://github.com/ris58h/exkeymo)
layout template. No root, input injection, or accessibility service is needed.

The TR build uses the AOSP Turkish Q KCM as its base, then adds the same 14 key
blocks. The EN build layers those blocks over the system's generic US base.

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
- If the Lenovo keyboard is not listed separately, try the global
  **Keyboard layout** entry on the same screen.
- TR uses the AOSP Turkish Q layout; Turkish F is not included.
- Home/End are text-editing keys, not the Android Home button.

## License

Apache-2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

The TR base layout is from the Android Open Source Project
(`packages/InputDevices/res/raw/keyboard_layout_turkish.kcm`, Apache-2.0).
APK packaging uses the ExKeyMo template by ris58h.
