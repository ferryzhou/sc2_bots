"""Build an AI Arena ladder zip for a repo bot (PhoenixBot or GriffinBot).

Packages the bot plus all non-standard dependencies as plain packages at the
zip root (the arena runs `python run.py ...` from the extracted zip, so the
zip root is on sys.path). Compiled extensions are taken from a site-packages
tree, so run this with / point it at a venv whose Python version matches the
AI Arena ladder (currently 3.12):

    python scripts/create_ladder_zip.py --site-packages \
        /root/venv312/lib/python3.12/site-packages
    python scripts/create_ladder_zip.py --bot griffin

Output: <BotName>.zip in the repo root.
"""

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# dir name -> (ladder bot name, builds yml consumed by the ares build runner)
BOT_REGISTRY = {
    "phoenix": ("PhoenixBot", "protoss_builds.yml"),
    "griffin": ("GriffinBot", "terran_builds.yml"),
    "aegis": ("AegisBot", "terran_builds.yml"),
}

BOT_FILES = ["run.py", "ladder.py", "config.yml"]
BOT_PACKAGE = "bot"

# package dirs harvested from site-packages (ares installs under src/)
DEPENDENCIES = {
    "ares": "src/ares",
    "sc2_helper": "src/sc2_helper",
    "sc2": "sc2",
    "map_analyzer": "map_analyzer",
    "cython_extensions": "cython_extensions",
}

IGNORE_SUFFIXES = (".pyx", ".pyi", ".c", ".pyd", ".h")
IGNORE_DIRS = {"__pycache__", "pickle_gameinfo", "tests", "docs"}
# sc2_helper ships binaries for many platforms/versions; keep only the
# linux one matching the target python
SC2_HELPER_KEEP = "sc2_helper.cpython-{v}-x86_64-linux-gnu.so"


def copy_package(src: Path, dst: Path, py_tag: str) -> None:
    def ignore(directory, names):
        skip = set()
        for name in names:
            p = Path(directory) / name
            if name in IGNORE_DIRS or name.endswith(IGNORE_SUFFIXES):
                skip.add(name)
            elif p.suffix in (".so",) and "sc2_helper" in name:
                if name != SC2_HELPER_KEEP.format(v=py_tag):
                    skip.add(name)
            elif p.suffix == ".so" and f"cpython-{py_tag}" not in name:
                # compiled for a different python version - useless on ladder
                skip.add(name)
        return skip

    shutil.copytree(src, dst, ignore=ignore)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bot", default="phoenix", choices=sorted(BOT_REGISTRY),
                        help="which repo bot to package")
    parser.add_argument(
        "--site-packages",
        default="/root/venv312/lib/python3.12/site-packages",
        help="site-packages of a venv matching the ladder python version",
    )
    parser.add_argument("--py-tag", default="312", help="cpython tag, e.g. 312")
    parser.add_argument("--output", default=None,
                        help="default: <BotName>.zip in the repo root")
    args = parser.parse_args()

    bot_name, builds_yml = BOT_REGISTRY[args.bot]
    bot_dir = REPO_ROOT / args.bot
    output = args.output or str(REPO_ROOT / f"{bot_name}.zip")

    sp = Path(args.site_packages)
    if not (sp / "src" / "ares").is_dir():
        sys.exit(f"ares not found under {sp} - install ares-sc2 there first")

    staging = Path(tempfile.mkdtemp(prefix="ladder_zip_"))
    try:
        for name in [*BOT_FILES, builds_yml]:
            shutil.copy2(bot_dir / name, staging / name)
        copy_package(bot_dir / BOT_PACKAGE, staging / BOT_PACKAGE, args.py_tag)
        for dst_name, rel_src in DEPENDENCIES.items():
            copy_package(sp / rel_src, staging / dst_name, args.py_tag)

        out = Path(output)
        out.unlink(missing_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(staging.rglob("*")):
                if f.is_file():
                    zf.write(f, f.relative_to(staging))
        print(f"Wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")
    finally:
        shutil.rmtree(staging, ignore_errors=True)


if __name__ == "__main__":
    main()
