#!/usr/bin/env bash
# Render + finish one or more specs:  ./art.sh rsl_gracenote [rsl_refrain ...]   (SAMPLES=96 by default)
set -euo pipefail
cd "$(dirname "$0")"
BLENDER="${BLENDER:-/c/Program Files/Blender Foundation/Blender 4.2/blender.exe}"
for id in "$@"; do
  "$BLENDER" -b --factory-startup -P blender/render.py -- "specs/$id.json" "renders/$id" --samples "${SAMPLES:-96}" \
    2>&1 | grep -E "RSL_RENDER_OK|Error:|Traceback|File \"|Exception" | grep -v "Not freed memory" || true
  python finish.py "specs/$id.json"
done
