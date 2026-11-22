# Contributing

## Adding a layout

The build is manifest-driven: one entry in `layouts/manifest.json` and one KCM
file produces one APK. A PR does not need to touch the Android template or the
workflow.

### 1. Add the KCM

A layout is a complete `type OVERLAY` KCM. The KB500U-specific part is the remap
section. The easiest approach:

1. Start from the base KCM for the language (for example
   `layouts/turkish-q-aosp.kcm`).
2. Append the KB500U remap section from `layouts/kb500u-fkeys-en.kcm`
   (everything from `# BEGIN KB500U REMAP` onward).
3. Save it as `layouts/kb500u-fkeys-<id>.kcm`.

`tools/build-tr.py` is a working example of this merge.

### 2. Add a manifest entry

Add an entry to `layouts/manifest.json`:

```json
{
  "id": "de",
  "package": "ris58h.exkeymo_keyboard_layout.de",
  "appName": "ExKeyMo DE",
  "providerLabel": "ExKeyMo DE",
  "layoutLabel": "ExKeyMo Layout DE",
  "kcm": "layouts/kb500u-fkeys-de.kcm",
  "output": "ExKeyMo-KB500U-Fkeys-DE.apk"
}
```

Use a unique package suffix. Do not reuse `.en` or `.tr`. The `output` field is
optional; the builder defaults to `ExKeyMo-KB500U-Fkeys-<ID>.apk`.

### 3. Validate and build

```sh
python3 tools/validate_kcm.py
python3 tools/build_apks.py \
  --ks /path/to/keystore.jks \
  --ks-pass "$KEYSTORE_PASSWORD" \
  --key-alias "$KEY_ALIAS" \
  --key-pass "$KEY_PASSWORD" \
  --out dist
```

Open a PR. CI validates every KCM, builds every layout with a debug key, and
uploads the APKs as the `kb500u-apks` artifact.

## KCM rules for the KB500U top row

Map the physical key to the target keycode at the scan/usage level. The KB500U
top row uses these codes:

| Key | Scan code | HID usage | Target |
|---|---|---|---|
| Silent | 113 | — | F1 |
| Volume Down | 114 | 0x0c00ea | F2 |
| Volume Up | 115 | 0x0c00e9 | F3 |
| Mic Mute | 248 | 0x0c0391 | F4 |
| Brightness Down | 224 | 0x0c0070 | F5 |
| Brightness Up | 225 | 0x0c006f | F6 |
| Trackpad | — | 0x0c0392 | F7 |
| Capture Screen | 99 | 0x0c046 | F8 |
| Full Screen | — | 0x0c0394 | F9 |
| Split Screen | — | 0x0c0395 | F10 |
| Device Collaboration | — | 0x0c0397 | F11 |
| Lock Screen | — | 0x0c038e | F12 |
| Lenovo Smart Key (AI) | — | 0x0c0398 | MOVE_HOME |
| App to Customize | — | 0x0c0399 | MOVE_END |

Use `map key` and `map key usage` lines:

```
map key 248 F4
map key usage 0x0c0391 F4
```

Only Meta should restore the original Lenovo action. Add behaviors to the
target key block, but **do not** add `base`, `ctrl`, or `alt` behaviors — those
would strip Ctrl/Alt and break Alt+F4:

```
key F4 {
    ctrl+alt+meta+shift: replace MUTE
    ctrl+meta+shift: replace MUTE
    alt+meta+shift: replace MUTE
    meta+shift: replace MUTE
    ctrl+alt+meta: replace MUTE
    ctrl+meta: replace MUTE
    alt+meta: replace MUTE
    meta: replace MUTE
}
```

`layouts/kb500u-fkeys-en.kcm` is the reference implementation.

This behavior is at Android's input layer. X11 and other scancode-based
environments bypass the KCM entirely; the remap is not active there.

## Signing and releases

- PR builds use a CI debug key. They cannot update a release install with the
  same package name, so uninstall the release build or use a separate device
  when testing changes to EN/TR. A new layout with a new package suffix installs
  alongside the existing ones.
- After installing a debug APK, reselect the ExKeyMo layout for the Lenovo
  keyboard; Lenovo may reset the layout when the package changes.
- Release tags `v*` use the repository signing secrets and publish a GitHub
  release automatically.
- Maintainers: bump `versionCode` in `layouts/manifest.json` before tagging.

## License

By contributing, you agree to license your work under Apache-2.0. If a layout is
based on another project, include its license and attribution in the PR and in
`NOTICE`.
