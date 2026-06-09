# helpers.py — utilidades compartidas del menú de configuración de perfiles

import os
from pathlib import Path

from config import (
	BUTTON_COLOR_PRESETS,
	JOYSTICK_COLOR_PRESETS,
	PROFILES_DIR,
	get_default_icon_path,
)
from utils import list_keyboard_devices_by_capabilities

SECTION_KEYS = {
	"General": ["window_mode", "ignore_videoresize", "local_backups", "mirror_xdg_profiles"],
	"Dispositivos": [
		"active_profile",
		"button_count",
		"default_input",
		"global_keyboard",
		"tournament_mode",
		"hitbox_alt_layout",
	],
	"Visualizacion": [
		"capture_mode",
		"mono_font",
		"controller_style",
		"change_icon",
		"toggle_icon_pack_lock",
		"joystick_color",
		"button_color",
		"joystick_color_hex",
		"edit_hud_layout",
	],
	"Perfiles": ["create_profile", "rename_profile", "export_profile", "import_profile"],
	"Extensiones": ["extensions_info"],
	"Avanzado": ["update_overlay"],
}


def repo_root():
	"""Raíz del repositorio (app/profile_config -> engine -> arcade -> root)."""
	return Path(__file__).resolve().parent.parent.parent.parent.parent


def color_name_from_values(values):
	for name, preset_values in JOYSTICK_COLOR_PRESETS.items():
		if list(preset_values) == list(values):
			return name
	return "personalizado"


def button_color_preset_name(inactive, active):
	for name, preset in BUTTON_COLOR_PRESETS.items():
		if (
			list(preset["inactive"]) == list(inactive)
			and list(preset["active"]) == list(active)
		):
			return name
	return "personalizado"


def available_icon_paths(labels, profile_id):
	options = []
	icons_dir = os.path.join(PROFILES_DIR, str(profile_id), "icons")
	if os.path.isdir(icons_dir):
		for filename in sorted(os.listdir(icons_dir)):
			if filename.lower().endswith(".png"):
				options.append(os.path.join("icons", filename))
	for label in labels:
		default_path = get_default_icon_path(label)
		if default_path not in options:
			options.append(default_path)
	if "ninguno" not in options:
		options.insert(0, "ninguno")
	if "Seleccionar..." not in options:
		options.insert(1, "Seleccionar...")
	return options


def keyboard_device_options():
	options = [("ninguno (solo con foco)", None)]
	devices = list_keyboard_devices_by_capabilities()
	for device in devices:
		options.append((f"{device.name} | {device.path}", device.path))
	for device in devices:
		device.close()
	return options
