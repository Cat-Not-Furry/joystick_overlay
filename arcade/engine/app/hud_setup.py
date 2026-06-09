# hud_setup.py — setup interactivo y flujos de mapeo antes del bucle HUD

from app.constants import MAPPER_WINDOW_SIZE, SELECTOR_WINDOW_SIZE
from app.secondary_flows import (
	choose_keyboard_device_secondary,
	confirm_keyboard_remap_secondary,
	run_secondary_selector,
)
from config import get_button_labels, get_active_bindings_format_key
from maps import map_keys, map_joystick_buttons, run_joystick_diagnostic
from render import choose_button_format, choose_input_mode


def run_hud_setup_interactive(profile, profile_data, screen):
	button_count, screen = run_secondary_selector(
		screen,
		"Formato de botones",
		SELECTOR_WINDOW_SIZE,
		lambda s: choose_button_format(s, profile["button_count"]),
	)
	if button_count is None:
		return None
	input_mode = None
	selected_device_path = profile.get("preferred_joystick_path")
	wants_keyboard_remap = False
	while input_mode is None:
		mode_choice, screen = run_secondary_selector(
			screen,
			"Modo de entrada",
			SELECTOR_WINDOW_SIZE,
			lambda s: choose_input_mode(s, profile["input_mode"]),
		)
		if mode_choice is None:
			return None
		if mode_choice in ["teclado", "hitbox", "mixbox"]:
			keyboard_action, screen = confirm_keyboard_remap_secondary(screen)
			if keyboard_action == "cancelar":
				continue
			select_status, screen = choose_keyboard_device_secondary(
				screen, profile.get("preferred_keyboard_path")
			)
			if select_status[0] == "cancelar":
				continue
			profile["preferred_keyboard_path"] = select_status[1]
			wants_keyboard_remap = keyboard_action == "si"
			input_mode = mode_choice
			break
		diagnostic, screen = run_secondary_selector(
			screen,
			"Diagnostico joystick",
			MAPPER_WINDOW_SIZE,
			lambda s: run_joystick_diagnostic(
				s,
				button_count,
				window_mode=profile_data.get("window_mode", "floating_hint"),
				controller_style=profile.get("controller_style", "default"),
			),
		)
		if diagnostic.get("status") == "back_to_input":
			continue
		selected_device_path = diagnostic.get("device_path")
		if diagnostic.get("status") == "mapped":
			profile["joystick_bindings"] = diagnostic.get("bindings", {})
			profile["joystick_bindings_style"] = profile.get(
				"controller_style", "default"
			)
		input_mode = "joystick"
	return (
		button_count,
		input_mode,
		selected_device_path,
		wants_keyboard_remap,
		screen,
	)


def run_hud_setup_non_interactive(profile):
	return (
		profile.get("button_count", 6),
		profile.get("input_mode", "teclado"),
		profile.get("preferred_joystick_path"),
		False,
		None,
	)


def keyboard_bindings_incomplete(profile, button_count):
	kb = profile.get("key_bindings") or {}
	need = (
		["Arriba", "Abajo", "Izquierda", "Derecha"]
		+ get_button_labels(button_count)
		+ ["SELECT", "START"]
	)
	return any(k not in kb for k in need)


def joystick_bindings_need_mapping(profile, button_count):
	jb = profile.get("joystick_bindings") or {}
	for lbl in get_button_labels(button_count) + ["SELECT", "START"]:
		if jb.get(lbl) is not None:
			return False
	return True


def run_keyboard_mapping_flow(screen, profile, button_count, interactive_setup):
	if keyboard_bindings_incomplete(profile, button_count):
		profile["key_bindings"] = {}
	if not profile["key_bindings"]:
		if not interactive_setup:
			print("[WARN] Perfil sin key_bindings en modo no interactivo.")
			return False, screen
		fmt = get_active_bindings_format_key(profile)
		im = profile.get("input_mode", "teclado")
		pid = profile["id"]
		mapped, new_screen = run_secondary_selector(
			screen,
			"Mapeo teclado",
			MAPPER_WINDOW_SIZE,
			lambda s: map_keys(s, button_count, pid, fmt, im),
		)
		if mapped:
			profile["key_bindings"] = mapped
		screen = new_screen
	return True, screen


def run_joystick_mapping_flow(screen, profile, button_count, selected_device_path):
	if profile.get("joystick_bindings_style") != profile.get(
		"controller_style", "default"
	):
		profile["joystick_bindings"] = {}
	if joystick_bindings_need_mapping(profile, button_count):
		mapped, new_screen = run_secondary_selector(
			screen,
			"Mapeo joystick",
			MAPPER_WINDOW_SIZE,
			lambda s: map_joystick_buttons(
				s,
				button_count,
				show_error=False,
				device_path=selected_device_path,
				controller_style=profile.get("controller_style", "default"),
				profile_id=profile["id"],
				format_key=get_active_bindings_format_key(profile),
			),
		)
		if not mapped:
			return False, screen
		profile["joystick_bindings"] = mapped
		profile["joystick_bindings_style"] = profile.get("controller_style", "default")
		screen = new_screen
	return True, screen


def run_hud_setup(profile, profile_data, interactive_setup, screen):
	if interactive_setup:
		result = run_hud_setup_interactive(profile, profile_data, screen)
		if result is None:
			return None
		bc, im, sdp, wkr, setup_screen = result
		return bc, im, sdp, wkr, setup_screen
	bc, im, sdp, wkr, _ = run_hud_setup_non_interactive(profile)
	return bc, im, sdp, wkr, None


def run_input_mapping_flows(
	screen, profile, button_count, input_mode, selected_device_path, interactive_setup
):
	if input_mode in ["teclado", "hitbox", "mixbox"]:
		ok, screen = run_keyboard_mapping_flow(
			screen, profile, button_count, interactive_setup
		)
		if not ok:
			return False, screen
	if input_mode == "joystick":
		ok, screen = run_joystick_mapping_flow(
			screen, profile, button_count, selected_device_path
		)
		if not ok:
			return False, screen
	return True, screen


# Aliases privados (compat main.py)
_run_hud_setup_interactive = run_hud_setup_interactive
_run_hud_setup_non_interactive = run_hud_setup_non_interactive
_keyboard_bindings_incomplete = keyboard_bindings_incomplete
_joystick_bindings_need_mapping = joystick_bindings_need_mapping
_run_keyboard_mapping_flow = run_keyboard_mapping_flow
_run_joystick_mapping_flow = run_joystick_mapping_flow
_run_hud_setup = run_hud_setup
_run_input_mapping_flows = run_input_mapping_flows
