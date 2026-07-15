#!/bin/bash
# SessionStart hook: prepare a Claude Code on the web session to develop and
# run the SC2 bots. Installs the ares-sc2 Python venvs, the Blizzard headless
# StarCraft II client, and the AI Arena ladder maps by delegating to the
# repo's idempotent scripts/setup_env.sh.
#
# Only runs in the remote (web) environment; on a local machine developers run
# scripts/setup_env.sh themselves. The heavy downloads (SC2 client + maps) are
# cached in the container snapshot after the first successful run, so repeat
# sessions start fast.
set -euo pipefail

# Only bother in Claude Code on the web; skip on local machines.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
    exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

bash "$PROJECT_DIR/scripts/setup_env.sh"

# Persist the SC2 client location for the rest of the session so the bots and
# harness can find it without re-deriving it.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    echo "export SC2PATH=\"${SC2PATH:-$HOME/StarCraftII}\"" >> "$CLAUDE_ENV_FILE"
fi
