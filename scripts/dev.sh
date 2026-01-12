#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BACKEND_PORT="${BACKEND_PORT:-8000}"

have() { command -v "$1" >/dev/null 2>&1; }

if ! have python; then
  echo "error: python not found in PATH" >&2
  exit 1
fi
if ! have npm; then
  echo "error: npm not found in PATH" >&2
  exit 1
fi

PYTHON_BIN="python"
if [[ "${NO_VENV:-0}" != "1" && -z "${VIRTUAL_ENV:-}" ]]; then
  if [[ ! -d ".venv" ]]; then
    "$PYTHON_BIN" -m venv .venv
  fi
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
  PYTHON_BIN="python"
fi

cleanup() {
  local code=$?
  if [[ -n "${FRONTEND_PID:-}" ]]; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "${BACKEND_PID:-}" ]]; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
  exit "$code"
}
trap cleanup INT TERM EXIT

echo "[backend] installing deps"
"$PYTHON_BIN" -m pip install -r "bool2cmos/backend/requirements.txt"

echo "[backend] starting on http://localhost:${BACKEND_PORT}"
"$PYTHON_BIN" -m uvicorn "bool2cmos.backend.app:app" --reload --port "${BACKEND_PORT}" &
BACKEND_PID=$!

echo "[frontend] installing deps (if needed)"
if [[ "${FORCE_NPM_INSTALL:-0}" == "1" || ! -d "bool2cmos/frontend/node_modules" ]]; then
  (cd "bool2cmos/frontend" && npm install)
fi

echo "[frontend] starting on http://localhost:3000 (proxy -> http://localhost:${BACKEND_PORT})"
(cd "bool2cmos/frontend" && npm start) &
FRONTEND_PID=$!

wait

