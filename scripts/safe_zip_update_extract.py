#!/usr/bin/env python3
"""Extracción segura de ZIP de release para scripts/update.sh (SEC-001)."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ENGINE)

from utils.safe_zip_extract import SafeZipExtractError, extract_zip_safely

# Límites más amplios que import de perfil; acotados para release OSS.
_MAX_MEMBERS = 5000
_MAX_PATH_LENGTH = 512
_MAX_FILE = 50 * 1024 * 1024
_MAX_TOTAL = 200 * 1024 * 1024


def main() -> int:
	if len(sys.argv) != 3:
		sys.stderr.write("Uso: safe_zip_update_extract.py ZIP DEST_DIR\n")
		return 2
	zip_path, dest_dir = sys.argv[1], sys.argv[2]
	try:
		extract_zip_safely(
			zip_path,
			dest_dir,
			max_members=_MAX_MEMBERS,
			max_path_length=_MAX_PATH_LENGTH,
			max_uncompressed_file=_MAX_FILE,
			max_total_uncompressed=_MAX_TOTAL,
		)
	except SafeZipExtractError as exc:
		sys.stderr.write(f"ZIP rechazado: {exc}\n")
		return 1
	except Exception as exc:
		sys.stderr.write(f"Error extrayendo ZIP: {exc}\n")
		return 1
	return 0


if __name__ == "__main__":
	sys.exit(main())
