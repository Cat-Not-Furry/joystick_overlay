import os
import pygame
from config import (
	JOYSTICK_COLOR_PRESETS,
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
	build_responsive_font,
	fit_text_to_width,
	run_modal_child_window,
	list_keyboard_devices_by_capabilities,
	set_ui_font_family,
)
from profile_store import get_active_profile, set_active_profile, create_profile
from image_file_picker import pick_image_file_with_validation


def _color_name_from_values(values):
	for name, preset_values in JOYSTICK_COLOR_PRESETS.items():
		if list(preset_values) == list(values):
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
	)


def _run_message_modal(title, message_lines, window_mode="floating_hint"):
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
	)


def open_profile_config_menu(screen, profile_data):
	clock = pygame.time.Clock()
	selected = 0
	option_keys = [
		"tournament_mode",
		"window_mode",
		"capture_mode",
		"mono_font",
		"controller_style",
		"active_profile",
		"button_count",
		"default_input",
		"global_keyboard",
		"joystick_color",
		"joystick_color_hex",
		"change_icon",
		"create_profile",
		"save_and_back",
		"cancel",
	]

	snapshot = {
		"active_profile": profile_data["active_profile"],
		"window_mode": profile_data.get("window_mode", "floating_hint"),
		"capture_mode": profile_data.get("capture_mode", "normal"),
		"ui_font_family": profile_data.get("ui_font_family", "JetBrainsMono"),
		"profiles": [
			{
				**profile,
				"joystick_color": list(profile["joystick_color"]),
				"button_icons": dict(profile["button_icons"]),
				"key_bindings": dict(profile["key_bindings"]),
				"joystick_bindings": dict(profile["joystick_bindings"]),
			}
			for profile in profile_data["profiles"]
		],
	}

	while True:
		set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))
		active_profile = get_active_profile(profile_data)
		color_name = _color_name_from_values(active_profile["joystick_color"])
		tournament_mode = "on" if active_profile.get("tournament_mode", False) else "off"
		tournament_mode_text = "On" if active_profile.get("tournament_mode", False) else "Off"
		window_mode = profile_data.get("window_mode", "floating_hint")
		capture_mode = profile_data.get("capture_mode", "normal")
		ui_font_family = profile_data.get("ui_font_family", "JetBrainsMono")
		keyboard_path = active_profile.get("preferred_keyboard_path")
		keyboard_label = "ninguno (foco)" if not keyboard_path else keyboard_path
		option_labels = {
			"tournament_mode": f"Modo torneo | {tournament_mode_text}",
			"window_mode": "Modo de ventana",
			"capture_mode": "Modo de captura",
			"mono_font": f"Fuente mono | {ui_font_family}",
			"controller_style": "Estilo de control",
			"active_profile": "Perfil activo",
			"button_count": "Cantidad de botones",
			"default_input": "Entrada por defecto",
			"global_keyboard": "Teclado global",
			"joystick_color": "Color joystick",
			"joystick_color_hex": "Color joystick hexa",
			"change_icon": "Cambiar icono de boton",
			"create_profile": "Crear perfil nuevo",
			"save_and_back": "Guardar y volver",
			"cancel": "Cancelar",
		}

		header_lines = [
			"Configuracion de perfiles",
			f"Ventana: {window_mode}",
			f"Captura: {capture_mode}",
			f"Fuente: {ui_font_family}",
			f"Torneo: {tournament_mode}",
			f"Perfil: {active_profile['name']}",
			f"Botones: {active_profile['button_count']} | Control: {active_profile.get('controller_style', 'default')}",
			f"Entrada: {active_profile['input_mode']} | Color: {color_name}",
			f"Teclado global: {keyboard_label}",
			"Flechas + Enter | Esc",
		]
		font, line_gap = build_responsive_font(
			screen,
			header_lines,
			base_size=20,
			min_size=12,
			max_size=30,
			base_resolution=(460, 320),
			max_height_ratio=0.90,
		)

		screen.fill((0, 0, 0))
		title_y = max(20, line_gap)
		draw_centered_text(screen, font, "Configuracion de perfiles", y=title_y)
		lines = [
			f"Ventana: {window_mode}",
			f"Captura: {capture_mode}",
			f"Fuente: {ui_font_family}",
			f"Perfil: {active_profile['name']}",
			f"Botones: {active_profile['button_count']} | Control: {active_profile.get('controller_style', 'default')}",
			f"Entrada: {active_profile['input_mode']} | Color: {color_name}",
			f"Teclado global: {keyboard_label}",
		]
		for line_index, line in enumerate(lines):
			trimmed_line = fit_text_to_width(font, line, int(screen.get_width() * 0.92))
			draw_centered_text(screen, font, trimmed_line, y=title_y + line_gap + line_index * line_gap)

		start_index = max(0, selected - 1)
		end_index = min(len(option_keys), start_index + 3)
		visible_keys = option_keys[start_index:end_index]
		options_start_y = title_y + line_gap + len(lines) * line_gap + 5
		for visible_index, option_key in enumerate(visible_keys):
			option_index = start_index + visible_index
			prefix = ">" if option_index == selected else " "
			draw_centered_text(screen, font, f"{prefix} {option_labels[option_key]}", y=options_start_y + visible_index * line_gap)

		draw_centered_text(screen, font, "Flechas + Enter | Esc", y=screen.get_height() - 16)
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return None

			if event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_UP, pygame.K_LEFT):
					selected = (selected - 1) % len(option_keys)
				elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
					selected = (selected + 1) % len(option_keys)
				elif event.key == pygame.K_ESCAPE:
					return None
				elif event.key == pygame.K_RETURN:
					current_option = option_keys[selected]
					if current_option == "tournament_mode":
						active_profile["tournament_mode"] = not active_profile.get("tournament_mode", False)

					elif current_option == "window_mode":
						window_options = ["floating_hint", "normal"]
						current_index = 0 if window_mode == "floating_hint" else 1
						chosen = _run_choice_menu(
							screen,
							"Modo de ventana",
							window_options,
							current_index,
							window_mode=window_mode
						)
						if chosen is not None:
							profile_data["window_mode"] = window_options[chosen]

					elif current_option == "capture_mode":
						current_index = SUPPORTED_CAPTURE_MODES.index(capture_mode) if capture_mode in SUPPORTED_CAPTURE_MODES else 0
						chosen = _run_choice_menu(
							screen,
							"Modo de captura",
							SUPPORTED_CAPTURE_MODES,
							current_index,
							window_mode=window_mode
						)
						if chosen is not None:
							profile_data["capture_mode"] = SUPPORTED_CAPTURE_MODES[chosen]

					elif current_option == "mono_font":
						current_index = SUPPORTED_MONO_FONT_FAMILIES.index(ui_font_family) if ui_font_family in SUPPORTED_MONO_FONT_FAMILIES else 0
						chosen = _run_choice_menu(
							screen,
							"Fuente mono",
							SUPPORTED_MONO_FONT_FAMILIES,
							current_index,
							window_mode=window_mode
						)
						if chosen is not None:
							profile_data["ui_font_family"] = SUPPORTED_MONO_FONT_FAMILIES[chosen]
							set_ui_font_family(profile_data["ui_font_family"])

					elif current_option == "controller_style":
						control_options = SUPPORTED_CONTROLLER_STYLES
						current_style = active_profile.get("controller_style", "default")
						current_index = control_options.index(current_style) if current_style in control_options else 0
						chosen = _run_choice_menu(
							screen,
							"Estilo de control",
							control_options,
							current_index,
							window_mode=window_mode
						)
						if chosen is not None:
							active_profile["controller_style"] = control_options[chosen]

					elif current_option == "active_profile":
						profile_names = [profile["name"] for profile in profile_data["profiles"]]
						current_index = next(
							(
								index
								for index, profile in enumerate(profile_data["profiles"])
								if profile["id"] == profile_data["active_profile"]
							),
							0,
						)
						chosen = _run_choice_menu(
							screen,
							"Selecciona perfil",
							profile_names,
							current_index,
							window_mode=window_mode
						)
						if chosen is not None:
							set_active_profile(profile_data, profile_data["profiles"][chosen]["id"])

					elif current_option == "button_count":
						button_options = [str(count) for count in SUPPORTED_BUTTON_COUNTS]
						current_index = SUPPORTED_BUTTON_COUNTS.index(active_profile["button_count"])
						chosen = _run_choice_menu(
							screen,
							"Cantidad de botones",
							button_options,
							current_index,
							window_mode=window_mode
						)
						if chosen is not None:
							new_count = SUPPORTED_BUTTON_COUNTS[chosen]
							active_profile["button_count"] = new_count
							active_profile["button_icons"] = {
								label: active_profile["button_icons"].get(label, get_default_icon_path(label))
								for label in get_button_labels(new_count)
							}

					elif current_option == "default_input":
						input_modes = SUPPORTED_INPUT_MODES
						current_index = input_modes.index(active_profile["input_mode"])
						chosen = _run_choice_menu(
							screen,
							"Entrada por defecto",
							input_modes,
							current_index,
							window_mode=window_mode
						)
						if chosen is not None:
							active_profile["input_mode"] = input_modes[chosen]

					elif current_option == "global_keyboard":
						keyboard_options = _keyboard_device_options()
						labels = [item[0] for item in keyboard_options]
						paths = [item[1] for item in keyboard_options]
						current_path = active_profile.get("preferred_keyboard_path")
						current_index = 0
						for index, path in enumerate(paths):
							if path == current_path:
								current_index = index
								break
						chosen = _run_choice_menu(
							screen,
							"Teclado global",
							labels,
							current_index,
							window_mode=window_mode
						)
						if chosen is not None:
							active_profile["preferred_keyboard_path"] = paths[chosen]

					elif current_option == "joystick_color":
						color_names = list(JOYSTICK_COLOR_PRESETS.keys())
						try:
							current_index = color_names.index(_color_name_from_values(active_profile["joystick_color"]))
						except ValueError:
							current_index = 0
						chosen = _run_choice_menu(
							screen,
							"Color joystick",
							color_names,
							current_index,
							window_mode=window_mode
						)
						if chosen is not None:
							selected_color = list(JOYSTICK_COLOR_PRESETS[color_names[chosen]])
							active_profile["joystick_color"] = selected_color
							active_profile["joystick_knob_color"] = list(selected_color)

					elif current_option == "joystick_color_hex":
						current_knob = rgb_to_hex(active_profile.get("joystick_knob_color", active_profile.get("joystick_color", [0, 255, 0])))
						current_bar = rgb_to_hex(active_profile.get("joystick_bar_color", [0, 0, 0]))
						current_ring = rgb_to_hex(active_profile.get("joystick_ring_color", [255, 255, 255]))

						knob_text = _run_text_input(screen, "Hex joystick (knob)", current_knob, window_mode=window_mode)
						if knob_text is None:
							continue
						bar_text = _run_text_input(screen, "Hex barra (stick)", current_bar, window_mode=window_mode)
						if bar_text is None:
							continue
						ring_text = _run_text_input(screen, "Hex anillo", current_ring, window_mode=window_mode)
						if ring_text is None:
							continue

						knob_color = parse_hex_color(knob_text)
						bar_color = parse_hex_color(bar_text)
						ring_color = parse_hex_color(ring_text)
						if knob_color and bar_color and ring_color:
							active_profile["joystick_knob_color"] = knob_color
							active_profile["joystick_bar_color"] = bar_color
							active_profile["joystick_ring_color"] = ring_color
							active_profile["joystick_color"] = list(knob_color)

					elif current_option == "change_icon":
						labels = get_button_labels(active_profile["button_count"])
						label_choice = _run_choice_menu(
							screen,
							"Selecciona boton",
							labels,
							0,
							window_mode=window_mode
						)
						if label_choice is not None:
							label = labels[label_choice]
							icon_options = _available_icon_paths(labels)
							current_icon = active_profile["button_icons"].get(label, get_default_icon_path(label))
							if current_icon and current_icon not in icon_options:
								icon_options.append(current_icon)
							try:
								icon_index = icon_options.index(current_icon)
							except ValueError:
								icon_index = 0
							icon_choice = _run_choice_menu(
								screen,
								f"Icono para {label}",
								icon_options,
								icon_index,
								window_mode=window_mode
							)
							if icon_choice is not None:
								selected_icon = icon_options[icon_choice]
								if selected_icon == "ninguno":
									active_profile["button_icons"][label] = None
								elif selected_icon == "Seleccionar...":
									chosen_file, error_message = pick_image_file_with_validation(
										initial_dir="icons",
										max_width=512,
										max_height=512,
									)
									if chosen_file:
										relative_path = os.path.relpath(chosen_file, os.getcwd())
										active_profile["button_icons"][label] = relative_path
									elif error_message:
										_run_message_modal(
											"Icono invalido",
											[
												error_message,
												"Solo se permiten imagenes <= 512x512.",
											],
											window_mode=window_mode,
										)
								else:
									active_profile["button_icons"][label] = selected_icon

					elif current_option == "create_profile":
						active_profile = get_active_profile(profile_data)
						create_profile(profile_data, active_profile)

					elif current_option == "save_and_back":
						return profile_data

					elif current_option == "cancel":
						profile_data["active_profile"] = snapshot["active_profile"]
						profile_data["window_mode"] = snapshot["window_mode"]
						profile_data["capture_mode"] = snapshot["capture_mode"]
						profile_data["ui_font_family"] = snapshot["ui_font_family"]
						profile_data["profiles"] = snapshot["profiles"]
						set_ui_font_family(profile_data["ui_font_family"])
						return None
		clock.tick(60)
