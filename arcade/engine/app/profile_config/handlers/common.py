# common.py — helpers compartidos entre handlers

from app.ui.modals import _run_choice_menu


def handle_toggle_profile(menu, active_profile, window_mode, key):
	active_profile[key] = not active_profile.get(key, False)
	return None


def handle_toggle_pd(menu, active_profile, window_mode, key):
	menu.profile_data[key] = not menu.profile_data.get(key, False)
	return None


def handle_choice(menu, active_profile, window_mode, title, options, get_current, set_value):
	cur = get_current(active_profile, menu.profile_data)
	idx = options.index(cur) if cur in options else 0
	chosen = _run_choice_menu(menu.screen, title, options, idx, window_mode=window_mode)
	if chosen is not None:
		set_value(active_profile, menu.profile_data, options[chosen])
	return None
