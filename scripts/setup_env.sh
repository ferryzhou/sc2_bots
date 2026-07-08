#!/usr/bin/env bash
# Set up everything needed to develop and run SC2 bots headless on Linux:
#   1. Python venv with ares-sc2 (+ burnysc2, SC2MapAnalysis, cython-extensions)
#   2. Blizzard headless StarCraft II Linux client
#   3. Current AI Arena ladder maps
#
# Designed to be idempotent so it can be used as a Claude Code environment
# setup script (the resulting filesystem gets snapshotted/cached) or run
# manually on any Linux box.
#
# Requires network access to: pypi.org, github.com,
#   blzdistsc2-a.akamaihd.net (SC2 client), aiarena.net (maps)

set -euo pipefail

VENV="${VENV:-$HOME/venv}"
SC2PATH="${SC2PATH:-$HOME/StarCraftII}"
SC2_ZIP_URL="https://blzdistsc2-a.akamaihd.net/Linux/SC2.4.10.zip"
# By downloading you agree to the Blizzard AI/ML license (this is the
# documented archive password, see github.com/Blizzard/s2client-proto)
SC2_ZIP_PASSWORD="iagreetotheeula"
MAP_PACK_URLS=(
    # 2025 Season 2, patched for the 4.10 linux client
    "https://aiarena.net/wiki/184/plugin/attachments/download/44/"
    # 2025 PreSeason 2
    "https://aiarena.net/wiki/184/plugin/attachments/download/45/"
)

echo "==> 1/3 Python environment ($VENV)"
if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install --quiet --upgrade pip setuptools wheel
if ! "$VENV/bin/python" -c "import ares" 2>/dev/null; then
    "$VENV/bin/pip" install --quiet "git+https://github.com/AresSC2/ares-sc2.git"
    SP="$("$VENV/bin/python" -c 'import site; print(site.getsitepackages()[0])')"
    # The ares-sc2 wheel installs its package under src/ - expose it on sys.path
    echo "$SP/src" > "$SP/ares_src.pth"
    # sc2_helper (rust combat simulator) ships in the repo but not the wheel
    if [ ! -d "$SP/src/sc2_helper" ]; then
        tmp="$(mktemp -d)"
        git clone --quiet --depth 1 https://github.com/AresSC2/ares-sc2.git "$tmp/ares-sc2"
        cp -r "$tmp/ares-sc2/sc2_helper" "$SP/src/"
        rm -rf "$tmp"
    fi
fi
"$VENV/bin/python" -c "from ares import AresBot; print('    ares-sc2 OK')"

echo "==> 2/3 StarCraft II headless client ($SC2PATH)"
if [ ! -d "$SC2PATH/Versions" ]; then
    tmp_zip="$(mktemp --suffix=.zip)"
    curl -sS -o "$tmp_zip" "$SC2_ZIP_URL"
    unzip -q -P "$SC2_ZIP_PASSWORD" "$tmp_zip" -d "$(dirname "$SC2PATH")"
    rm -f "$tmp_zip"
fi
echo "    $(ls "$SC2PATH/Versions" | head -1) installed"

echo "==> 3/3 Ladder maps ($SC2PATH/Maps)"
mkdir -p "$SC2PATH/Maps"
# python-sc2 expects a lowercase maps dir on linux
[ -e "$SC2PATH/maps" ] || ln -s "$SC2PATH/Maps" "$SC2PATH/maps"
if ! ls "$SC2PATH/Maps"/*.SC2Map >/dev/null 2>&1; then
    for url in "${MAP_PACK_URLS[@]}"; do
        tmp_zip="$(mktemp --suffix=.zip)"
        curl -sSL -o "$tmp_zip" "$url"
        unzip -q -o "$tmp_zip" -d "$SC2PATH/Maps"
        rm -f "$tmp_zip"
    done
fi
echo "    $(ls "$SC2PATH/Maps" | wc -l) maps installed"

echo "Done. Run a game with: $VENV/bin/python phoenix/run.py"
