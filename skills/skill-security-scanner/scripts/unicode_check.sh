#!/usr/bin/env bash
# Detect hidden/invisible Unicode characters in files that could be used
# for prompt injection or obfuscation in AI skill packages.
#
# Usage: ./unicode_check.sh <path-to-scan>
#
# Supports macOS (uses perl fallback since macOS grep lacks -P/PCRE).

set -euo pipefail

TARGET="${1:-.}"

if [ ! -e "$TARGET" ]; then
    echo "ERROR: Target path does not exist: $TARGET"
    exit 1
fi

echo "=== Unicode Security Scan ==="
echo "Target: $TARGET"
echo ""

# Determine if we have PCRE grep available
USE_PCRE=false
GREP_CMD=""
if command -v ggrep &>/dev/null; then
    GREP_CMD="ggrep"
    USE_PCRE=true
elif echo "" | grep -P '' 2>/dev/null; then
    GREP_CMD="grep"
    USE_PCRE=true
fi

# Helper: search with proper exit code handling.
# Uses grep -P if available, otherwise perl with explicit exit code.
run_search() {
    local label="$1"
    local grep_pattern="$2"
    local perl_pattern="$3"
    local max_lines="${4:-20}"

    echo "--- $label ---"

    local output=""
    if [ "$USE_PCRE" = true ]; then
        output=$("$GREP_CMD" -rnP "$grep_pattern" "$TARGET" 2>/dev/null | head -"$max_lines") || true
    else
        output=$(find "$TARGET" -type f -print0 2>/dev/null | \
            xargs -0 perl -CSD -ne \
            "if (/$perl_pattern/) { print \"\$ARGV:\$.: \$_\"; }" \
            2>/dev/null | head -"$max_lines") || true
    fi

    if [ -n "$output" ]; then
        echo "$output"
        echo "[!] $label: FOUND!"
        return 0
    else
        echo "[OK] $label: Clean."
        return 1
    fi
}

TOTAL_FINDINGS=0

# --- Check 1: Zero-width and bidirectional control characters ---
if run_search "Zero-Width & Bidirectional Characters" \
    '[\x{200B}\x{200C}\x{200D}\x{200E}\x{200F}\x{202A}\x{202B}\x{202C}\x{202D}\x{202E}\x{2060}\x{2061}\x{2062}\x{2063}\x{2064}\x{FEFF}]' \
    '[\x{200B}\x{200C}\x{200D}\x{200E}\x{200F}\x{202A}\x{202B}\x{202C}\x{202D}\x{202E}\x{2060}\x{2061}\x{2062}\x{2063}\x{2064}\x{FEFF}]'; then
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
fi
echo ""

# --- Check 2: Tag characters (U+E0001 to U+E007F) ---
if run_search "Tag Characters (U+E0001-U+E007F)" \
    '[\x{E0001}-\x{E007F}]' \
    '[\x{E0001}-\x{E007F}]'; then
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
fi
echo ""

# --- Check 3: Homoglyphs (Cyrillic/Greek lookalikes) ---
if run_search "Potential Homoglyphs (Cyrillic/Greek)" \
    '[а-яА-ЯёЁ]|[αβγδεζηθικλμνξοπρστυφχψω]' \
    '[\x{0430}-\x{044F}\x{0410}-\x{042F}\x{0451}\x{0401}]|[\x{03B1}-\x{03C9}]'; then
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
fi
echo ""

# --- Check 4: Base64 blobs (40+ chars) ---
if run_search "Potential Base64 Encoded Payloads" \
    '[A-Za-z0-9+/]{40,}={0,2}' \
    '[A-Za-z0-9+\/]{40,}={0,2}'; then
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
fi
echo ""

# --- Check 5: Hex-encoded sequences (4+ consecutive \xNN) ---
if run_search "Hex-Encoded Sequences" \
    '(\\x[0-9a-fA-F]{2}){4,}' \
    '(\\x[0-9a-fA-F]{2}){4,}'; then
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
fi
echo ""

# --- Check 6: HTML entity sequences (3+ consecutive entities) ---
if run_search "HTML Entity Sequences" \
    '(&#x?[0-9a-fA-F]+;){3,}' \
    '(\&\#x?[0-9a-fA-F]+;){3,}'; then
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
fi
echo ""

# --- Check 7: Unicode escape sequences (3+ consecutive \uNNNN) ---
if run_search "Unicode Escape Sequences" \
    '(\\u[0-9a-fA-F]{4}){3,}' \
    '(\\u[0-9a-fA-F]{4}){3,}'; then
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
fi
echo ""

# --- Check 8: File type vs extension mismatch ---
echo "--- File Type Verification ---"
MISMATCHES=0
while IFS= read -r -d '' f; do
    detected=$(file -b "$f" 2>/dev/null || echo "unknown")
    ext="${f##*.}"
    mismatch=false
    case "$ext" in
        md|txt|yaml|yml|json|toml|cfg|ini|conf|csv)
            if ! echo "$detected" | grep -qi "text\|json\|empty\|ascii"; then
                mismatch=true
            fi
            ;;
        png)
            if ! echo "$detected" | grep -qi "png\|image"; then mismatch=true; fi
            ;;
        jpg|jpeg)
            if ! echo "$detected" | grep -qi "jpeg\|image"; then mismatch=true; fi
            ;;
        gif)
            if ! echo "$detected" | grep -qi "gif\|image"; then mismatch=true; fi
            ;;
        svg)
            if ! echo "$detected" | grep -qi "svg\|xml\|text"; then mismatch=true; fi
            ;;
        sh|bash|zsh)
            if ! echo "$detected" | grep -qi "text\|script\|ascii\|empty"; then mismatch=true; fi
            ;;
        py)
            if ! echo "$detected" | grep -qi "text\|script\|python\|ascii\|empty"; then mismatch=true; fi
            ;;
        js|ts)
            if ! echo "$detected" | grep -qi "text\|script\|ascii\|empty"; then mismatch=true; fi
            ;;
        exe|dll)
            # These are inherently suspicious in a skill package regardless
            echo "[!] SUSPICIOUS: Binary executable found: $f ($detected)"
            MISMATCHES=$((MISMATCHES + 1))
            ;;
    esac
    if [ "$mismatch" = true ]; then
        echo "[!] MISMATCH: $f (ext: .$ext, actual: $detected)"
        MISMATCHES=$((MISMATCHES + 1))
    fi
done < <(find "$TARGET" -type f -print0 2>/dev/null)
if [ "$MISMATCHES" -eq 0 ]; then
    echo "[OK] No file type mismatches detected."
else
    echo "[!] $MISMATCHES file type issue(s) found."
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
fi
echo ""

# --- Check 9: Extended attributes (macOS) ---
if command -v xattr &>/dev/null; then
    echo "--- Extended Attributes (macOS) ---"
    XATTR_COUNT=0
    while IFS= read -r -d '' f; do
        attrs=$(xattr "$f" 2>/dev/null || true)
        if [ -n "$attrs" ]; then
            echo "[!] $f has xattrs: $attrs"
            XATTR_COUNT=$((XATTR_COUNT + 1))
        fi
    done < <(find "$TARGET" -type f -print0 2>/dev/null)
    if [ "$XATTR_COUNT" -eq 0 ]; then
        echo "[OK] No extended attributes found."
    else
        echo "[!] $XATTR_COUNT file(s) with extended attributes."
        TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
    fi
    echo ""
fi

# --- Check 10: Symlinks ---
echo "--- Symlink Analysis ---"
SYMLINK_OUTPUT=$(find "$TARGET" -type l 2>/dev/null || true)
if [ -n "$SYMLINK_OUTPUT" ]; then
    while IFS= read -r link; do
        link_target=$(readlink "$link" 2>/dev/null || echo "unresolvable")
        # Check if symlink escapes the skill directory
        real_target=$(cd "$(dirname "$link")" && realpath "$link_target" 2>/dev/null || echo "unresolvable")
        real_skill_dir=$(realpath "$TARGET" 2>/dev/null)
        if [[ "$real_target" != "$real_skill_dir"* ]]; then
            echo "[!] ESCAPE: $link -> $link_target (resolves outside skill directory)"
        else
            echo "[WARN] SYMLINK: $link -> $link_target"
        fi
    done <<< "$SYMLINK_OUTPUT"
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
else
    echo "[OK] No symlinks found."
fi
echo ""

# --- Check 11: Suspicious filenames ---
echo "--- Filename Analysis ---"
BAD_NAMES=0
while IFS= read -r -d '' f; do
    basename=$(basename "$f")
    if echo "$basename" | grep -qE '[$`|;(){}]|\.\./' 2>/dev/null; then
        echo "[!] SUSPICIOUS FILENAME: $f"
        BAD_NAMES=$((BAD_NAMES + 1))
    fi
    # Check for extremely long filenames (> 200 chars)
    if [ "${#basename}" -gt 200 ]; then
        echo "[!] LONG FILENAME (${#basename} chars): $f"
        BAD_NAMES=$((BAD_NAMES + 1))
    fi
done < <(find "$TARGET" -print0 2>/dev/null)
if [ "$BAD_NAMES" -eq 0 ]; then
    echo "[OK] No suspicious filenames found."
else
    echo "[!] $BAD_NAMES suspicious filename(s) found."
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
fi
echo ""

# --- Check 12: .git directory (may contain secrets in history) ---
echo "--- Git Repository Check ---"
if [ -d "$TARGET/.git" ]; then
    echo "[!] .git directory found — commit history may contain secrets."
    echo "    Run: git -C \"$TARGET\" log --all --oneline | wc -l  (to check history size)"
    echo "    Run: git -C \"$TARGET\" log --all --diff-filter=D --name-only  (to find deleted files)"
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
else
    echo "[OK] No .git directory found."
fi
echo ""

# --- Summary ---
echo "=== Scan Complete ==="
echo "Total categories with findings: $TOTAL_FINDINGS"
if [ "$TOTAL_FINDINGS" -eq 0 ]; then
    echo "Result: No automated findings (manual review still required)."
else
    echo "Result: $TOTAL_FINDINGS category/categories flagged — review above."
fi
