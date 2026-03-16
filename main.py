# main.py

# ---Archivo principal ---

import pygame
import threading
import sys
import os
import subprocess
from config import (
	SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TOURNAMENT_FPS, get_button_labels, get_background_color,
	EASTEREGG_ENABLE_MULTI_INSTANCE, EASTEREGG_MULTI_INSTANCE_KEY, EASTEREGG_MAX_INSTANCES
)
from button_format_selector import choose_button_format
from input_selector import choose_input_mode
from keymapper import map_keys
from joystick_mapper import map_joystick_buttons, run_joystick_diagnostic
from input_reader import start_input_listener
from hud_renderer import draw_hud, load_icons, set_stick_color, set_controller_style
from hud_renderer import set_stick_colors, set_render_mode, set_input_layout
from profile_store import (
	load_profiles_data, save_profiles_data, get_active_profile,
	sync_active_profile_to_legacy_files
)
from profile_config_menu import open_profile_config_menu
from utils import (
	draw_centered_text,
	build_responsive_font,
	fit_text_to_width,
	open_secondary_window,
	restore_primary_window,
	list_keyboard_devices_by_capabilities,
	set_ui_font_family,
)

# Funcines Principales
MENU_WIDTH = 320
MENU_HEIGHT = 180
SELECTOR_WINDOW_SIZE = (500, 300)
MAPPER_WINDOW_SIZE = (620, 380)
CONFIRM_WINDOW_SIZE = (420, 230)

def _set_window_size(width, height, title):
	screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
	window_mode = "floating_hint"
	try:
		window_mode = _current_window_mode
	except NameError:
		pass
	if window_mode == "floating_hint" and hasattr(pygame.display, "set_window_size"):
		pygame.display.set_window_size(width, height)
	pygame.display.set_caption(title)
	return screen

def _count_running_overlay_instances():
	current_pid = os.getpid()
	count = 0
	for pid_text in os.listdir("/proc"):
		if not pid_text.isdigit():
			continue
		pid = int(pid_text)
		if pid == current_pid:
			continue
		cmdline_path = f"/proc/{pid_text}/cmdline"
		try:
			with open(cmdline_path, "rb") as cmdline_file:
				raw = cmdline_file.read().decode("utf-8", errors="ignore")
		except Exception:
			continue
		cmdline = raw.replace("\x00", " ").strip()
		if "python" in cmdline and "main.py" in cmdline and "hud_overlay" in cmdline:
			count += 1
	return count

def _launch_easteregg_instance():
	# Easteregg: permite abrir nuevas instancias para comparar dispositivos.
	if not EASTEREGG_ENABLE_MULTI_INSTANCE:
		return False
	if _count_running_overlay_instances() + 1 >= EASTEREGG_MAX_INSTANCES:
		print(f"[WARN] Limite de instancias alcanzado ({EASTEREGG_MAX_INSTANCES}).")
		return False

	main_path = os.path.join(os.path.dirname(__file__), "main.py")
	try:
		subprocess.Popen(
			[sys.executable, main_path],
			cwd=os.path.dirname(__file__),
			start_new_session=True
		)
		print("[INFO] Easteregg activado: nueva instancia iniciada.")
		return True
	except Exception as error:
		print(f"[WARN] No se pudo abrir una nueva instancia: {error}")
		return False

def _run_secondary_selector(title, size, runner):
	window_mode = "floating_hint"
	try:
		window_mode = _current_window_mode
	except NameError:
		pass
	secondary, primary_size = open_secondary_window(
		title,
		size=size,
		window_mode=window_mode
	)
	result = runner(secondary)
	primary = restore_primary_window(
		primary_size,
		window_mode=window_mode,
		title="Arcade HUD Overlay"
	)
	return result, primary

def select_profile_secondary(profile_data, title="Selecciona perfil"):
	def _runner(screen):
		clock = pygame.time.Clock()
		profiles = profile_data["profiles"]
		selected = 0
		for index, profile in enumerate(profiles):
			if profile["id"] == profile_data.get("active_profile"):
				selected = index
				break

		while True:
			profile_names = [profile["name"] for profile in profiles]
			lines = [title] + profile_names[:6] + ["Flechas + Enter | Esc"]
			font, line_gap = build_responsive_font(
				screen,
				lines,
				base_size=28,
				min_size=14,
				max_size=34,
				base_resolution=SELECTOR_WINDOW_SIZE,
				max_height_ratio=0.82,
			)
			screen.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(screen, font, title, y=title_y)
			start_index = max(0, selected - 2)
			end_index = min(len(profiles), start_index + 5)
			visible = profiles[start_index:end_index]
			start_y = title_y + line_gap
			for visible_index, profile in enumerate(visible):
				option_index = start_index + visible_index
				prefix = ">" if option_index == selected else " "
				draw_centered_text(screen, font, f"{prefix} {profile['name']}", y=start_y + visible_index * line_gap)
			draw_centered_text(screen, font, "Flechas + Enter | Esc", y=screen.get_height() - max(20, line_gap))
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_UP, pygame.K_LEFT):
						selected = (selected - 1) % len(profiles)
					elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
						selected = (selected + 1) % len(profiles)
					elif event.key == pygame.K_ESCAPE:
						return None
					elif event.key == pygame.K_RETURN:
						return profiles[selected]["id"]
			clock.tick(FPS)

	selected_id, screen = _run_secondary_selector(title, SELECTOR_WINDOW_SIZE, _runner)
	return selected_id, screen

def _confirm_exit_secondary():
	def _runner(screen):
		clock = pygame.time.Clock()
		selected = 1
		options = ["No", "Si"]
		while True:
			render_lines = ["Confirmar salida", "Deseas cerrar el HUD?"] + options + ["Flechas + Enter | Esc"]
			font, line_gap = build_responsive_font(
				screen,
				render_lines,
				base_size=30,
				min_size=14,
				max_size=34,
				base_resolution=(420, 220),
			)
			screen.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(screen, font, "Confirmar salida", y=title_y)
			draw_centered_text(screen, font, "Deseas cerrar el HUD?", y=title_y + line_gap)
			for index, option in enumerate(options):
				prefix = ">" if index == selected else " "
				draw_centered_text(screen, font, f"{prefix} {option}", y=title_y + line_gap * (3 + index))
			draw_centered_text(screen, font, "Flechas + Enter | Esc", y=screen.get_height() - max(20, line_gap))
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return False
				if event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT):
						selected = (selected + 1) % len(options)
					elif event.key == pygame.K_ESCAPE:
						return False
					elif event.key == pygame.K_RETURN:
						return options[selected] == "Si"
			clock.tick(FPS)

	confirmed, restored = _run_secondary_selector("Confirmar salida", CONFIRM_WINDOW_SIZE, _runner)
	return confirmed, restored

def _confirm_keyboard_remap_secondary():
	def _runner(screen):
		clock = pygame.time.Clock()
		selected = 0
		options = ["No", "Si", "Cancelar y volver"]
		while True:
			render_lines = ["Modo teclado", "Quieres remapear teclas?"] + options + ["Flechas + Enter | Esc"]
			font, line_gap = build_responsive_font(
				screen,
				render_lines,
				base_size=30,
				min_size=14,
				max_size=34,
				base_resolution=(420, 220),
			)
			screen.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(screen, font, "Modo teclado", y=title_y)
			draw_centered_text(screen, font, "Quieres remapear teclas?", y=title_y + line_gap)
			for index, option in enumerate(options):
				prefix = ">" if index == selected else " "
				draw_centered_text(screen, font, f"{prefix} {option}", y=title_y + line_gap * (3 + index))
			draw_centered_text(screen, font, "Flechas + Enter | Esc", y=screen.get_height() - max(20, line_gap))
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return False
				if event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT):
						if event.key in (pygame.K_UP, pygame.K_LEFT):
							selected = (selected - 1) % len(options)
						else:
							selected = (selected + 1) % len(options)
					elif event.key == pygame.K_ESCAPE:
						return "cancelar"
					elif event.key == pygame.K_RETURN:
						if options[selected] == "Si":
							return "si"
						if options[selected] == "No":
							return "no"
						return "cancelar"
			clock.tick(FPS)

	confirmed, restored = _run_secondary_selector("Remapeo teclado", CONFIRM_WINDOW_SIZE, _runner)
	return confirmed, restored

def _choose_keyboard_device_secondary(current_path):
	def _runner(screen):
		clock = pygame.time.Clock()
		devices = list_keyboard_devices_by_capabilities()
		options = [("Ninguno (solo con foco)", None)]
		for device in devices:
			options.append((f"{device.name} | {device.path}", device.path))
		for device in devices:
			device.close()

		selected = 0
		for index, option in enumerate(options):
			if option[1] == current_path:
				selected = index
				break

		while True:
			lines_for_fit = ["Teclado global (sin foco)"] + [label for label, _ in options[:6]] + ["Flechas + Enter | Esc"]
			font, line_gap = build_responsive_font(
				screen,
				lines_for_fit,
				base_size=28,
				min_size=14,
				max_size=34,
				base_resolution=SELECTOR_WINDOW_SIZE,
				max_height_ratio=0.82,
			)
			screen.fill((0, 0, 0))
			title_y = max(28, line_gap)
			draw_centered_text(screen, font, "Teclado global (sin foco)", y=title_y)

			start_index = max(0, selected - 2)
			end_index = min(len(options), start_index + 5)
			visible = options[start_index:end_index]
			start_y = title_y + line_gap
			for visible_index, (label, _) in enumerate(visible):
				option_index = start_index + visible_index
				prefix = ">" if option_index == selected else " "
				trimmed = fit_text_to_width(font, label, int(screen.get_width() * 0.90))
				draw_centered_text(screen, font, f"{prefix} {trimmed}", y=start_y + visible_index * line_gap)

			draw_centered_text(screen, font, "Flechas + Enter | Esc", y=screen.get_height() - max(20, line_gap))
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return "cancelar", current_path
				if event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_UP, pygame.K_LEFT):
						selected = (selected - 1) % len(options)
					elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
						selected = (selected + 1) % len(options)
					elif event.key == pygame.K_ESCAPE:
						return "cancelar", current_path
					elif event.key == pygame.K_RETURN:
						return "ok", options[selected][1]
			clock.tick(FPS)

	result, restored = _run_secondary_selector("Teclado global", SELECTOR_WINDOW_SIZE, _runner)
	return result, restored

def show_main_menu(screen):
	options = ["Iniciar HUD", "Configurar perfiles", "Salir"]
	selected = 0
	clock = pygame.time.Clock()
	force_resize_frames = FPS
	frame_count = 0

	while True:
		if _current_window_mode == "floating_hint" and frame_count < force_resize_frames:
			if hasattr(pygame.display, "set_window_size"):
				pygame.display.set_window_size(MENU_WIDTH, MENU_HEIGHT)
		frame_count += 1

		lines = ["HUD Overlay"] + options + ["Flechas + Enter"] + ["Space en Iniciar HUD: nueva instancia"]
		font, line_gap = build_responsive_font(
			screen,
			lines,
			base_size=30,
			min_size=14,
			max_size=36,
			base_resolution=(MENU_WIDTH, MENU_HEIGHT),
			max_height_ratio=0.88,
		)
		screen.fill((0, 0, 0))
		title_y = max(28, line_gap)
		base_y = title_y + line_gap
		for index, option in enumerate(options):
			prefix = ">" if index == selected else " "
			draw_centered_text(screen, font, f"{prefix} {option}", y=base_y + index * line_gap)
		hint_y = base_y + len(options) * line_gap
		draw_centered_text(screen, font, "HUD Overlay", y=title_y)
		draw_centered_text(screen, font, "Flechas + Enter", y=hint_y)
		if selected == 0 and EASTEREGG_ENABLE_MULTI_INSTANCE:
			draw_centered_text(screen, font, "Space: instancia extra", y=screen.get_height() - max(18, line_gap))
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return "salir"
			if event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_UP, pygame.K_LEFT):
					selected = (selected - 1) % len(options)
				elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
					selected = (selected + 1) % len(options)
				elif event.key == pygame.K_ESCAPE:
					return "salir"
				elif event.key == pygame.K_SPACE and selected == 0 and EASTEREGG_MULTI_INSTANCE_KEY == "space":
					_launch_easteregg_instance()
				elif event.key == pygame.K_RETURN:
					if selected == 0:
						return "iniciar"
					if selected == 1:
						return "configurar"
					return "salir"
		clock.tick(FPS)

def _open_config_secondary_window(profile_data):
	screen, primary_size = open_secondary_window(
		"Configuracion de perfiles",
		size=(460, 320),
		window_mode=_current_window_mode
	)
	updated = open_profile_config_menu(screen, profile_data)
	restored = restore_primary_window(primary_size, window_mode=_current_window_mode, title="Arcade HUD Overlay")
	return updated, restored


def run_hud_session(screen, profile_data, interactive_setup=True, force_tournament=False):
	profile = get_active_profile(profile_data)
	wants_keyboard_remap = False
	if interactive_setup:
		button_count, screen = _run_secondary_selector(
			"Formato de botones",
			SELECTOR_WINDOW_SIZE,
			lambda secondary: choose_button_format(secondary, profile["button_count"])
		)
		if button_count is None:
			return False
		input_mode = None
		selected_device_path = profile.get("preferred_joystick_path")
		while input_mode is None:
			mode_choice, screen = _run_secondary_selector(
				"Modo de entrada",
				SELECTOR_WINDOW_SIZE,
				lambda secondary: choose_input_mode(secondary, profile["input_mode"])
			)
			if mode_choice is None:
				return False
			if mode_choice in ["teclado", "hitbox"]:
				keyboard_action, screen = _confirm_keyboard_remap_secondary()
				if keyboard_action == "cancelar":
					continue
				select_keyboard_status, screen = _choose_keyboard_device_secondary(profile.get("preferred_keyboard_path"))
				if select_keyboard_status[0] == "cancelar":
					continue
				profile["preferred_keyboard_path"] = select_keyboard_status[1]
				wants_keyboard_remap = keyboard_action == "si"
				input_mode = mode_choice
				break

			diagnostic, screen = _run_secondary_selector(
				"Diagnostico joystick",
				MAPPER_WINDOW_SIZE,
				lambda secondary: run_joystick_diagnostic(
					secondary,
					button_count,
					window_mode=profile_data.get("window_mode", "floating_hint"),
					controller_style=profile.get("controller_style", "default")
				)
			)
			if diagnostic.get("status") == "back_to_input":
				continue
			selected_device_path = diagnostic.get("device_path")
			if diagnostic.get("status") == "mapped":
				profile["joystick_bindings"] = diagnostic.get("bindings", {})
				profile["joystick_bindings_style"] = profile.get("controller_style", "default")
			input_mode = "joystick"
	else:
		button_count = profile.get("button_count", 6)
		input_mode = profile.get("input_mode", "teclado")
		selected_device_path = profile.get("preferred_joystick_path")

	profile["button_count"] = button_count
	profile["input_mode"] = input_mode
	profile["preferred_joystick_path"] = selected_device_path

	labels = get_button_labels(button_count)
	profile["button_icons"] = {label: profile["button_icons"].get(label) for label in labels}
	if profile["key_bindings"] and any(key not in profile["key_bindings"] for key in ["Arriba", "Abajo", "Izquierda", "Derecha"] + labels):
		profile["key_bindings"] = {}
	if profile["joystick_bindings"] and any(label not in profile["joystick_bindings"] for label in labels):
		profile["joystick_bindings"] = {}

	if input_mode in ["teclado", "hitbox"] and wants_keyboard_remap:
		profile["key_bindings"] = {}
	if input_mode in ["teclado", "hitbox"] and not profile["key_bindings"]:
		if not interactive_setup:
			print("[WARN] Perfil sin key_bindings en modo no interactivo.")
			return False
		mapped, screen = _run_secondary_selector(
			"Mapeo teclado",
			MAPPER_WINDOW_SIZE,
			lambda secondary: map_keys(secondary, button_count)
		)
		if mapped:
			profile["key_bindings"] = mapped
	if input_mode == "joystick":
		selected_style = profile.get("controller_style", "default")
		bindings_style = profile.get("joystick_bindings_style")
		if bindings_style != selected_style:
			profile["joystick_bindings"] = {}

	if input_mode == "joystick" and not profile["joystick_bindings"]:
		mapped, screen = _run_secondary_selector(
			"Mapeo joystick",
			MAPPER_WINDOW_SIZE,
			lambda secondary: map_joystick_buttons(
				secondary,
				button_count,
				show_error=False,
				device_path=selected_device_path,
				controller_style=profile.get("controller_style", "default")
			)
		)
		if not mapped:
			return False
		profile["joystick_bindings"] = mapped
		profile["joystick_bindings_style"] = profile.get("controller_style", "default")

	sync_active_profile_to_legacy_files(profile_data)
	save_profiles_data(profile_data)

	input_state = {"stick": [0, 0], "buttons": [False] * len(labels)}
	tournament_mode = bool(force_tournament)
	load_icons(button_count, profile["button_icons"], enable_icons=not tournament_mode)
	set_stick_color(profile["joystick_color"])
	set_stick_colors(
		profile.get("joystick_knob_color", profile["joystick_color"]),
		profile.get("joystick_bar_color", [0, 0, 0]),
		profile.get("joystick_ring_color", [255, 255, 255]),
	)
	set_controller_style(profile.get("controller_style", "default"))
	set_render_mode("tournament" if tournament_mode else "normal")
	set_input_layout("hitbox" if input_mode == "hitbox" else "stick")

	threading.Thread(
		target=start_input_listener,
		args=(input_mode, button_count, input_state, selected_device_path, profile.get("preferred_keyboard_path")),
		daemon=True
	).start()

	clock = pygame.time.Clock()
	running = True
	background_color = get_background_color(profile_data.get("capture_mode", "normal"))
	target_fps = TOURNAMENT_FPS if tournament_mode else FPS
	while running:
		screen.fill(background_color)
		draw_hud(screen, input_state, button_count)
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				running = False
		clock.tick(target_fps)
	return True


def main():
	global _current_window_mode
	pygame.init()
	os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"
	_current_window_mode = "floating_hint"
	screen = _set_window_size(MENU_WIDTH, MENU_HEIGHT, "Arcade HUD Overlay")

	profile_data = load_profiles_data()
	_current_window_mode = profile_data.get("window_mode", "floating_hint")
	set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))
	while True:
		_current_window_mode = profile_data.get("window_mode", "floating_hint")
		set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))
		screen = _set_window_size(MENU_WIDTH, MENU_HEIGHT, "Arcade HUD Overlay")
		action = show_main_menu(screen)
		if action == "salir":
			confirmed, screen = _confirm_exit_secondary()
			if confirmed:
				break
			continue
		if action == "configurar":
			updated, screen = _open_config_secondary_window(profile_data)
			if updated:
				profile_data = updated
				save_profiles_data(profile_data)
				set_ui_font_family(profile_data.get("ui_font_family", "JetBrainsMono"))
			continue
		if action == "iniciar":
			screen = _set_window_size(SCREEN_WIDTH, SCREEN_HEIGHT, "Arcade HUD Overlay")
			run_hud_session(screen, profile_data)
			screen = _set_window_size(MENU_WIDTH, MENU_HEIGHT, "Arcade HUD Overlay")

	pygame.quit()
	sys.exit()

if __name__ == "__main__":
    main()

