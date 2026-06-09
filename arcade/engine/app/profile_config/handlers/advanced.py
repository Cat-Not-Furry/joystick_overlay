# advanced.py — actualizar overlay, cancelar, extensiones

import os
import subprocess
import sys

from app.profile_config.helpers import repo_root
from app.ui.modals import _run_message_modal, _run_update_modal
from utils import set_ui_font_family


def handle_cancel(menu, active_profile, window_mode):
	pd = menu.profile_data
	snap = menu.snapshot
	pd["active_profile"] = snap["active_profile"]
	pd["window_mode"] = snap["window_mode"]
	pd["ignore_videoresize"] = snap["ignore_videoresize"]
	pd["capture_mode"] = snap["capture_mode"]
	pd["ui_font_family"] = snap["ui_font_family"]
	pd["backups_enabled"] = snap.get("backups_enabled", True)
	pd["xdg_mirror_enabled"] = snap.get("xdg_mirror_enabled", True)
	pd["backup_prompt_completed"] = snap.get("backup_prompt_completed", True)
	pd["profiles"] = snap["profiles"]
	set_ui_font_family(pd["ui_font_family"])
	return "cancel"


def handle_update_overlay(menu, active_profile, window_mode):
	root = repo_root()
	update_script = str(root / "scripts" / "update.sh")
	if not os.path.exists(update_script):
		_run_message_modal(
			menu.screen,
			"Actualizar overlay",
			["No se encontro scripts/update.sh en el repositorio."],
			window_mode=window_mode,
		)
		return None
	result = _run_update_modal(menu.screen, update_script, window_mode=window_mode)
	if result == "open_hud":
		main_path = str(root / "main.py")
		try:
			subprocess.Popen(
				[sys.executable, main_path],
				cwd=str(root),
				start_new_session=True,
			)
		except Exception as error:
			_run_message_modal(
				menu.screen,
				"Abrir HUD",
				[f"No se pudo abrir HUD: {error}"],
				window_mode=window_mode,
			)
	return None
