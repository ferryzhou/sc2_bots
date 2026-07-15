#!/usr/bin/env bash
# Set up everything needed to develop and run SC2 bots headless on Linux:
#   1. Python venv with ares-sc2 (+ burnysc2, SC2MapAnalysis, cython-extensions)
#   2. Blizzard headless StarCraft II Linux client
#   3. Current AI Arena ladder maps
#   4. Python 3.12 venv matching the AI Arena ladder runtime - used to build
#      the ladder zip (scripts/create_ladder_zip.py) and to run downloaded
#      opponent bots (harness/versus.py, harness/download_bots.py)
#
# Designed to be idempotent so it can be used as a Claude Code environment
# setup script (the resulting filesystem gets snapshotted/cached) or run
# manually on any Linux box.
#
# Requires network access to: pypi.org, github.com,
#   blzdistsc2-a.akamaihd.net (SC2 client), aiarena.net (maps)

set -euo pipefail

VENV="${VENV:-$HOME/venv}"
VENV312="${VENV312:-/root/venv312}"
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

echo "==> 2/4 Python 3.12 ladder toolchain ($VENV312)"
if [ ! -x "$VENV312/bin/python" ]; then
    "$VENV/bin/pip" install --quiet uv
    "$VENV/bin/uv" python install 3.12
    "$VENV/bin/uv" venv --python 3.12 "$VENV312"
    "$VENV/bin/uv" pip install --python "$VENV312/bin/python" --quiet \
        pip setuptools wheel
fi
if ! "$VENV312/bin/python" -c "import ares" 2>/dev/null; then
    "$VENV312/bin/pip" install --quiet "git+https://github.com/AresSC2/ares-sc2.git"
    SP312="$("$VENV312/bin/python" -c 'import site; print(site.getsitepackages()[0])')"
    echo "$SP312/src" > "$SP312/ares_src.pth"
    if [ ! -d "$SP312/src/sc2_helper" ]; then
        tmp="$(mktemp -d)"
        git clone --quiet --depth 1 https://github.com/AresSC2/ares-sc2.git "$tmp/ares-sc2"
        cp -r "$tmp/ares-sc2/sc2_helper" "$SP312/src/"
        rm -rf "$tmp"
    fi
    # extra packages the AI Arena image provides - downloaded opponent bots
    # (harness/versus.py) expect them
    "$VENV312/bin/pip" install --quiet pillow matplotlib requests async_timeout
fi
"$VENV312/bin/python" -c "from ares import AresBot; print('    ares-sc2 on 3.12 OK')"

echo "==> 3/4 StarCraft II headless client ($SC2PATH)"
if [ ! -d "$SC2PATH/Versions" ]; then
    tmp_zip="$(mktemp --suffix=.zip)"
    curl -sS -o "$tmp_zip" "$SC2_ZIP_URL"
    unzip -q -P "$SC2_ZIP_PASSWORD" "$tmp_zip" -d "$(dirname "$SC2PATH")"
    rm -f "$tmp_zip"
fi
echo "    $(ls "$SC2PATH/Versions" | head -1) installed"

echo "==> 4/4 Ladder maps ($SC2PATH/Maps)"
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

echo "==> Replay analysis toolchain (sc2reader)"
# analysis/*.py parse replays with sc2reader, which needs mpyq. mpyq's setup.py
# fails to build on recent setuptools, but it is a single pure-Python module, so
# vendor it directly then install sc2reader without deps (see
# analysis/principle_analyzer.py).
if ! "$VENV/bin/python" -c "import sc2reader, mpyq" 2>/dev/null; then
    SP="$("$VENV/bin/python" -c 'import site; print(site.getsitepackages()[0])')"
    if ! "$VENV/bin/python" -c "import mpyq" 2>/dev/null; then
        tmp="$(mktemp -d)"
        "$VENV/bin/pip" download mpyq --no-deps --no-binary :all: -d "$tmp" >/dev/null
        tar xzf "$tmp"/mpyq-*.tar.gz -C "$tmp"
        cp "$tmp"/mpyq-*/mpyq.py "$SP/"
        rm -rf "$tmp"
    fi
    "$VENV/bin/pip" install --quiet sc2reader --no-deps
fi
"$VENV/bin/python" -c "import sc2reader; print('    sc2reader', sc2reader.__version__, 'OK')"

echo "Done."
echo "  Local game:        $VENV/bin/python phoenix/run.py"
echo "  Gauntlet:          $VENV/bin/python harness/gauntlet.py --games 6"
echo "  Download opponents: AIARENA_API_TOKEN=... $VENV/bin/python harness/download_bots.py"
echo "  Versus opponents:  $VENV312/bin/python harness/versus.py --opponent <name>"
echo "  Ladder zip:        $VENV312/bin/python scripts/create_ladder_zip.py"
echo "  Analyze replays:   $VENV/bin/python analysis/analyze_aegis_replays.py <run_id>"
