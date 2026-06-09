# general.py — ventana, videoresize, backups, espejo XDG

from app.ui.modals import _run_message_modal
from profiles import save_profiles_data


def handle_window_mode(menu, active_profile, window_mode):
	pd = menu.profile_data
	pd["window_mode"] = "normal" if pd.get("window_mode") == "floating_hint" else "floating_hint"
	return None


def handle_toggle_local_backups(menu, active_profile, window_mode):
	pd = menu.profile_data
	pd["backups_enabled"] = not bool(pd.get("backups_enabled", True))
	save_profiles_data(pd)
	return None


def handle_toggle_mirror_xdg(menu, active_profile, window_mode):
	pd = menu.profile_data
	pd["xdg_mirror_enabled"] = not bool(pd.get("xdg_mirror_enabled", True))
	save_profiles_data(pd)
	return None


def handle_extensions_info(menu, active_profile, window_mode):
	_run_message_modal(
		menu.screen,
		"Extensiones",
		[
			"Hooks en core/extensions_runtime.py.",
			"Opcion B: semantic_binding en perfil para plugins.",
		],
		window_mode=window_mode,
	)
	return None


# Re-export para compat con imports de toggle pd
__all__ = [
	"handle_window_mode",
	"handle_toggle_local_backups",
	"handle_toggle_mirror_xdg",
	"handle_extensions_info",
]
