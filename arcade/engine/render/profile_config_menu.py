# profile_config_menu.py — shim de compatibilidad; implementación en app/profile_config/

from app.profile_config import open_profile_config_menu
from app.ui.modals import (
	_run_choice_menu,
	_run_message_modal,
	_run_text_input,
	_run_update_modal,
)

__all__ = [
	"open_profile_config_menu",
	"_run_choice_menu",
	"_run_message_modal",
	"_run_text_input",
	"_run_update_modal",
]
