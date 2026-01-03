#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/workspaces/vector-guardrails"
cd "$PROJECT_DIR"

# --- Install uv (if not present) ---
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Make sure the current shell sees uv (install puts it under ~/.local/bin)
export PATH="$HOME/.local/bin:$PATH"

# --- Create venv (idempotent) ---
if [ ! -d ".venv" ]; then
  uv venv
fi

# --- If pyproject exists, sync deps (safe to run repeatedly) ---
if [ -f "pyproject.toml" ]; then
  uv sync
fi

# --- If this is a package repo, do editable install for imports ---
if [ -f "pyproject.toml" ]; then
  uv pip install -e . --reinstall
fi

# --- Optional: register a Jupyter kernel (only if ipykernel is installed) ---
if python -c "import ipykernel" >/dev/null 2>&1; then
  python -m ipykernel install --user --name="vector-guardrails" --display-name="Python (vector-guardrails)"
fi

echo "postCreate complete ✅  (uv ready; venv created; deps synced if pyproject exists)"
