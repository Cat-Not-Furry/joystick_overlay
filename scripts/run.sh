#!/usr/bin/env bash

set -u

SCRIPT_PATH="$(readlink -f "$0")"
BASE_DIR="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"

if [ -L "$0" ]; then
	LINK_REAL="$(readlink -f "$0")"
	if [ -n "$LINK_REAL" ]; then
		SCRIPT_PATH="$LINK_REAL"
		BASE_DIR="$(dirname "$SCRIPT_PATH")"
	fi
fi

cd "$BASE_DIR" || exit 1

if [ ! -x "$BASE_DIR/venv/bin/python3" ]; then
	echo "No se encontro venv listo en $BASE_DIR/venv"
	echo "Ejecuta install.sh primero."
	exit 1
fi

"$BASE_DIR/venv/bin/python3" "$BASE_DIR/cli.py" "$@"
