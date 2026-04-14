import os
import pygame
from config import (
	JOYSTICK_COLOR_PRESETS,
	BUTTON_COLOR_PRESETS,
	SUPPORTED_BUTTON_COUNTS,
	SUPPORTED_CONTROLLER_STYLES,
	SUPPORTED_CAPTURE_MODES,
	SUPPORTED_INPUT_MODES,
	SUPPORTED_MONO_FONT_FAMILIES,
	parse_hex_color,
	rgb_to_hex,
	get_button_labels,
	get_default_icon_path
)
from utils import (
	draw_centered_text,
	draw_text_left,
	build_responsive_font,
	fit_text_to_width,
	run_modal_child_window,
	list_keyboard_devices_by_capabilities,
	set_ui_font_family,
)
from profiles import get_active_profile, set_active_profile, create_profile
from profiles.profile_export import export_profile_to_zip, import_profile_from_zip
from render.hud_layout_editor import run_hud_layout_editor
from utils import pick_image_file_with_validation
from utils.file_picker import pick_directory, pick_zip_file


def _color_name_from_values(values):
	for name, preset_values in JOYSTICK_COLOR_PRESETS.items():
		if list(preset_values) == list(values):
			return name
	return "personalizado"


def _button_color_preset_name(inactive, active):
	for name, preset in BUTTON_COLOR_PRESETS.items():
		if (list(preset["inactive"]) == list(inactive) and
				list(preset["active"]) == list(active)):
			return name
	return "personalizado"


def _available_icon_paths(labels):
	options = []
	icons_dir = "icons"
	if os.path.isdir(icons_dir):
		for filename in sorted(os.listdir(icons_dir)):
			if filename.lower().endswith(".png"):
				options.append(os.path.join("icons", filename))
	for label in labels:
		default_path = get_default_icon_path(label)
		if default_path not in options:
			options.append(default_path)
	if "ninguno" not in options:
		options.insert(0, "ninguno")
	if "Seleccionar..." not in options:
		options.insert(1, "Seleccionar...")
	return options

def _keyboard_device_options():
	options = [("ninguno (solo con foco)", None)]
	devices = list_keyboard_devices_by_capabilities()
	for device in devices:
		options.append((f"{device.name} | {device.path}", device.path))
	for device in devices:
		device.close()
	return options

def _run_text_input(screen, title, initial_value="", window_mode="floating_hint"):
	def _runner(secondary):
		typed = str(initial_value)
		clock = pygame.time.Clock()

		while True:
			lines = [title, typed or "...", "Enter confirmar | Backspace | Esc cancelar"]
			font, line_gap = build_responsive_font(
				secondary,
				lines,
				base_size=26,
				min_size=14,
				max_size=34,
				base_resolution=(560, 300),
			)
			secondary.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(secondary, font, title, y=title_y)
			draw_centered_text(secondary, font, typed or "...", y=title_y + line_gap)
			draw_centered_text(secondary, font, "Enter confirmar | Backspace | Esc cancelar", y=secondary.get_height() - max(22, line_gap))
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						return None
					if event.key == pygame.K_BACKSPACE:
						typed = typed[:-1]
					elif event.key == pygame.K_RETURN:
						return typed
					elif event.unicode and event.unicode.isprintable():
						typed += event.unicode
			clock.tick(60)

	return run_modal_child_window(
		title=title,
		size=(560, 300),
		window_mode=window_mode,
		runner=_runner,
		screen=screen,
	)


def _run_choice_menu(screen, title, options, initial_index=0, window_mode="floating_hint"):
	def _runner(secondary):
		selected = max(0, min(initial_index, len(options) - 1))
		clock = pygame.time.Clock()

		while True:
			lines_for_fit = [title] + [str(option) for option in options[:8]] + ["Flechas + Enter | Esc"]
			font, line_gap = build_responsive_font(
				secondary,
				lines_for_fit,
				base_size=26,
				min_size=14,
				max_size=34,
				base_resolution=(540, 320),
				max_height_ratio=0.84,
			)
			secondary.fill((0, 0, 0))
			draw_centered_text(secondary, font, title, y=max(28, line_gap))
			start_y = max(28, line_gap) + line_gap
			for index, option in enumerate(options):
				prefix = ">" if index == selected else " "
				draw_centered_text(secondary, font, f"{prefix} {option}", y=start_y + index * line_gap)
			draw_centered_text(secondary, font, "Flechas + Enter | Esc", y=secondary.get_height() - max(20, line_gap))
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_UP, pygame.K_LEFT):
						selected = (selected - 1) % len(options)
					elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
						selected = (selected + 1) % len(options)
					elif event.key == pygame.K_RETURN:
						return selected
					elif event.key == pygame.K_ESCAPE:
						return None
			clock.tick(60)

	return run_modal_child_window(
		title=title,
		size=(540, 320),
		window_mode=window_mode,
		runner=_runner,
		screen=screen,
	)


def _run_message_modal(screen, title, message_lines, window_mode="floating_hint"):
	lines = [title] + list(message_lines) + ["Enter/Esc para continuar"]

	def _runner(secondary):
		clock = pygame.time.Clock()
		while True:
			font, line_gap = build_responsive_font(
				secondary,
				lines,
				base_size=24,
				min_size=14,
				max_size=34,
				base_resolution=(560, 280),
			)
			secondary.fill((0, 0, 0))
			start_y = max(24, (secondary.get_height() - line_gap * len(lines)) // 2)
			for index, line in enumerate(lines):
				trimmed = fit_text_to_width(font, line, int(secondary.get_width() * 0.92))
				draw_centered_text(secondary, font, trimmed, y=start_y + index * line_gap)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
					return None
			clock.tick(60)

	return run_modal_child_window(
		title=title,
		size=(560, 280),
		window_mode=window_mode,
		runner=_runner,
		screen=screen,
	)


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
		"change_icon",
		"create_profile",
		"joystick_color_hex",
		"edit_hud_layout",
		"export_profile",
		"import_profile",
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
			"profiles": [
				{
					**p,
					"joystick_color": list(p["joystick_color"]),
					"button_icons": dict(p["button_icons"]),
					"key_bindings": dict(p["key_bindings"]),
					"joystick_bindings": dict(p["joystick_bindings"]),
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
		btn_color_name = _button_color_preset_name(btn_inactive, btn_active)
		return {
			"tournament_mode": f"Torneo | {tournament_text}",
			"hitbox_alt_layout": f"Pos. Hitbox | {alt_text}",
			"window_mode": f"Ventana | {'Flotante' if window_mode == 'floating_hint' else 'Normal'}",
			"ignore_videoresize": f"Videoresize | {'ignorado' if self.profile_data.get('ignore_videoresize', False) else 'activo'}",
			"capture_mode": f"Captura | {'OBS' if self.profile_data.get('capture_mode') == 'obs_green' else 'Normal'}",
			"mono_font": f"Fuente | {ui_font_family}",
			"controller_style": f"Control | {active_profile.get('controller_style', 'default')}",
			"active_profile": f"Perfil | {active_profile['name']}",
			"button_count": f"Botones | {active_profile['button_count']}",
			"default_input": f"Entrada | {active_profile['input_mode']}",
			"global_keyboard": f"Teclado | {'ninguno' if not active_profile.get('preferred_keyboard_path') else 'dispositivo'}",
			"joystick_color": f"Color stick | {_color_name_from_values(active_profile['joystick_color'])}",
			"joystick_color_hex": "Color joystick hexa",
			"button_color": f"Color botones | {btn_color_name}",
			"change_icon": "Cambiar icono",
			"create_profile": "Crear perfil",
			"edit_hud_layout": "Editar posicion HUD",
			"export_profile": "Exportar perfil",
			"import_profile": "Importar perfil",
			"save_and_back": "Guardar y volver",
			"cancel": "Cancelar",
		}

	def _render(self, active_profile, option_labels, font, line_gap):
		screen = self.screen
		screen.fill((0, 0, 0))
		padding_x = 12
		screen_width = screen.get_width()
		col_width = screen_width // 2
		title_y = max(20, line_gap)
		draw_centered_text(screen, font, "Configuracion de perfiles", y=title_y)
		table_y = title_y + line_gap + 4
		for row_idx, row_keys in enumerate(self.TABLE_CELLS):
			row_y = table_y + row_idx * line_gap
			for col_idx, key in enumerate(row_keys):
				x = padding_x + col_idx * col_width
				label = option_labels.get(key, key)
				trimmed = fit_text_to_width(font, f"{label}", col_width - 20)
				prefix = ">" if self._key_to_index(key) == self.selected else " "
				draw_text_left(screen, font, f"{prefix}{trimmed}", x, row_y)
		actions_y = table_y + len(self.TABLE_CELLS) * line_gap + 8
		for vi, key in enumerate(self.ACTIONS_ROW):
			idx = self._key_to_index(key)
			prefix = ">" if idx == self.selected else " "
			label = fit_text_to_width(font, option_labels[key], col_width - 20)
			draw_text_left(screen, font, f"{prefix}{label}", padding_x + (vi % 2) * col_width, actions_y + (vi // 2) * line_gap)
		draw_centered_text(screen, font, "Flechas + Enter | Esc", y=screen.get_height() - 16)

	def _key_to_index(self, key):
		for i, k in enumerate(self.OPTION_KEYS):
			if k == key:
				return i
		return -1

	def _handle_option(self, key, active_profile, window_mode):
		handler = _OPTION_HANDLERS.get(key)
		if handler is None:
			return None
		return handler(self, active_profile, window_mode)

	def _handle_change_icon(self, active_profile, window_mode):
		labels = get_button_labels(active_profile["button_count"])
		label_choice = _run_choice_menu(self.screen, "Selecciona boton", labels, 0, window_mode=window_mode)
		if label_choice is None:
			return
		label = labels[label_choice]
		icon_opts = _available_icon_paths(labels)
		cur_icon = active_profile["button_icons"].get(label, get_default_icon_path(label))
		if cur_icon and cur_icon not in icon_opts:
			icon_opts.append(cur_icon)
		try:
			icon_idx = icon_opts.index(cur_icon)
		except ValueError:
			icon_idx = 0
		icon_choice = _run_choice_menu(self.screen, f"Icono para {label}", icon_opts, icon_idx, window_mode=window_mode)
		if icon_choice is None:
			return
		sel = icon_opts[icon_choice]
		if sel == "ninguno":
			active_profile["button_icons"][label] = None
		elif sel == "Seleccionar...":
			chosen_file, err = pick_image_file_with_validation(initial_dir="icons", max_width=512, max_height=512)
			if chosen_file:
				active_profile["button_icons"][label] = os.path.relpath(chosen_file, os.getcwd())
			elif err:
				_run_message_modal(
					self.screen,
					"Icono invalido",
					[err, "Solo se permiten imagenes <= 512x512."],
					window_mode=window_mode,
				)
		else:
			active_profile["button_icons"][label] = sel

	def _process_config_keydown(self, event, selected, n, cols):
		"""Procesa KEYDOWN del menu config. Retorna (new_selected, action) con action en (None, 'quit', 'save', 'cancel')."""
		if event.key == pygame.K_ESCAPE:
			return selected, "quit"
		if event.key == pygame.K_RETURN:
			return selected, "enter"
		if event.key not in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
			return selected, None
		row, col = selected // cols, selected % cols
		if event.key == pygame.K_UP:
			row = max(0, row - 1)
		elif event.key == pygame.K_DOWN:
			row = min((n - 1) // cols, row + 1)
		elif event.key == pygame.K_LEFT:
			col = max(0, col - 1)
		else:
			col = min(cols - 1, col + 1)
		return min(row * cols + col, n - 1), None

	def run(self):
		clock = pygame.time.Clock()
		n = len(self.OPTION_KEYS)
		cols = 2
		while True:
			set_ui_font_family(self.profile_data.get("ui_font_family", "JetBrainsMono"))
			active_profile = get_active_profile(self.profile_data)
			window_mode = self.profile_data.get("window_mode", "floating_hint")
			ui_font_family = self.profile_data.get("ui_font_family", "JetBrainsMono")
			keyboard_path = active_profile.get("preferred_keyboard_path")
			keyboard_label = "ninguno (foco)" if not keyboard_path else keyboard_path
			option_labels = self._get_option_labels(active_profile, window_mode, ui_font_family, keyboard_label)
			header = ["Configuracion de perfiles"] + list(option_labels.values()) + ["Flechas + Enter | Esc"]
			font, line_gap = build_responsive_font(
				self.screen, header, base_size=20, min_size=12, max_size=30,
				base_resolution=(460, 320), max_height_ratio=0.90,
			)
			self._render(active_profile, option_labels, font, line_gap)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN:
					self.selected, action = self._process_config_keydown(
						event, self.selected, n, cols
					)
					if action == "quit":
						return None
					if action == "enter":
						result = self._handle_option(
							self.OPTION_KEYS[self.selected],
							active_profile,
							window_mode,
						)
						if result == "save":
							return self.profile_data
						if result == "cancel":
							return None
			clock.tick(60)


def _h_toggle_profile(menu, active_profile, window_mode, key):
	active_profile[key] = not active_profile.get(key, False)
	return None


def _h_toggle_pd(menu, active_profile, window_mode, key):
	menu.profile_data[key] = not menu.profile_data.get(key, False)
	return None


def _h_window_mode(menu, active_profile, window_mode):
	pd = menu.profile_data
	pd["window_mode"] = "normal" if pd.get("window_mode") == "floating_hint" else "floating_hint"
	return None


def _h_capture_mode(menu, active_profile, window_mode):
	pd = menu.profile_data
	idx = SUPPORTED_CAPTURE_MODES.index(pd.get("capture_mode", "normal")) if pd.get("capture_mode") in SUPPORTED_CAPTURE_MODES else 0
	pd["capture_mode"] = SUPPORTED_CAPTURE_MODES[(idx + 1) % len(SUPPORTED_CAPTURE_MODES)]
	return None


def _h_choice(menu, active_profile, window_mode, title, options, get_current, set_value):
	cur = get_current(active_profile, menu.profile_data)
	idx = options.index(cur) if cur in options else 0
	chosen = _run_choice_menu(menu.screen, title, options, idx, window_mode=window_mode)
	if chosen is not None:
		set_value(active_profile, menu.profile_data, options[chosen])
	return None


def _h_mono_font(menu, active_profile, window_mode):
	def get(ap, pd): return pd.get("ui_font_family", "JetBrainsMono")
	def set_val(ap, pd, v): pd["ui_font_family"] = v; set_ui_font_family(v)
	return _h_choice(menu, active_profile, window_mode, "Fuente mono", SUPPORTED_MONO_FONT_FAMILIES, get, set_val)


def _h_controller_style(menu, active_profile, window_mode):
	def get(p, _): return p.get("controller_style", "default")
	def set_val(p, _, v): p["controller_style"] = v
	return _h_choice(menu, active_profile, window_mode, "Estilo de control", SUPPORTED_CONTROLLER_STYLES, get, set_val)


def _h_active_profile(menu, active_profile, window_mode):
	pd = menu.profile_data
	names = [p["name"] for p in pd["profiles"]]
	idx = next((i for i, p in enumerate(pd["profiles"]) if p["id"] == pd["active_profile"]), 0)
	chosen = _run_choice_menu(menu.screen, "Selecciona perfil", names, idx, window_mode=window_mode)
	if chosen is not None:
		set_active_profile(pd, pd["profiles"][chosen]["id"])
	return None


def _h_button_count(menu, active_profile, window_mode):
	idx = SUPPORTED_BUTTON_COUNTS.index(active_profile["button_count"])
	nc = SUPPORTED_BUTTON_COUNTS[(idx + 1) % len(SUPPORTED_BUTTON_COUNTS)]
	active_profile["button_count"] = nc
	active_profile["button_icons"] = {lbl: active_profile["button_icons"].get(lbl, get_default_icon_path(lbl)) for lbl in get_button_labels(nc)}
	return None


def _h_default_input(menu, active_profile, window_mode):
	def get(p, _): return p["input_mode"]
	def set_val(p, _, v): p["input_mode"] = v
	return _h_choice(menu, active_profile, window_mode, "Entrada por defecto", SUPPORTED_INPUT_MODES, get, set_val)


def _h_global_keyboard(menu, active_profile, window_mode):
	kb_opts = _keyboard_device_options()
	labels = [x[0] for x in kb_opts]
	paths = [x[1] for x in kb_opts]
	cur = active_profile.get("preferred_keyboard_path")
	idx = next((i for i, p in enumerate(paths) if p == cur), 0)
	chosen = _run_choice_menu(menu.screen, "Teclado global", labels, idx, window_mode=window_mode)
	if chosen is not None:
		active_profile["preferred_keyboard_path"] = paths[chosen]
	return None


def _h_joystick_color(menu, active_profile, window_mode):
	names = list(JOYSTICK_COLOR_PRESETS.keys())
	try:
		idx = names.index(_color_name_from_values(active_profile["joystick_color"]))
	except ValueError:
		idx = 0
	chosen = _run_choice_menu(menu.screen, "Color joystick", names, idx, window_mode=window_mode)
	if chosen is not None:
		col = list(JOYSTICK_COLOR_PRESETS[names[chosen]])
		active_profile["joystick_color"] = col
		active_profile["joystick_knob_color"] = list(col)
	return None


def _h_button_color(menu, active_profile, window_mode):
	names = list(BUTTON_COLOR_PRESETS.keys())
	try:
		idx = names.index(_button_color_preset_name(
			active_profile.get("button_color_inactive", [80, 80, 80]),
			active_profile.get("button_color_active", [255, 0, 0]),
		))
	except ValueError:
		idx = 0
	chosen = _run_choice_menu(menu.screen, "Color de botones", names, idx, window_mode=window_mode)
	if chosen is not None:
		preset = BUTTON_COLOR_PRESETS[names[chosen]]
		active_profile["button_color_inactive"] = list(preset["inactive"])
		active_profile["button_color_active"] = list(preset["active"])
	return None


def _h_joystick_color_hex(menu, active_profile, window_mode):
	knob_hex = rgb_to_hex(active_profile.get("joystick_knob_color", active_profile.get("joystick_color", [0, 255, 0])))
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


def _h_change_icon(menu, active_profile, window_mode):
	menu._handle_change_icon(active_profile, window_mode)
	return None


def _h_create_profile(menu, active_profile, window_mode):
	create_profile(menu.profile_data, get_active_profile(menu.profile_data))
	return None


def _h_edit_hud_layout(menu, active_profile, window_mode):
	run_hud_layout_editor(menu.screen, active_profile, window_mode=window_mode)
	return None


def _h_export_profile(menu, active_profile, window_mode):
	dest_dir = pick_directory(title="Guardar perfil en...")
	if not dest_dir:
		return None
	zip_path = export_profile_to_zip(active_profile, dest_dir)
	if zip_path:
		_run_message_modal(
			menu.screen,
			"Exportado",
			[f"Perfil guardado en {zip_path}"],
			window_mode=window_mode,
		)
	else:
		_run_message_modal(
			menu.screen,
			"Error",
			["No se pudo exportar el perfil."],
			window_mode=window_mode,
		)
	return None


def _h_import_profile(menu, active_profile, window_mode):
	zip_path = pick_zip_file(title="Seleccionar perfil ZIP")
	if not zip_path:
		return None

	def conflict_resolver(imported_name):
		choice = _run_choice_menu(
			menu.screen,
			f"Perfil '{imported_name}' ya existe",
			["Sobrescribir", "Renombrar (_importado)", "Cancelar"],
			0,
			window_mode=window_mode,
		)
		if choice is None or choice == 2:
			return "cancel"
		if choice == 0:
			return "overwrite"
		return "rename"

	try:
		imported = import_profile_from_zip(
			zip_path, menu.profile_data, conflict_resolver=conflict_resolver
		)
		if imported:
			_run_message_modal(
				menu.screen,
				"Importado",
				[f"Perfil '{imported['name']}' importado correctamente."],
				window_mode=window_mode,
			)
	except ValueError as e:
		_run_message_modal(menu.screen, "Error", [str(e)], window_mode=window_mode)
	return None


def _h_cancel(menu, active_profile, window_mode):
	pd = menu.profile_data
	snap = menu.snapshot
	pd["active_profile"] = snap["active_profile"]
	pd["window_mode"] = snap["window_mode"]
	pd["ignore_videoresize"] = snap["ignore_videoresize"]
	pd["capture_mode"] = snap["capture_mode"]
	pd["ui_font_family"] = snap["ui_font_family"]
	pd["profiles"] = snap["profiles"]
	set_ui_font_family(pd["ui_font_family"])
	return "cancel"


_OPTION_HANDLERS = {
	"tournament_mode": lambda m, p, w: _h_toggle_profile(m, p, w, "tournament_mode"),
	"hitbox_alt_layout": lambda m, p, w: _h_toggle_profile(m, p, w, "hitbox_alt_layout"),
	"window_mode": _h_window_mode,
	"ignore_videoresize": lambda m, p, w: _h_toggle_pd(m, p, w, "ignore_videoresize"),
	"capture_mode": _h_capture_mode,
	"mono_font": _h_mono_font,
	"controller_style": _h_controller_style,
	"active_profile": _h_active_profile,
	"button_count": _h_button_count,
	"default_input": _h_default_input,
	"global_keyboard": _h_global_keyboard,
	"joystick_color": _h_joystick_color,
	"button_color": _h_button_color,
	"joystick_color_hex": _h_joystick_color_hex,
	"change_icon": _h_change_icon,
	"create_profile": _h_create_profile,
	"edit_hud_layout": _h_edit_hud_layout,
	"export_profile": _h_export_profile,
	"import_profile": _h_import_profile,
	"save_and_back": lambda m, p, w: "save",
	"cancel": _h_cancel,
}


def open_profile_config_menu(screen, profile_data):
	menu = ProfileConfigMenu(screen, profile_data)
	return menu.run()
