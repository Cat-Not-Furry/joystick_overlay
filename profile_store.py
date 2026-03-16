import json
import os
from config import (
	PROFILES_PATH,
	BINDINGS_PATH,
	JOYSTICK_BINDINGS_PATH,
	SUPPORTED_BUTTON_COUNTS,
	SUPPORTED_CONTROLLER_STYLES,
	SUPPORTED_INPUT_MODES,
	SUPPORTED_CAPTURE_MODES,
	SUPPORTED_MONO_FONT_FAMILIES,
	DEFAULT_MONO_FONT_FAMILY,
	JOYSTICK_COLOR_PRESETS,
	get_button_labels,
	get_bindings_format_key,
	get_default_icon_path,
)


def _read_json_file(path, default):
	if not os.path.exists(path):
		return default

	try:
		with open(path, "r") as file:
			content = file.read().strip()
			if content == "":
				return default
			return json.loads(content)
	except Exception:
		return default


def _write_json_file(path, data):
	with open(path, "w") as file:
		json.dump(data, file, indent=4)


def _backup_if_exists(path):
	if not os.path.exists(path):
		return
	backup_path = f"{path}.bak"
	if os.path.exists(backup_path):
		return
	try:
		with open(path, "r") as source:
			content = source.read()
		with open(backup_path, "w") as backup:
			backup.write(content)
	except Exception:
		pass


def _default_button_icons(button_count):
	return {label: get_default_icon_path(label) for label in get_button_labels(button_count)}


def _default_profile(profile_id, name, button_count=6):
	color_values = list(JOYSTICK_COLOR_PRESETS.values())
	return {
		"id": profile_id,
		"name": name,
		"button_count": button_count,
		"input_mode": "teclado",
		"preferred_joystick_path": None,
		"preferred_keyboard_path": None,
		"tournament_mode": False,
		"controller_style": "default",
		"joystick_bindings_style": None,
		"joystick_color": list(color_values[0]),
		"joystick_knob_color": list(color_values[0]),
		"joystick_bar_color": [0, 0, 0],
		"joystick_ring_color": [255, 255, 255],
		"button_icons": _default_button_icons(button_count),
		"key_bindings": {},
		"joystick_bindings": {},
	}

def _default_window_mode():
	return "floating_hint"

def _default_capture_mode():
	return "normal"

def _default_ui_font_family():
	return DEFAULT_MONO_FONT_FAMILY


def _normalize_profile(profile, fallback_index):
	profile_id = profile.get("id") or f"perfil_{fallback_index}"
	profile_name = profile.get("name") or f"Perfil {fallback_index}"
	button_count = profile.get("button_count", 6)
	if button_count not in SUPPORTED_BUTTON_COUNTS:
		button_count = 6

	input_mode = profile.get("input_mode", "teclado")
	if input_mode not in SUPPORTED_INPUT_MODES:
		input_mode = "teclado"
	controller_style = profile.get("controller_style", "default")
	if controller_style not in SUPPORTED_CONTROLLER_STYLES:
		controller_style = "default"
	joystick_bindings_style = profile.get("joystick_bindings_style")
	if joystick_bindings_style is not None and joystick_bindings_style not in SUPPORTED_CONTROLLER_STYLES:
		joystick_bindings_style = None
	preferred_joystick_path = profile.get("preferred_joystick_path")
	if preferred_joystick_path is not None and not isinstance(preferred_joystick_path, str):
		preferred_joystick_path = None
	preferred_keyboard_path = profile.get("preferred_keyboard_path")
	if preferred_keyboard_path is not None and not isinstance(preferred_keyboard_path, str):
		preferred_keyboard_path = None

	joystick_color = profile.get("joystick_color", [0, 255, 0])
	if not isinstance(joystick_color, list) or len(joystick_color) != 3:
		joystick_color = [0, 255, 0]
	joystick_knob_color = profile.get("joystick_knob_color", joystick_color)
	if not isinstance(joystick_knob_color, list) or len(joystick_knob_color) != 3:
		joystick_knob_color = list(joystick_color)
	joystick_bar_color = profile.get("joystick_bar_color", [0, 0, 0])
	if not isinstance(joystick_bar_color, list) or len(joystick_bar_color) != 3:
		joystick_bar_color = [0, 0, 0]
	joystick_ring_color = profile.get("joystick_ring_color", [255, 255, 255])
	if not isinstance(joystick_ring_color, list) or len(joystick_ring_color) != 3:
		joystick_ring_color = [255, 255, 255]
	tournament_mode = profile.get("tournament_mode", False)
	if not isinstance(tournament_mode, bool):
		tournament_mode = False

	button_icons = profile.get("button_icons", {})
	if not isinstance(button_icons, dict):
		button_icons = {}
	if button_count == 8:
		if "PPP" in button_icons and "TR" not in button_icons:
			button_icons["TR"] = button_icons["PPP"]
		if "KKK" in button_icons and "BR" not in button_icons:
			button_icons["BR"] = button_icons["KKK"]
	for label in get_button_labels(button_count):
		if label not in button_icons:
			button_icons[label] = get_default_icon_path(label)

	key_bindings = profile.get("key_bindings", {})
	if not isinstance(key_bindings, dict):
		key_bindings = {}
	if button_count == 8:
		if "PPP" in key_bindings and "TR" not in key_bindings:
			key_bindings["TR"] = key_bindings["PPP"]
		if "KKK" in key_bindings and "BR" not in key_bindings:
			key_bindings["BR"] = key_bindings["KKK"]

	joystick_bindings = profile.get("joystick_bindings", {})
	if not isinstance(joystick_bindings, dict):
		joystick_bindings = {}
	if button_count == 8:
		if "PPP" in joystick_bindings and "TR" not in joystick_bindings:
			joystick_bindings["TR"] = joystick_bindings["PPP"]
		if "KKK" in joystick_bindings and "BR" not in joystick_bindings:
			joystick_bindings["BR"] = joystick_bindings["KKK"]

	return {
		"id": profile_id,
		"name": profile_name,
		"button_count": button_count,
		"input_mode": input_mode,
		"preferred_joystick_path": preferred_joystick_path,
		"preferred_keyboard_path": preferred_keyboard_path,
		"tournament_mode": tournament_mode,
		"controller_style": controller_style,
		"joystick_bindings_style": joystick_bindings_style,
		"joystick_color": joystick_color,
		"joystick_knob_color": joystick_knob_color,
		"joystick_bar_color": joystick_bar_color,
		"joystick_ring_color": joystick_ring_color,
		"button_icons": button_icons,
		"key_bindings": key_bindings,
		"joystick_bindings": joystick_bindings,
	}


def migrate_legacy_bindings():
	old_keyboard = _read_json_file(BINDINGS_PATH, {})
	old_joystick = _read_json_file(JOYSTICK_BINDINGS_PATH, {})

	profiles = []
	profile_index = 1
	for button_count in [4, 6]:
		format_key = get_bindings_format_key(button_count)
		key_bindings = old_keyboard.get(format_key, {}) if isinstance(old_keyboard, dict) else {}
		joy_bindings = old_joystick.get(format_key, {}) if isinstance(old_joystick, dict) else {}

		if key_bindings or joy_bindings:
			profile = _default_profile(
				profile_id=f"perfil_{profile_index}",
				name=f"Perfil {button_count} botones",
				button_count=button_count,
			)
			profile["key_bindings"] = key_bindings
			profile["joystick_bindings"] = joy_bindings
			if joy_bindings:
				profile["input_mode"] = "joystick"
			profiles.append(profile)
			profile_index += 1

	if len(profiles) == 0:
		profiles.append(_default_profile("perfil_1", "Perfil principal", 6))

	_backup_if_exists(BINDINGS_PATH)
	_backup_if_exists(JOYSTICK_BINDINGS_PATH)

	data = {
		"active_profile": profiles[0]["id"],
		"window_mode": _default_window_mode(),
		"capture_mode": _default_capture_mode(),
		"ui_font_family": _default_ui_font_family(),
		"profiles": profiles,
	}
	_write_json_file(PROFILES_PATH, data)
	return data


def load_profiles_data():
	if not os.path.exists(PROFILES_PATH):
		return migrate_legacy_bindings()

	data = _read_json_file(PROFILES_PATH, {})
	if not isinstance(data, dict):
		return migrate_legacy_bindings()

	raw_profiles = data.get("profiles", [])
	if not isinstance(raw_profiles, list) or len(raw_profiles) == 0:
		return migrate_legacy_bindings()

	profiles = []
	for index, profile in enumerate(raw_profiles, start=1):
		if isinstance(profile, dict):
			profiles.append(_normalize_profile(profile, index))

	if len(profiles) == 0:
		return migrate_legacy_bindings()

	active_profile = data.get("active_profile", profiles[0]["id"])
	if active_profile not in [profile["id"] for profile in profiles]:
		active_profile = profiles[0]["id"]

	window_mode = data.get("window_mode", _default_window_mode())
	if window_mode not in ["floating_hint", "normal"]:
		window_mode = _default_window_mode()
	capture_mode = data.get("capture_mode", _default_capture_mode())
	if capture_mode not in SUPPORTED_CAPTURE_MODES:
		capture_mode = _default_capture_mode()
	ui_font_family = data.get("ui_font_family", _default_ui_font_family())
	if ui_font_family not in SUPPORTED_MONO_FONT_FAMILIES:
		ui_font_family = _default_ui_font_family()

	normalized = {
		"active_profile": active_profile,
		"window_mode": window_mode,
		"capture_mode": capture_mode,
		"ui_font_family": ui_font_family,
		"profiles": profiles,
	}
	save_profiles_data(normalized)
	return normalized


def save_profiles_data(data):
	_write_json_file(PROFILES_PATH, data)


def get_active_profile(data):
	active_id = data["active_profile"]
	for profile in data["profiles"]:
		if profile["id"] == active_id:
			return profile
	return data["profiles"][0]


def set_active_profile(data, profile_id):
	for profile in data["profiles"]:
		if profile["id"] == profile_id:
			data["active_profile"] = profile_id
			return


def create_profile(data, base_profile):
	new_id = f"perfil_{len(data['profiles']) + 1}"
	new_profile = {
		"id": new_id,
		"name": f"Perfil {len(data['profiles']) + 1}",
		"button_count": base_profile["button_count"],
		"input_mode": base_profile["input_mode"],
		"preferred_joystick_path": base_profile.get("preferred_joystick_path"),
		"preferred_keyboard_path": base_profile.get("preferred_keyboard_path"),
		"tournament_mode": base_profile.get("tournament_mode", False),
		"controller_style": base_profile.get("controller_style", "default"),
		"joystick_bindings_style": base_profile.get("joystick_bindings_style"),
		"joystick_color": list(base_profile["joystick_color"]),
		"joystick_knob_color": list(base_profile.get("joystick_knob_color", base_profile["joystick_color"])),
		"joystick_bar_color": list(base_profile.get("joystick_bar_color", [0, 0, 0])),
		"joystick_ring_color": list(base_profile.get("joystick_ring_color", [255, 255, 255])),
		"button_icons": dict(base_profile["button_icons"]),
		"key_bindings": dict(base_profile["key_bindings"]),
		"joystick_bindings": dict(base_profile["joystick_bindings"]),
	}
	data["profiles"].append(new_profile)
	data["active_profile"] = new_id
	return new_profile


def sync_active_profile_to_legacy_files(data):
	profile = get_active_profile(data)
	format_key = get_bindings_format_key(profile["button_count"])

	keyboard_data = _read_json_file(BINDINGS_PATH, {})
	if not isinstance(keyboard_data, dict):
		keyboard_data = {}
	keyboard_data[format_key] = profile["key_bindings"]
	_write_json_file(BINDINGS_PATH, keyboard_data)

	joystick_data = _read_json_file(JOYSTICK_BINDINGS_PATH, {})
	if not isinstance(joystick_data, dict):
		joystick_data = {}
	joystick_data[format_key] = profile["joystick_bindings"]
	_write_json_file(JOYSTICK_BINDINGS_PATH, joystick_data)
