#!/usr/bin/env python3
"""Build one signed APK per layout listed in layouts/manifest.json."""
from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "template"


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def find_tool(explicit: str | None, name: str) -> str:
    if explicit:
        return explicit
    found = shutil.which(name)
    if not found:
        raise SystemExit(f"error: {name} not found in PATH")
    return found


def find_android_jar(explicit: str | None, target_sdk: int) -> str:
    if explicit:
        return explicit
    for env in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        sdk = os.environ.get(env)
        if not sdk:
            continue
        platforms = Path(sdk) / "platforms"
        exact = platforms / f"android-{target_sdk}" / "android.jar"
        if exact.exists():
            return str(exact)
        candidates = sorted(platforms.glob("android-*/android.jar"))
        if candidates:
            return str(candidates[-1])
    local = Path("/system/framework/framework-res.apk")
    if local.exists():
        return str(local)
    raise SystemExit("error: Android framework jar not found; pass --android-jar")


def render(template_path: Path, replacements: dict[str, str]) -> str:
    text = template_path.read_text()
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def build_layout(layout: dict, settings: dict, args: argparse.Namespace,
                 tools: dict[str, str], android_jar: str) -> Path:
    layout_id = layout["id"]
    version_code = args.version_code or settings["versionCode"]
    version_name = args.version_name or settings["versionName"]
    min_sdk = args.min_sdk or settings["minSdk"]
    target_sdk = args.target_sdk or settings["targetSdk"]

    kcm_path = ROOT / layout["kcm"]
    if not kcm_path.is_file():
        raise SystemExit(f"error: KCM not found for {layout_id}: {kcm_path}")

    work = Path(tempfile.mkdtemp(prefix=f"kb500u-{layout_id}-"))
    try:
        res = work / "res"
        (res / "values").mkdir(parents=True)
        (res / "xml").mkdir(parents=True)
        (res / "raw").mkdir(parents=True)

        strings = render(TEMPLATE / "res/values/strings.xml", {
            "APP_NAME": html.escape(layout["appName"]),
            "PROVIDER_LABEL": html.escape(layout["providerLabel"]),
            "LAYOUT_LABEL": html.escape(layout["layoutLabel"]),
        })
        (res / "values/strings.xml").write_text(strings)

        manifest = render(TEMPLATE / "AndroidManifest.xml", {
            "PACKAGE": layout["package"],
            "VERSION_CODE": str(version_code),
            "VERSION_NAME": html.escape(version_name),
            "MIN_SDK": str(min_sdk),
            "TARGET_SDK": str(target_sdk),
        })
        (work / "AndroidManifest.xml").write_text(manifest)

        shutil.copy2(TEMPLATE / "res/xml/keyboard_layouts.xml",
                     res / "xml/keyboard_layouts.xml")
        shutil.copy2(kcm_path, res / "raw/keyboard_layout.kcm")

        compiled = work / "compiled.zip"
        unsigned = work / "unsigned.apk"
        aligned = work / "aligned.apk"
        run([tools["aapt2"], "compile", "--dir", str(res), "-o", str(compiled)])
        run([tools["aapt2"], "link", "-o", str(unsigned), "-I", android_jar,
             "--manifest", str(work / "AndroidManifest.xml"), str(compiled),
             "--min-sdk-version", str(min_sdk),
             "--target-sdk-version", str(target_sdk)])

        classes = work / "classes"
        classes.mkdir()
        java_file = TEMPLATE / "src/io/github/nckirik/kb500u/Placeholder.java"
        run([tools["javac"], "-d", str(classes), str(java_file)])
        run([tools["d8"], "--min-api", str(min_sdk), "--output", str(work),
             str(classes / "io/github/nckirik/kb500u/Placeholder.class")])

        with zipfile.ZipFile(unsigned, "a", compression=zipfile.ZIP_DEFLATED) as apk:
            apk.write(work / "classes.dex", "classes.dex")

        run([tools["zipalign"], "-f", "4", str(unsigned), str(aligned)])

        output_name = layout.get("output") or f"ExKeyMo-KB500U-Fkeys-{layout_id.upper()}.apk"
        output = Path(args.out) / output_name
        output.parent.mkdir(parents=True, exist_ok=True)
        run([tools["apksigner"], "sign",
             "--ks", args.ks,
             "--ks-key-alias", args.key_alias,
             "--ks-pass", f"pass:{args.ks_pass}",
             "--key-pass", f"pass:{args.key_pass}",
             "--out", str(output), str(aligned)])
        run([tools["apksigner"], "verify", "--min-sdk-version", str(min_sdk),
             str(output)])
        print(f"built {output} (package {layout['package']}, v{version_name})")
        return output
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(ROOT / "layouts/manifest.json"))
    parser.add_argument("--out", default=str(ROOT / "dist"))
    parser.add_argument("--ks", required=True, help="signing keystore")
    parser.add_argument("--ks-pass", default=os.environ.get("KEYSTORE_PASSWORD"))
    parser.add_argument("--key-alias", default=os.environ.get("KEY_ALIAS"))
    parser.add_argument("--key-pass", default=os.environ.get("KEY_PASSWORD"))
    parser.add_argument("--only", action="append", default=[],
                        help="build only this layout id (repeatable)")
    parser.add_argument("--version-code", type=int)
    parser.add_argument("--version-name")
    parser.add_argument("--min-sdk", type=int)
    parser.add_argument("--target-sdk", type=int)
    parser.add_argument("--android-jar")
    parser.add_argument("--aapt2")
    parser.add_argument("--zipalign")
    parser.add_argument("--apksigner")
    parser.add_argument("--javac")
    parser.add_argument("--d8")
    args = parser.parse_args()

    if not (args.ks_pass and args.key_alias and args.key_pass):
        raise SystemExit("error: --ks-pass, --key-alias and --key-pass are required")

    manifest_path = Path(args.manifest)
    settings = json.loads(manifest_path.read_text())
    layouts = settings["layouts"]
    if args.only:
        wanted = set(args.only)
        layouts = [layout for layout in layouts if layout["id"] in wanted]
        if not layouts:
            raise SystemExit(f"error: no layouts matched {sorted(wanted)}")

    packages = [layout["package"] for layout in layouts]
    duplicates = {package for package in packages if packages.count(package) > 1}
    if duplicates:
        raise SystemExit(f"error: duplicate package names: {sorted(duplicates)}")

    tools = {
        "aapt2": find_tool(args.aapt2, "aapt2"),
        "zipalign": find_tool(args.zipalign, "zipalign"),
        "apksigner": find_tool(args.apksigner, "apksigner"),
        "javac": find_tool(args.javac, "javac"),
        "d8": find_tool(args.d8, "d8"),
    }
    target_sdk = args.target_sdk or settings["targetSdk"]
    android_jar = find_android_jar(args.android_jar, target_sdk)
    print(f"framework: {android_jar}")
    print(f"tools: {tools}")

    outputs = []
    for layout in layouts:
        outputs.append(build_layout(layout, settings, args, tools, android_jar))

    print("\nAPKs:")
    for output in outputs:
        print(f"  {output}")


if __name__ == "__main__":
    main()
