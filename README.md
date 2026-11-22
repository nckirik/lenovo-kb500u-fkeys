# Lenovo KB500U F-keys

No-root top-row remap for the **Lenovo Yoga Tab Plus (TB520FU)** with the
**KB500U** keyboard cover. The custom top row becomes F1–F12, the AI/App keys
become Home/End, and every original Lenovo action stays available with
**Meta** (the Fn key). Ctrl and Alt are passed through at the Android input
layer, so apps that consume Android key events can see Alt+F4. Consumers that
capture keys through an accessibility/direct-input layer (for example X11)
bypass the Android KCM entirely, so the remap does not apply there.

Tested on:

- Lenovo Yoga Tab Plus TB520FU
- Android 17 (API 37)
- KB500U keyboard cover
- Termux

## Features

- F1–F12 on the 12 keys between Esc and Lock
- Home/End on the Lenovo Smart Key (AI) and App to Customize
- Original actions on any Meta combination; modifiers are stripped
- Ctrl and Alt are left on the F-key event; Android-key-event consumers see
  Alt+F4/Ctrl+F4 normally
- Not applicable to accessibility/direct-input consumers (e.g., X11), which
  bypass the Android KCM for all keys
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
Meta+Lock locks the screen. Alt+F4 is preserved for apps that consume Android
key events. X11 and other accessibility/direct-input consumers bypass the KCM,
so the remap does not apply there.

## Install

1. Download the latest APK from
   **[Releases](https://github.com/nckirik/lenovo-kb500u-fkeys/releases/latest)**.

   The `apk/` folder keeps the older v1.2 files:
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

**After installing or updating the APK**, Lenovo may switch the keyboard back
to the default layout. Reselect **ExKeyMo Layout EN** or **ExKeyMo Layout TR**
for the Lenovo keyboard, or reboot to force Android to reload the KCM.

### Termux install note

If `termux-open` returns immediately with no installer, set:

```
allow-external-apps = true
```

in `~/.termux/termux.properties`, run `termux-reload-settings`, and retry.
This lets Termux hand the APK to the package installer.

## Test

In the **native Termux Android app** (not inside X11):

```sh
cat -v
```

- **Silent** → F1 escape sequence, not mute.
- **Alt+F4** in an app that consumes Android key events → preserved.
  (X11 and other accessibility/direct-input consumers bypass the KCM.)
- **Ctrl+F4** / **Shift+F4** → reach the app unchanged.
- **Meta+Volume Down** → volume goes down (original action).
- **Meta+Lock** → screen locks.
- **AI key** → Home (start of line).
- **App key** → End (end of line).
- **Meta+AI** → original Lenovo Smart Key action.
- **Meta+App** → original App to Customize action.
- In the TR layout, type `ı ş ğ ü ö ç` to confirm Turkish characters.

X11 is not a reliable test of this layout: it captures keys through an
accessibility/direct-input layer, bypassing the Android KCM. On Yoga, enabling
accessibility to capture the top row, Meta combos, Alt+Tab, etc. also bypasses
the KCM for all keys. Configure the X11 side separately; see
[`x11/README.md`](x11/README.md). An X11 window manager can also reserve Alt+F4.

## How it works

Android physical keyboards use a KCM (Key Character Map) file selected in the
physical-keyboard settings. This project ships a `type OVERLAY` KCM that:

- maps the physical top-row keys to F1–F12 at the scan/usage level
- maps the AI/App keys to `MOVE_HOME`/`MOVE_END` the same way
- maps Meta combinations back to the original Lenovo keycodes

Ctrl and Alt are deliberately left on the target key event. Only Meta is
treated as Fn. This preserves Alt+F4 at the Android input layer. X11 and other
accessibility/direct-input consumers bypass the KCM entirely, so the remap is
not active there.

This is a whole-keyboard bypass, not just the top-row remap: when
accessibility/direct input is active, Meta, Alt+Tab, and other classic
shortcuts are handled by that layer, not by the KCM.

The KCM is packaged into a minimal layout-provider APK by
`tools/build_apks.py`; the receiver is metadata-only and the app contains only
a tiny placeholder class. No root, input injection, or accessibility service is
needed.

The TR build uses the AOSP Turkish Q KCM as its base, then appends the KB500U
remap section. The EN build layers that section over the system's generic US
base.

### X11 consumers

X11 captures keys through an accessibility/direct-input layer, so the Android
KCM is not applied. The optional [`x11/`](x11/README.md) helper remaps the local
X server's keycodes for any X11 client.

## Repo layout

```
.github/   CI and release workflows
apk/       prebuilt signed APKs (v1.2)
layouts/   KCM sources + manifest.json
template/  minimal APK template
tools/     KCM generators, validator, APK builder
x11/       X11 keymap helper for accessibility/direct-input consumers
```

## Build

Regenerate the KCMs:

```sh
python3 tools/gen_kcm.py
python3 tools/build-tr.py
```

Validate and build every layout in `layouts/manifest.json`:

```sh
python3 tools/validate_kcm.py
python3 tools/build_apks.py \
  --ks /path/to/keystore.jks \
  --ks-pass "$KEYSTORE_PASSWORD" \
  --key-alias "$KEY_ALIAS" \
  --key-pass "$KEY_PASSWORD" \
  --out dist
```

The builder uses `aapt2`, `zipalign`, and `apksigner` with the minimal template
in `template/`. No Gradle or Android Studio is required. CI builds all layouts
on PRs and uploads them as the `kb500u-apks` artifact.

## CI and releases

- Pull requests: validate every KCM and build every layout, with APKs uploaded
  as the `kb500u-apks` artifact.
- Tags `v*`: build every layout with the release key and publish a GitHub
  release with the APKs and `SHA256SUMS`.
- Add a layout by adding a KCM and an entry in `layouts/manifest.json`; see
  [`CONTRIBUTING.md`](CONTRIBUTING.md).

The CI builder defaults to targetSdk 36. Bump `versionCode` in
`layouts/manifest.json` before tagging a release.

## Limitations

- The layout picker applies one KCM per physical keyboard.
- **Lenovo/Yoga interception and accessibility bypass the Android KCM for all
  keys.** Yoga keyboards can route shortcuts through Lenovo's service.
  Accessibility/direct access is often the only way to capture the Meta key and
  its combinations, Alt+Tab, and other classic shortcuts, as well as the top
  row. That layer bypasses the Android KCM for the whole keyboard, not just the
  remapped keys. This is a layer bypass, not a keycode difference. Native apps
  on the normal input pipeline still use the KCM; accessibility/X11 consumers
  handle all shortcuts in their own layer (see
  [`x11/README.md`](x11/README.md) for the top-row X11 keymap).
- X11 window managers may reserve Alt+F4 for **Close Window** (KDE/GNOME).
  Even if a keymap maps F4, the X11 client may never receive Alt+F4; rebind or
  disable the WM shortcut if you need it inside the client.
- If the Lenovo Keyboard Pack menu is missing, use
  **Settings → System → Languages & input → Physical keyboard**.
- TR uses the AOSP Turkish Q layout; Turkish F is not included.
- Home/End are text-editing keys, not the Android Home button.

## Changelog

- **v1.3** — CI-built APKs with the self-contained template; reselect the
  layout after installing or updating. Documented that the
  accessibility/direct-input layer (Lenovo/Yoga, X11) bypasses the KCM for all
  keys.
- **v1.2** — Meta is the only Fn modifier; Ctrl/Alt pass through at the
  Android input layer.
- **v1.1** — EN and TR builds; AI/App keys become Home/End.
- **v1.0** — initial F1–F12 remap.

## License

Apache-2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

The TR base layout is from the Android Open Source Project
(`packages/InputDevices/res/raw/keyboard_layout_turkish.kcm`, Apache-2.0).
The v1.0–v1.2 APKs in `apk/` were packaged with the ExKeyMo template by
ris58h. The CI build uses an original minimal layout-provider template.
