#!/usr/bin/env bash
# ABOUTME: Run Chainlit UI for any domain in development mode
# Usage: ./run_ui.sh <domain> [port]
# Example: ./run_ui.sh demo 1337
#          ./run_ui.sh nurture 1338

set -euo pipefail

# Check if domain argument is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <domain> [port]"
    echo "Example: $0 demo 1337"
    echo "         $0 nurture 1338"
    exit 1
fi

DOMAIN="$1"
PORT="${2:-1337}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Validate that the domain exists
DOMAIN_PATH="src/autobots_agents_jarvis/domains/$DOMAIN"
if [ ! -d "$DOMAIN_PATH" ]; then
    echo "Error: Domain '$DOMAIN' not found at $DOMAIN_PATH"
    echo "Available domains:"
    ls -1 src/autobots_agents_jarvis/domains/ | grep -v "^__"
    exit 1
fi

# Set config directory
export DYNAGENT_CONFIG_ROOT_DIR="${DYNAGENT_CONFIG_ROOT_DIR:-agent_configs/$DOMAIN}"

echo "Starting $DOMAIN on http://localhost:$PORT"
echo "Config directory: $DYNAGENT_CONFIG_ROOT_DIR"

# Run Chainlit
chainlit run "$DOMAIN_PATH/server.py" --port "$PORT" --host 0.0.0.0
