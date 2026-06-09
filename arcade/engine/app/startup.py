# startup.py — preflight, reset de datos

import os
import shutil
import subprocess
import sys
import tempfile
import time

from config import (
	USER_DIR,
	PROFILES_DIR,
	RESET_LOG_PATH,
	ASSETS_VERSION_PATH,
	RUNTIME_VERSION_PATH,
	BACKUP_PROFILES_ROOT,
	ensure_contract_dirs,
	get_assets_version,
	get_runtime_version,
	get_data_version,
	write_data_version,
)
from core.assets_resolver import clear_cache as clear_assets_cache
from core.data_migrations import CURRENT_DATA_VERSION, migrate_if_needed


def _repo_root():
	return os.path.dirname(
		os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	)


def append_reset_log(message):
	ensure_contract_dirs()
	timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
	with open(RESET_LOG_PATH, "a", encoding="utf-8") as file:
		file.write(f"{timestamp} | reset | {message}\n")


def do_reset_data():
	try:
		from datetime import datetime

		if os.path.isdir(USER_DIR):
			ts = datetime.now().strftime("%Y%m%d_%H%M%S")
			pre_dir = os.path.join(
				tempfile.gettempdir(), f"joystick_overlay_pre_reset_{ts}"
			)
			os.makedirs(pre_dir, exist_ok=True)
			for fname in (
				"reset.log",
				"profiles_index.json",
				"update.log",
				".data_version",
			):
				fp = os.path.join(USER_DIR, fname)
				if os.path.isfile(fp):
					shutil.copy2(fp, os.path.join(pre_dir, fname))
			shutil.rmtree(USER_DIR)
		ensure_contract_dirs()
		write_data_version(CURRENT_DATA_VERSION)
		append_reset_log("SUCCESS user dir reset")
		print("Reset de datos completado (canon bajo proyecto).")
		print(f"Espejo de perfiles en XDG no borrado: {BACKUP_PROFILES_ROOT}")
		print(
			"Si hubo pre-respaldos de reset, buscar carpetas joystick_overlay_pre_reset_* en el directorio temporal del sistema."
		)
		return
	except Exception as error:
		append_reset_log(f"ERROR {error}")
		print(f"No se pudo resetear datos: {error}")


def run_reset_data_confirmation():
	print(f"Se borrará el directorio de datos del proyecto: {USER_DIR}")
	print("(Pre-respaldado fuera del repo: joystick_overlay_pre_reset_* en el tmp del sistema.)")
	print(f"No se borra el espejo XDG de perfiles: {BACKUP_PROFILES_ROOT}")
	confirm = input("Confirmar reset de datos? (s/n): ").strip().lower()
	if confirm not in ("s", "si"):
		print("Reset cancelado.")
		return
	main_path = os.path.join(_repo_root(), "main.py")
	args = [sys.executable, os.path.abspath(main_path), "--do-reset-data"]
	subprocess.run(args, check=False, cwd=_repo_root())


def preflight_startup():
	ensure_contract_dirs()
	assets_version = get_assets_version()
	if not assets_version:
		print(f"[ERR] assets inválidos: falta {ASSETS_VERSION_PATH}")
		return False
	runtime_version = get_runtime_version()
	if not runtime_version:
		print(f"[ERR] runtime inválido: falta {RUNTIME_VERSION_PATH}")
		return False
	data_version_raw = get_data_version(default_version="0")
	try:
		data_version = int(data_version_raw)
	except Exception:
		data_version = 0
	if data_version < CURRENT_DATA_VERSION:
		result = migrate_if_needed()
		print(f"[INFO] Migración de datos: {result}")
		clear_assets_cache()
	elif data_version > CURRENT_DATA_VERSION:
		print(
			f"[ERR] data_version ({data_version}) mayor que soportado ({CURRENT_DATA_VERSION})."
		)
		return False
	if runtime_version != os.environ.get(
		"JOYSTICK_EXPECTED_RUNTIME_VERSION", runtime_version
	):
		print("[WARN] .joystick_version no coincide con runtime esperado; continuando.")
	if not os.path.isdir(PROFILES_DIR):
		ensure_contract_dirs()
	return True


# Aliases privados (compat main.py)
_append_reset_log = append_reset_log
_do_reset_data = do_reset_data
_run_reset_data_confirmation = run_reset_data_confirmation
_preflight_startup = preflight_startup
