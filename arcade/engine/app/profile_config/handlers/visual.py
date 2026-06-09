# visual.py — colores, iconos, captura, fuente, layout HUD

import os

from config import (
	BUTTON_COLOR_PRESETS,
	DEFAULT_ICON_PACK,
	JOYSTICK_COLOR_PRESETS,
	PROFILES_DIR,
	SUPPORTED_CAPTURE_MODES,
	SUPPORTED_CONTROLLER_STYLES,
	SUPPORTED_MONO_FONT_FAMILIES,
	get_button_labels,
	get_default_icon_path,
	parse_hex_color,
	rgb_to_hex,
	suggested_icon_pack_for_style,
)
from app.profile_config.handlers.common import handle_choice
from app.profile_config.helpers import (
	available_icon_paths,
	button_color_preset_name,
	color_name_from_values,
)
from app.ui.modals import (
	_run_choice_menu,
	_run_message_modal,
	_run_text_input,
)
from core.assets_resolver import invalidate_profile_cache
from render.hud_layout_editor import run_hud_layout_editor
from utils import set_ui_font_family
from utils.image_file_picker import pick_image_file_with_validation
from utils.safe_paths import path_is_under_root


def handle_capture_mode(menu, active_profile, window_mode):
	pd = menu.profile_data
	idx = (
		SUPPORTED_CAPTURE_MODES.index(pd.get("capture_mode", "normal"))
		if pd.get("capture_mode") in SUPPORTED_CAPTURE_MODES
		else 0
	)
	pd["capture_mode"] = SUPPORTED_CAPTURE_MODES[(idx + 1) % len(SUPPORTED_CAPTURE_MODES)]
	return None


def handle_mono_font(menu, active_profile, window_mode):
	def get(ap, pd):
		return pd.get("ui_font_family", "JetBrainsMono")

	def set_val(ap, pd, v):
		pd["ui_font_family"] = v
		set_ui_font_family(v)

	return handle_choice(
		menu,
		active_profile,
		window_mode,
		"Fuente mono",
		SUPPORTED_MONO_FONT_FAMILIES,
		get,
		set_val,
	)


def handle_controller_style(menu, active_profile, window_mode):
	def get(p, _):
		return p.get("controller_style", "default")

	def set_val(p, _, v):
		old_pack = str(p.get("icon_pack", DEFAULT_ICON_PACK))
		p["controller_style"] = v
		if not p.get("icon_pack_locked", False):
			p["icon_pack"] = suggested_icon_pack_for_style(v)
		new_pack = str(p.get("icon_pack", DEFAULT_ICON_PACK))
		if old_pack != new_pack and isinstance(p.get("button_icons"), dict):
			for lbl, val in list(p["button_icons"].items()):
				if isinstance(val, str) and "icon_packs" in val.replace("\\", "/"):
					p["button_icons"][lbl] = None
		invalidate_profile_cache(p.get("id"))

	return handle_choice(
		menu,
		active_profile,
		window_mode,
		"Estilo de control",
		SUPPORTED_CONTROLLER_STYLES,
		get,
		set_val,
	)


def handle_change_icon(menu, active_profile, window_mode):
	"""Handler único para cambio de icono por botón."""
	labels = get_button_labels(active_profile["button_count"])
	label_choice = _run_choice_menu(
		menu.screen, "Selecciona boton", labels, 0, window_mode=window_mode
	)
	if label_choice is None:
		return None
	label = labels[label_choice]
	icon_opts = available_icon_paths(labels, active_profile["id"])
	cur_icon = active_profile["button_icons"].get(label, get_default_icon_path(label))
	if cur_icon and cur_icon not in icon_opts:
		icon_opts.append(cur_icon)
	try:
		icon_idx = icon_opts.index(cur_icon)
	except ValueError:
		icon_idx = 0
	icon_choice = _run_choice_menu(
		menu.screen, f"Icono para {label}", icon_opts, icon_idx, window_mode=window_mode
	)
	if icon_choice is None:
		return None
	sel = icon_opts[icon_choice]
	if sel == "ninguno":
		active_profile["button_icons"][label] = None
	elif sel == "Seleccionar...":
		prof_root = os.path.join(PROFILES_DIR, str(active_profile["id"]))
		icons_dir = os.path.join(prof_root, "icons")
		os.makedirs(icons_dir, exist_ok=True)
		chosen_file, err = pick_image_file_with_validation(
			initial_dir=icons_dir, max_width=512, max_height=512
		)
		if chosen_file and path_is_under_root(prof_root, chosen_file):
			active_profile["button_icons"][label] = os.path.relpath(chosen_file, prof_root)
		elif err:
			_run_message_modal(
				menu.screen,
				"Icono invalido",
				[err, "Solo se permiten imagenes <= 512x512."],
				window_mode=window_mode,
			)
	else:
		active_profile["button_icons"][label] = sel
	return None


def handle_toggle_icon_pack_lock(menu, active_profile, window_mode):
	active_profile["icon_pack_locked"] = not bool(active_profile.get("icon_pack_locked", False))
	invalidate_profile_cache(active_profile.get("id"))
	return None


def handle_joystick_color(menu, active_profile, window_mode):
	names = list(JOYSTICK_COLOR_PRESETS.keys())
	try:
		idx = names.index(color_name_from_values(active_profile["joystick_color"]))
	except ValueError:
		idx = 0
	chosen = _run_choice_menu(menu.screen, "Color joystick", names, idx, window_mode=window_mode)
	if chosen is not None:
		col = list(JOYSTICK_COLOR_PRESETS[names[chosen]])
		active_profile["joystick_color"] = col
		active_profile["joystick_knob_color"] = list(col)
	return None


def handle_button_color(menu, active_profile, window_mode):
	names = list(BUTTON_COLOR_PRESETS.keys())
	try:
		idx = names.index(
			button_color_preset_name(
				active_profile.get("button_color_inactive", [80, 80, 80]),
				active_profile.get("button_color_active", [255, 0, 0]),
			)
		)
	except ValueError:
		idx = 0
	chosen = _run_choice_menu(menu.screen, "Color de botones", names, idx, window_mode=window_mode)
	if chosen is not None:
		preset = BUTTON_COLOR_PRESETS[names[chosen]]
		active_profile["button_color_inactive"] = list(preset["inactive"])
		active_profile["button_color_active"] = list(preset["active"])
	return None


def handle_joystick_color_hex(menu, active_profile, window_mode):
	knob_hex = rgb_to_hex(
		active_profile.get("joystick_knob_color", active_profile.get("joystick_color", [0, 255, 0]))
	)
	bar_hex = rgb_to_hex(active_profile.get("joystick_bar_color", [0, 0, 0]))
	ring_hex = rgb_to_hex(active_profile.get("joystick_ring_color", [255, 255, 255]))
	knob_t = _run_text_input(menu.screen, "Hex joystick (knob)", knob_hex, window_mode=window_mode)
	if knob_t is None:
		return None
	bar_t = _run_text_input(menu.screen, "Hex barra (stick)", bar_hex, window_mode=window_mode)
	if bar_t is None:
		return None
	ring_t = _run_text_input(menu.screen, "Hex anillo", ring_hex, window_mode=window_mode)
	if ring_t is None:
		return None
	knob_c = parse_hex_color(knob_t)
	bar_c = parse_hex_color(bar_t)
	ring_c = parse_hex_color(ring_t)
	if knob_c and bar_c and ring_c:
		active_profile["joystick_knob_color"] = knob_c
		active_profile["joystick_bar_color"] = bar_c
		active_profile["joystick_ring_color"] = ring_c
		active_profile["joystick_color"] = list(knob_c)
	return None


def handle_edit_hud_layout(menu, active_profile, window_mode):
	run_hud_layout_editor(menu.screen, active_profile, window_mode=window_mode)
	invalidate_profile_cache(active_profile.get("id"))
	return None
