# devices.py — perfil activo, botones, entrada, teclado, torneo

from config import SUPPORTED_BUTTON_COUNTS, SUPPORTED_INPUT_MODES, get_button_labels
from app.profile_config.handlers.common import handle_choice
from app.profile_config.helpers import keyboard_device_options
from app.ui.modals import _run_choice_menu
from core.assets_resolver import invalidate_profile_cache
from profiles import set_active_profile


def handle_active_profile(menu, active_profile, window_mode):
	pd = menu.profile_data
	names = [p["name"] for p in pd["profiles"]]
	idx = next(
		(i for i, p in enumerate(pd["profiles"]) if p["id"] == pd["active_profile"]),
		0,
	)
	chosen = _run_choice_menu(menu.screen, "Selecciona perfil", names, idx, window_mode=window_mode)
	if chosen is not None:
		set_active_profile(pd, pd["profiles"][chosen]["id"])
	return None


def handle_button_count(menu, active_profile, window_mode):
	idx = SUPPORTED_BUTTON_COUNTS.index(active_profile["button_count"])
	nc = SUPPORTED_BUTTON_COUNTS[(idx + 1) % len(SUPPORTED_BUTTON_COUNTS)]
	active_profile["button_count"] = nc
	if nc != 4:
		active_profile["layout_four_variant_4a"] = False
	active_profile["button_icons"] = {
		lbl: active_profile.get("button_icons", {}).get(lbl) for lbl in get_button_labels(nc)
	}
	invalidate_profile_cache(active_profile.get("id"))
	return None


def handle_default_input(menu, active_profile, window_mode):
	def get(p, _):
		return p["input_mode"]

	def set_val(p, _, v):
		p["input_mode"] = v

	return handle_choice(
		menu,
		active_profile,
		window_mode,
		"Entrada por defecto",
		SUPPORTED_INPUT_MODES,
		get,
		set_val,
	)


def handle_global_keyboard(menu, active_profile, window_mode):
	kb_opts = keyboard_device_options()
	labels = [x[0] for x in kb_opts]
	paths = [x[1] for x in kb_opts]
	cur = active_profile.get("preferred_keyboard_path")
	idx = next((i for i, p in enumerate(paths) if p == cur), 0)
	chosen = _run_choice_menu(menu.screen, "Teclado global", labels, idx, window_mode=window_mode)
	if chosen is not None:
		active_profile["preferred_keyboard_path"] = paths[chosen]
	return None
