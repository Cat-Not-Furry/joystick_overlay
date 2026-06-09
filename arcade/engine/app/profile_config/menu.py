# menu.py — ProfileConfigMenu y bucle de secciones

import pygame

from app.profile_config.handlers import OPTION_HANDLERS
from app.profile_config.helpers import (
	SECTION_KEYS,
	button_color_preset_name,
	color_name_from_values,
)
from app.ui.modals import _run_choice_menu
from core.assets_resolver import invalidate_profile_cache
from profiles import get_active_profile
from utils import set_ui_font_family


class ProfileConfigMenu:
	TABLE_CELLS = [
		["window_mode", "capture_mode"],
		["ignore_videoresize", "mono_font"],
		["active_profile", "button_count"],
		["controller_style", "default_input"],
		["joystick_color", "button_color"],
		["global_keyboard", "tournament_mode"],
	]
	ACTIONS_ROW = [
		"hitbox_alt_layout",
		"local_backups",
		"mirror_xdg_profiles",
		"change_icon",
		"create_profile",
		"rename_profile",
		"toggle_icon_pack_lock",
		"joystick_color_hex",
		"edit_hud_layout",
		"export_profile",
		"import_profile",
		"update_overlay",
		"save_and_back",
		"cancel",
	]

	@property
	def OPTION_KEYS(self):
		flat = []
		for row in self.TABLE_CELLS:
			flat.extend(row)
		flat.extend(self.ACTIONS_ROW)
		return flat

	def __init__(self, screen, profile_data):
		self.screen = screen
		self.profile_data = profile_data
		self.selected = 0
		self.snapshot = self._make_snapshot()

	def _make_snapshot(self):
		return {
			"active_profile": self.profile_data["active_profile"],
			"window_mode": self.profile_data.get("window_mode", "floating_hint"),
			"ignore_videoresize": self.profile_data.get("ignore_videoresize", False),
			"capture_mode": self.profile_data.get("capture_mode", "normal"),
			"ui_font_family": self.profile_data.get("ui_font_family", "JetBrainsMono"),
			"backups_enabled": bool(self.profile_data.get("backups_enabled", True)),
			"xdg_mirror_enabled": bool(self.profile_data.get("xdg_mirror_enabled", True)),
			"backup_prompt_completed": bool(
				self.profile_data.get("backup_prompt_completed", True)
			),
			"profiles": [
				{
					**p,
					"joystick_color": list(p["joystick_color"]),
					"button_icons": dict(p["button_icons"]),
					"key_bindings": dict(p.get("key_bindings") or {}),
					"joystick_bindings": dict(p.get("joystick_bindings") or {}),
					"button_color_inactive": list(p.get("button_color_inactive", [80, 80, 80])),
					"button_color_active": list(p.get("button_color_active", [255, 0, 0])),
				}
				for p in self.profile_data["profiles"]
			],
		}

	def _get_option_labels(self, active_profile, window_mode, ui_font_family, keyboard_label):
		tournament_text = "On" if active_profile.get("tournament_mode", False) else "Off"
		alt_text = "On" if active_profile.get("hitbox_alt_layout", False) else "Off"
		btn_inactive = active_profile.get("button_color_inactive", [80, 80, 80])
		btn_active = active_profile.get("button_color_active", [255, 0, 0])
		btn_color_name = button_color_preset_name(btn_inactive, btn_active)
		return {
			"tournament_mode": f"Torneo | {tournament_text}",
			"hitbox_alt_layout": f"Pos. Hitbox | {alt_text}",
			"local_backups": (
				f"Backups locales | {'Si' if self.profile_data.get('backups_enabled', True) else 'No'}"
			),
			"mirror_xdg_profiles": (
				f"Espejo datos sistema | {'Si' if self.profile_data.get('xdg_mirror_enabled', True) else 'No'}"
			),
			"window_mode": f"Ventana | {'Flotante' if window_mode == 'floating_hint' else 'Normal'}",
			"ignore_videoresize": f"Videoresize | {'ignorado' if self.profile_data.get('ignore_videoresize', False) else 'activo'}",
			"capture_mode": f"Captura | {'OBS' if self.profile_data.get('capture_mode') == 'obs_green' else 'Normal'}",
			"mono_font": f"Fuente | {ui_font_family}",
			"controller_style": f"Control | {active_profile.get('controller_style', 'default')}",
			"active_profile": f"Perfil | {active_profile['name']}",
			"button_count": (
				f"Botones | {active_profile['button_count']}"
				+ (
					" (4A)"
					if active_profile.get("button_count") == 4
					and bool(active_profile.get("layout_four_variant_4a", False))
					else ""
				)
			),
			"default_input": f"Entrada | {active_profile['input_mode']}",
			"global_keyboard": f"Teclado | {'ninguno' if not active_profile.get('preferred_keyboard_path') else 'dispositivo'}",
			"joystick_color": f"Color stick | {color_name_from_values(active_profile['joystick_color'])}",
			"joystick_color_hex": "Color joystick hexa",
			"button_color": f"Color botones | {btn_color_name}",
			"change_icon": "Cambiar icono",
			"create_profile": "Crear perfil",
			"rename_profile": "Renombrar perfil",
			"toggle_icon_pack_lock": (
				f"Pack iconos fijo | {'Si' if active_profile.get('icon_pack_locked') else 'No'}"
			),
			"edit_hud_layout": "Editar posicion HUD",
			"export_profile": "Exportar perfil",
			"import_profile": "Importar perfil",
			"update_overlay": "Actualizar overlay",
			"extensions_info": "Extensiones (informacion)",
			"save_and_back": "Guardar y volver",
			"cancel": "Cancelar",
		}

	def _handle_option(self, key, active_profile, window_mode):
		handler = OPTION_HANDLERS.get(key)
		if handler is None:
			return None
		return handler(self, active_profile, window_mode)

	def run(self):
		clock = pygame.time.Clock()
		section_titles = list(SECTION_KEYS.keys()) + ["Guardar y volver"]
		while True:
			sec_idx = _run_choice_menu(
				self.screen,
				"Preferencias (secciones)",
				section_titles,
				0,
				window_mode=self.profile_data.get("window_mode", "floating_hint"),
			)
			if sec_idx is None:
				return None
			if sec_idx == len(SECTION_KEYS):
				return self.profile_data
			section_name = list(SECTION_KEYS.keys())[sec_idx]
			keys = SECTION_KEYS[section_name]
			while True:
				set_ui_font_family(self.profile_data.get("ui_font_family", "JetBrainsMono"))
				active_profile = get_active_profile(self.profile_data)
				window_mode = self.profile_data.get("window_mode", "floating_hint")
				ui_font_family = self.profile_data.get("ui_font_family", "JetBrainsMono")
				keyboard_path = active_profile.get("preferred_keyboard_path")
				keyboard_label = "ninguno (foco)" if not keyboard_path else keyboard_path
				option_labels = self._get_option_labels(
					active_profile, window_mode, ui_font_family, keyboard_label
				)
				sub_labels = [option_labels[k] for k in keys] + ["Volver"]
				if section_name == "Dispositivos":

					def _refresh_dispositivos_options():
						ap = get_active_profile(self.profile_data)
						kp = ap.get("preferred_keyboard_path")
						kbl = "ninguno (foco)" if not kp else kp
						wm = self.profile_data.get("window_mode", "floating_hint")
						ff = self.profile_data.get("ui_font_family", "JetBrainsMono")
						ol = self._get_option_labels(ap, wm, ff, kbl)
						return [ol[k] for k in keys] + ["Volver"]

					def _on_tab_dispositivos(sel):
						if sel < 0 or sel >= len(keys):
							return
						if keys[sel] != "button_count":
							return
						ap = get_active_profile(self.profile_data)
						if ap.get("button_count") != 4:
							return
						ap["layout_four_variant_4a"] = not bool(ap.get("layout_four_variant_4a", False))
						invalidate_profile_cache(ap.get("id"))

					footer_dispositivos = "Flechas + Enter | Esc | Tab en Botones (solo 4): alternar 4A"
					sub_idx = _run_choice_menu(
						self.screen,
						f"Seccion: {section_name}",
						sub_labels,
						0,
						window_mode=window_mode,
						refresh_options=_refresh_dispositivos_options,
						on_tab=_on_tab_dispositivos,
						footer_extra=footer_dispositivos,
					)
				else:
					sub_idx = _run_choice_menu(
						self.screen,
						f"Seccion: {section_name}",
						sub_labels,
						0,
						window_mode=window_mode,
					)
				if sub_idx is None:
					return None
				if sub_idx == len(keys):
					break
				key = keys[sub_idx]
				result = self._handle_option(key, active_profile, window_mode)
				if result == "save":
					return self.profile_data
				if result == "cancel":
					return None
			clock.tick(60)


def open_profile_config_menu(screen, profile_data):
	menu = ProfileConfigMenu(screen, profile_data)
	return menu.run()
