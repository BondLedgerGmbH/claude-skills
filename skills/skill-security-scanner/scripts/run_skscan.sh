#!/usr/bin/env bash
# Wrapper to run skscan against a target skill directory.
#
# skscan's npm package (as of 0.1.1) is broken: it declares a
# "workspace:*" dependency on @skvault/scanner, which is never published
# to npm. Both `npx` and `pnpm dlx` fail. This script works around the
# issue by cloning the monorepo and building from source.
#
# Usage: ./run_skscan.sh <path-to-scan>

set -euo pipefail

TARGET="${1:?Usage: run_skscan.sh <path-to-scan>}"

if [ ! -e "$TARGET" ]; then
    echo "ERROR: Target path does not exist: $TARGET" >&2
    exit 1
fi

# --- Attempt 1: npx (in case the npm package is eventually fixed) ---
if npx skscan@latest "$TARGET" 2>/dev/null; then
    exit 0
fi

echo "[skscan] npx failed (known workspace:* packaging bug). Building from source..." >&2

# --- Attempt 2: Build from GitHub source ---
SKSCAN_CACHE="${SKSCAN_CACHE_DIR:-$HOME/.cache/skscan}"

# Reuse cached build if it exists and is less than 7 days old
if [ -x "$SKSCAN_CACHE/apps/cli/dist/index.js" ]; then
    cache_age=$(( $(date +%s) - $(stat -f %m "$SKSCAN_CACHE/apps/cli/dist/index.js" 2>/dev/null || echo 0) ))
    if [ "$cache_age" -lt 604800 ]; then
        node "$SKSCAN_CACHE/apps/cli/dist/index.js" "$TARGET"
        exit 0
    fi
fi

# Need pnpm to build the monorepo
if ! command -v pnpm &>/dev/null; then
    echo "[skscan] ERROR: pnpm is required to build skscan from source." >&2
    echo "[skscan] Install with: npm install -g pnpm" >&2
    echo "[skscan] Skipping automated scan — proceed with manual audit." >&2
    exit 1
fi

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "[skscan] Cloning github.com/Khaledgarbaya/skillvault..." >&2
git clone --depth 1 --quiet https://github.com/Khaledgarbaya/skillvault.git "$TMPDIR/skillvault" 2>&1 >&2

echo "[skscan] Installing dependencies..." >&2
(cd "$TMPDIR/skillvault" && pnpm install --silent 2>&1 >&2)

echo "[skscan] Building @skvault/scanner..." >&2
(cd "$TMPDIR/skillvault" && pnpm --filter @skvault/scanner build --silent 2>&1 >&2)

echo "[skscan] Building skscan CLI..." >&2
(cd "$TMPDIR/skillvault" && pnpm --filter skscan build --silent 2>&1 >&2)

# Cache the built repo for future runs
mkdir -p "$(dirname "$SKSCAN_CACHE")"
rm -rf "$SKSCAN_CACHE"
cp -R "$TMPDIR/skillvault" "$SKSCAN_CACHE"

echo "[skscan] Build complete. Running scan..." >&2
node "$SKSCAN_CACHE/apps/cli/dist/index.js" "$TARGET"
