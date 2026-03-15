import os
import pygame
from config import (
	JOYSTICK_COLOR_PRESETS, SUPPORTED_BUTTON_COUNTS, SUPPORTED_CONTROLLER_STYLES, SUPPORTED_CAPTURE_MODES,
	get_button_labels, get_default_icon_path
)
from utils import (
	draw_centered_text,
	build_responsive_font,
	fit_text_to_width,
	open_secondary_window,
	restore_primary_window,
	list_keyboard_devices_by_capabilities,
)
from profile_store import get_active_profile, set_active_profile, create_profile


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
	return options

def _keyboard_device_options():
	options = [("ninguno (solo con foco)", None)]
	devices = list_keyboard_devices_by_capabilities()
	for device in devices:
		options.append((f"{device.name} | {device.path}", device.path))
	for device in devices:
		device.close()
	return options


def _run_choice_menu(screen, title, options, initial_index=0, window_mode="floating_hint"):
	secondary, primary_size = open_secondary_window(
		title,
		size=(540, 320),
		window_mode=window_mode
	)
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
				restore_primary_window(primary_size, window_mode=window_mode)
				return None
			if event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_UP, pygame.K_LEFT):
					selected = (selected - 1) % len(options)
				elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
					selected = (selected + 1) % len(options)
				elif event.key == pygame.K_RETURN:
					restore_primary_window(primary_size, window_mode=window_mode)
					return selected
				elif event.key == pygame.K_ESCAPE:
					restore_primary_window(primary_size, window_mode=window_mode)
					return None
		clock.tick(60)


def open_profile_config_menu(screen, profile_data):
	font = pygame.font.SysFont(None, 20)
	clock = pygame.time.Clock()
	selected = 0
	options = [
		"Modo de ventana",
		"Modo de captura",
		"Estilo de control",
		"Perfil activo",
		"Cantidad de botones",
		"Entrada por defecto",
		"Teclado global",
		"Color joystick",
		"Cambiar icono de boton",
		"Crear perfil nuevo",
		"Guardar y volver",
		"Cancelar",
	]

	snapshot = {
		"active_profile": profile_data["active_profile"],
		"window_mode": profile_data.get("window_mode", "floating_hint"),
		"capture_mode": profile_data.get("capture_mode", "normal"),
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
		active_profile = get_active_profile(profile_data)
		color_name = _color_name_from_values(active_profile["joystick_color"])
		window_mode = profile_data.get("window_mode", "floating_hint")
		capture_mode = profile_data.get("capture_mode", "normal")
		keyboard_path = active_profile.get("preferred_keyboard_path")
		keyboard_label = "ninguno (foco)" if not keyboard_path else keyboard_path

		header_lines = [
			"Configuracion de perfiles",
			f"Ventana: {window_mode}",
			f"Captura: {capture_mode}",
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
			f"Perfil: {active_profile['name']}",
			f"Botones: {active_profile['button_count']} | Control: {active_profile.get('controller_style', 'default')}",
			f"Entrada: {active_profile['input_mode']} | Color: {color_name}",
			f"Teclado global: {keyboard_label}",
		]
		for line_index, line in enumerate(lines):
			trimmed_line = fit_text_to_width(font, line, int(screen.get_width() * 0.92))
			draw_centered_text(screen, font, trimmed_line, y=title_y + line_gap + line_index * line_gap)

		start_index = max(0, selected - 1)
		end_index = min(len(options), start_index + 3)
		visible_options = options[start_index:end_index]
		options_start_y = title_y + line_gap + len(lines) * line_gap + 5
		for visible_index, option in enumerate(visible_options):
			option_index = start_index + visible_index
			prefix = ">" if option_index == selected else " "
			draw_centered_text(screen, font, f"{prefix} {option}", y=options_start_y + visible_index * line_gap)

		draw_centered_text(screen, font, "Flechas + Enter | Esc", y=screen.get_height() - 16)
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return None

			if event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_UP, pygame.K_LEFT):
					selected = (selected - 1) % len(options)
				elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
					selected = (selected + 1) % len(options)
				elif event.key == pygame.K_ESCAPE:
					return None
				elif event.key == pygame.K_RETURN:
					current_option = options[selected]
					if current_option == "Modo de ventana":
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

					elif current_option == "Modo de captura":
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

					elif current_option == "Estilo de control":
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

					elif current_option == "Perfil activo":
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

					elif current_option == "Cantidad de botones":
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

					elif current_option == "Entrada por defecto":
						input_modes = ["teclado", "joystick"]
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

					elif current_option == "Teclado global":
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

					elif current_option == "Color joystick":
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
							active_profile["joystick_color"] = list(JOYSTICK_COLOR_PRESETS[color_names[chosen]])

					elif current_option == "Cambiar icono de boton":
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
								active_profile["button_icons"][label] = None if selected_icon == "ninguno" else selected_icon

					elif current_option == "Crear perfil nuevo":
						active_profile = get_active_profile(profile_data)
						create_profile(profile_data, active_profile)

					elif current_option == "Guardar y volver":
						return profile_data

					elif current_option == "Cancelar":
						profile_data["active_profile"] = snapshot["active_profile"]
						profile_data["window_mode"] = snapshot["window_mode"]
						profile_data["capture_mode"] = snapshot["capture_mode"]
						profile_data["profiles"] = snapshot["profiles"]
						return None
		clock.tick(60)
