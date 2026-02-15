#!/usr/bin/env bash
# ABOUTME: Orchestrator for sanity tests - validates Dynagent via Concierge canary.
# Supports separate-clone CI via SHARED_LIB_DIR, CONCIERGE_DIR, WS_ROOT, VENV.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONCIERGE_DIR="${CONCIERGE_DIR:-$(cd "$SCRIPT_DIR/.." && pwd)}"
WS_ROOT="${WS_ROOT:-$(cd "$CONCIERGE_DIR/.." && pwd)}"
SHARED_LIB_DIR="${SHARED_LIB_DIR:-$WS_ROOT/autobots-devtools-shared-lib}"
VENV="${VENV:-$WS_ROOT/.venv}"
ENV_FILE="${ENV_FILE:-$CONCIERGE_DIR/.env}"

cd "$WS_ROOT"

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: Missing env file at $ENV_FILE" >&2
  exit 1
fi

# Export vars from .env so pytest (child process) inherits them
set -a
source "$ENV_FILE"
set +a

# 1. Validate (supports separate CI clones via SHARED_LIB_DIR, JARVIS_DIR)
if [ ! -d "$SHARED_LIB_DIR" ]; then
  echo "Error: Missing shared-lib at $SHARED_LIB_DIR" >&2
  exit 1
fi
if [ ! -d "$CONCIERGE_DIR" ]; then
  echo "Error: Missing concierge at $CONCIERGE_DIR" >&2
  exit 1
fi

# 2. Pre-check: GOOGLE_API_KEY required for sanity tests
if [ -z "${GOOGLE_API_KEY:-}" ] || [ ${#GOOGLE_API_KEY} -lt 20 ]; then
  echo "Error: GOOGLE_API_KEY must be set (and at least 20 chars) for sanity tests" >&2
  exit 1
fi

# 3. Setup (unless CI provides pre-built env)
if [ "${SANITY_SKIP_SETUP:-0}" != "1" ]; then
  if [ -f "$WS_ROOT/Makefile" ]; then
    make setup install install-dev
  else
    echo "Warning: No Makefile at $WS_ROOT - skipping setup. Set SANITY_SKIP_SETUP=1 and ensure venv has shared-lib + concierge installed." >&2
  fi
fi

if [ ! -x "$VENV/bin/python" ]; then
  echo "Error: Missing venv at $VENV - run setup first or set VENV" >&2
  exit 1
fi

# 4. Ensure Playwright browsers are installed (for UI test)
if "$VENV/bin/python" -c "import playwright" 2>/dev/null; then
  "$VENV/bin/python" -m playwright install chromium
fi

# 5. Run sanity tests
cd "$CONCIERGE_DIR"
"$VENV/bin/python" -m pytest "$CONCIERGE_DIR/tests/sanity" -v -m sanity
