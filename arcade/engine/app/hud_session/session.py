# session.py — orquestación setup, mapeo y bucle HUD

from app.hud_setup import run_hud_setup, run_input_mapping_flows
from app.hud_session.loop import run_hud_main_loop
from config import get_button_labels
from core.extensions_runtime import set_extensions_enabled
from core.input_state_sync import bind_input_state_lock, create_input_state
from profiles import (
	get_active_profile,
	save_profiles_data,
	sync_active_profile_to_legacy_files,
)


def apply_session_profile(
	profile, button_count, input_mode, selected_device_path, labels, wants_keyboard_remap
):
	"""Aplica valores de setup al perfil activo."""
	profile["button_count"] = button_count
	if button_count != 4:
		profile["layout_four_variant_4a"] = False
	profile["input_mode"] = input_mode
	profile["preferred_joystick_path"] = selected_device_path
	profile["button_icons"] = {lbl: profile["button_icons"].get(lbl) for lbl in labels}
	if profile["joystick_bindings"] and any(
		lbl not in profile["joystick_bindings"] for lbl in labels
	):
		profile["joystick_bindings"] = {}
	if input_mode in ["teclado", "hitbox", "mixbox"] and wants_keyboard_remap:
		profile["key_bindings"] = {}


def run_hud_session(screen, profile_data, interactive_setup=True, force_tournament=False):
	set_extensions_enabled(
		profile_data.get("extensions", {}).get("plugin_standby_enabled", True)
	)
	profile = get_active_profile(profile_data)
	setup_result = run_hud_setup(profile, profile_data, interactive_setup, screen)
	if setup_result is None:
		return False
	button_count, input_mode, selected_device_path, wants_keyboard_remap, setup_screen = (
		setup_result
	)
	if setup_screen is not None:
		screen = setup_screen

	labels = get_button_labels(button_count)
	apply_session_profile(
		profile, button_count, input_mode, selected_device_path, labels, wants_keyboard_remap
	)

	ok, screen = run_input_mapping_flows(
		screen, profile, button_count, input_mode, selected_device_path, interactive_setup
	)
	if not ok:
		return False

	sync_active_profile_to_legacy_files(profile_data)
	save_profiles_data(profile_data)
	input_state = create_input_state(len(labels))
	bind_input_state_lock(input_state)
	run_hud_main_loop(
		screen,
		input_state,
		button_count,
		profile_data,
		input_mode,
		selected_device_path,
		profile,
		force_tournament,
	)
	return True


# Aliases privados (compat)
_apply_session_profile = apply_session_profile
