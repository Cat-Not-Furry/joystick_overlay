# handlers — registro central de opciones del menú de perfiles

from app.profile_config.handlers.advanced import (
	handle_cancel,
	handle_update_overlay,
)
from app.profile_config.handlers.common import (
	handle_toggle_pd,
	handle_toggle_profile,
)
from app.profile_config.handlers.devices import (
	handle_active_profile,
	handle_button_count,
	handle_default_input,
	handle_global_keyboard,
)
from app.profile_config.handlers.general import (
	handle_extensions_info,
	handle_toggle_local_backups,
	handle_toggle_mirror_xdg,
	handle_window_mode,
)
from app.profile_config.handlers.profiles_io import (
	handle_create_profile,
	handle_export_profile,
	handle_import_profile,
	handle_rename_profile,
)
from app.profile_config.handlers.visual import (
	handle_button_color,
	handle_capture_mode,
	handle_change_icon,
	handle_controller_style,
	handle_edit_hud_layout,
	handle_joystick_color,
	handle_joystick_color_hex,
	handle_mono_font,
	handle_toggle_icon_pack_lock,
)

OPTION_HANDLERS = {
	"tournament_mode": lambda m, p, w: handle_toggle_profile(m, p, w, "tournament_mode"),
	"hitbox_alt_layout": lambda m, p, w: handle_toggle_profile(m, p, w, "hitbox_alt_layout"),
	"local_backups": handle_toggle_local_backups,
	"mirror_xdg_profiles": handle_toggle_mirror_xdg,
	"window_mode": handle_window_mode,
	"ignore_videoresize": lambda m, p, w: handle_toggle_pd(m, p, w, "ignore_videoresize"),
	"capture_mode": handle_capture_mode,
	"mono_font": handle_mono_font,
	"controller_style": handle_controller_style,
	"active_profile": handle_active_profile,
	"button_count": handle_button_count,
	"default_input": handle_default_input,
	"global_keyboard": handle_global_keyboard,
	"joystick_color": handle_joystick_color,
	"button_color": handle_button_color,
	"joystick_color_hex": handle_joystick_color_hex,
	"change_icon": handle_change_icon,
	"create_profile": handle_create_profile,
	"rename_profile": handle_rename_profile,
	"toggle_icon_pack_lock": handle_toggle_icon_pack_lock,
	"edit_hud_layout": handle_edit_hud_layout,
	"export_profile": handle_export_profile,
	"import_profile": handle_import_profile,
	"update_overlay": handle_update_overlay,
	"extensions_info": handle_extensions_info,
	"save_and_back": lambda m, p, w: "save",
	"cancel": handle_cancel,
}
