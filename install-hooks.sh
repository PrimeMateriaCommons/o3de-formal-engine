#!/usr/bin/env bash
# Install and configure local git pre-commit hooks for o3de-lexlean
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".git" ]; then
    echo "Initializing git repository on main..."
    git init -b main
fi

chmod +x .githooks/pre-commit
git config core.hooksPath .githooks

# Also copy to .git/hooks as fallback
mkdir -p .git/hooks
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "O3DE LexLean pre-commit hooks installed successfully!"
echo "Git core.hooksPath set to: $(git config --get core.hooksPath)"
