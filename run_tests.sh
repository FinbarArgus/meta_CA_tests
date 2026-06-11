#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_PROJECTS="$(cd "${SCRIPT_DIR}/.." && pwd)"

export CIRCULATORY_AUTOGEN_DIR="${CIRCULATORY_AUTOGEN_DIR:-${GIT_PROJECTS}/circulatory_autogen}"

if [[ -n "${PYTHON:-}" ]]; then
  PY="${PYTHON}"
elif [[ -x "${CIRCULATORY_AUTOGEN_DIR}/venv/bin/python" ]]; then
  PY="${CIRCULATORY_AUTOGEN_DIR}/venv/bin/python"
else
  PY="$(command -v python3)"
fi

# Export the chosen interpreter so subprocess-spawned child suites use the same
# one (sys.executable is empty under the OpenCOR Python shell).
export PYTHON="${PY}"

cd "${SCRIPT_DIR}"
"${PY}" -m pytest tests/ -v "$@"
