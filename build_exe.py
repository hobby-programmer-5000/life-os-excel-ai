"""
=============================================================================
📦 ALL-IN-ONE LIFE OS : Standalone Windows EXE Builder (PyInstaller)
=============================================================================
Keeps canonical binary filename 'LifeOS_Assistant_v2.exe' while embedding
system-language PE Version Metadata (ProductName, FileDescription) and
bundling full 4-language (ko / en / ja / zh) support.
=============================================================================
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

from i18n import (
    resolve_language,
    tr,
    get_app_name,
    get_app_description,
    PE_LOCALE_TABLE,
)
from app_icon import generate_icon_assets, get_app_icon_paths
from ui_theme import get_lucide_dir

# Set console encoding to UTF-8
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent


def generate_version_info_file(out_path: Path, lang: str = None) -> Path:
    """Create a UTF-8 PyInstaller VSVersionInfo resource file localized to the build language."""
    resolved = resolve_language(lang)
    table_id, lcid = PE_LOCALE_TABLE.get(resolved, ("040904B0", 1033))
    app_name = get_app_name(resolved).replace("'", "\\'")
    app_desc = get_app_description(resolved).replace("'", "\\'")

    content = (
        "# UTF-8\n"
        "VSVersionInfo(\n"
        "  ffi=FixedFileInfo(\n"
        "    filevers=(2, 0, 0, 0),\n"
        "    prodvers=(2, 0, 0, 0),\n"
        "    mask=0x3f,\n"
        "    flags=0x0,\n"
        "    OS=0x40004,\n"
        "    fileType=0x1,\n"
        "    subtype=0x0,\n"
        "    date=(0, 0)\n"
        "  ),\n"
        "  kids=[\n"
        "    StringFileInfo([\n"
        "      StringTable(\n"
        f"        '{table_id}',\n"
        "        [\n"
        "          StringStruct('CompanyName', 'Life OS'),\n"
        f"          StringStruct('FileDescription', '{app_desc}'),\n"
        "          StringStruct('FileVersion', '2.0.0.0'),\n"
        "          StringStruct('InternalName', 'LifeOS_Assistant_v2'),\n"
        "          StringStruct('OriginalFilename', 'LifeOS_Assistant_v2.exe'),\n"
        f"          StringStruct('ProductName', '{app_name}'),\n"
        "          StringStruct('ProductVersion', '2.0.0.0')\n"
        "        ]\n"
        "      )\n"
        "    ]),\n"
        f"    VarFileInfo([VarStruct('Translation', [{lcid}, 1200])])\n"
        "  ]\n"
        ")\n"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path


def verify_clean_exe_bundle(exe_path: Path) -> list:
    """Audit PyInstaller archive TOC to ensure no DB, .env, .xlsx, or token files were bundled."""
    from PyInstaller.archive.readers import CArchiveReader
    reader = CArchiveReader(str(exe_path))
    entries = sorted(reader.toc.keys())
    blocked_markers = (".db", ".env", ".xlsx", "token", "secret", ".spec")
    return [n for n in entries if any(m in n.lower() for m in blocked_markers)]


def build(lang: str = None):
    resolved_lang = resolve_language(lang)
    app_name = get_app_name(resolved_lang)
    exe_name = "LifeOS_Assistant_v2.exe"

    print("=" * 65)
    print(tr("build_start", resolved_lang, app_name=app_name, exe_name=exe_name, lang=resolved_lang))
    print("=" * 65)

    entry_script = BASE_DIR / "main_app.py"
    dist_dir = BASE_DIR / "dist"
    build_dir = BASE_DIR / "build"

    version_file = generate_version_info_file(build_dir / f"version_info_{resolved_lang}.txt", resolved_lang)
    ico_path, png_path = get_app_icon_paths()
    if not ico_path.is_file() or not png_path.is_file():
        ico_path, png_path = generate_icon_assets(BASE_DIR / "assets")
    lucide_dir = get_lucide_dir()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name", "LifeOS_Assistant_v2",
        "--hidden-import", "i18n",
        "--hidden-import", "i18n_habits",
        "--hidden-import", "i18n_personas",
        "--hidden-import", "bot_commands",
        "--hidden-import", "discord_bot",
        "--hidden-import", "app_icon",
        "--hidden-import", "ui_theme",
        "--add-data", f"{ico_path}{os.pathsep}assets",
        "--add-data", f"{png_path}{os.pathsep}assets",
        "--add-data", f"{lucide_dir}{os.pathsep}assets/icons/lucide",
        "--specpath", str(build_dir),
        "--clean",
    ]
    if sys.platform.startswith("win") and ico_path.is_file():
        cmd.extend(["--icon", str(ico_path)])
    if sys.platform.startswith("win") and version_file.is_file():
        cmd.extend(["--version-file", str(version_file)])
    cmd.append(str(entry_script))

    print(tr("build_cmd", resolved_lang, cmd=" ".join(cmd)) + "\n")
    res = subprocess.run(cmd, cwd=str(BASE_DIR))

    if res.returncode == 0:
        exe_path = dist_dir / exe_name
        leaked = verify_clean_exe_bundle(exe_path)
        if leaked:
            print(f"[!] Privacy audit failed inside EXE archive: {leaked}")
            sys.exit(1)
        print("\n" + "=" * 65)
        print(tr("build_success", resolved_lang, path=exe_path, app_name=app_name))
        print("=" * 65)
    else:
        print("\n" + tr("build_fail", resolved_lang))
        sys.exit(res.returncode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build standalone Life OS executable")
    parser.add_argument("--lang", type=str, default=None, help="Override PE version language (ko, en, ja, zh)")
    args = parser.parse_args()
    build(lang=args.lang)
