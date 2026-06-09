# secondary_flows.py — selectores y ventanas secundarias en la misma superficie

import json
import os
import subprocess
import sys
import tempfile

import pygame

from app.constants import CONFIRM_WINDOW_SIZE, SELECTOR_WINDOW_SIZE
from app.debug_menu import debug_menu
from config import (
	FPS,
	EASTEREGG_ENABLE_MULTI_INSTANCE,
	EASTEREGG_MAX_INSTANCES,
)
from utils import (
	draw_centered_text,
	build_responsive_font,
	fit_text_to_width,
	list_keyboard_devices_by_capabilities,
	track_set_mode,
	MenuArrowRepeater,
)


def _repo_root():
	return os.path.dirname(
		os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	)


def set_window_size(width, height, title):
	debug_menu(f"_set_window_size({width}x{height})")
	screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
	pygame.display.set_caption(title)
	track_set_mode()
	return screen


def count_running_overlay_instances():
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
		if "python" in cmdline and "main.py" in cmdline:
			count += 1
	return count


def launch_training_window(sequence_data):
	"""Lanza ventana de entrenamiento independiente con la secuencia."""
	fd, path = tempfile.mkstemp(suffix=".json", prefix="joystick_training_")
	root = _repo_root()
	try:
		with os.fdopen(fd, "w") as f:
			json.dump(sequence_data, f, indent=2)
		standalone_path = os.path.join(root, "arcade", "engine", "training", "standalone.py")
		subprocess.Popen(
			[sys.executable, standalone_path, path],
			cwd=root,
			start_new_session=True,
		)
	except Exception as err:
		print(f"[WARN] No se pudo abrir ventana de entrenamiento: {err}")
		try:
			os.unlink(path)
		except Exception:
			pass


def launch_easteregg_instance():
	if not EASTEREGG_ENABLE_MULTI_INSTANCE:
		return False
	if count_running_overlay_instances() + 1 >= EASTEREGG_MAX_INSTANCES:
		print(f"[WARN] Limite de instancias alcanzado ({EASTEREGG_MAX_INSTANCES}).")
		return False

	main_path = os.path.join(_repo_root(), "main.py")
	try:
		subprocess.Popen(
			[sys.executable, main_path],
			cwd=_repo_root(),
			start_new_session=True,
		)
		print("[INFO] Easteregg activado: nueva instancia iniciada.")
		return True
	except Exception as error:
		print(f"[WARN] No se pudo abrir una nueva instancia: {error}")
		return False


def run_secondary_selector(screen, title, size, runner):
	"""Ejecuta selector en la misma superficie (sin cambiar set_mode)."""
	result = runner(screen)
	return result, screen


def select_profile_secondary(profile_data, screen, title="Selecciona perfil"):
	def _runner(screen):
		clock = pygame.time.Clock()
		profiles = profile_data["profiles"]
		selected = 0
		for index, profile in enumerate(profiles):
			if profile["id"] == profile_data.get("active_profile"):
				selected = index
				break

		repeater = MenuArrowRepeater()
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
				draw_centered_text(
					screen,
					font,
					f"{prefix} {profile['name']}",
					y=start_y + visible_index * line_gap,
				)
			draw_centered_text(
				screen,
				font,
				"Flechas + Enter | Esc",
				y=screen.get_height() - max(20, line_gap),
			)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN:
					if event.key in (
						pygame.K_UP,
						pygame.K_DOWN,
						pygame.K_LEFT,
						pygame.K_RIGHT,
					):
						dnav = repeater.consume_keydown(event)
						if dnav is not None:
							selected = (selected + dnav) % len(profiles)
					else:
						repeater.reset()
						if event.key == pygame.K_ESCAPE:
							return None
						elif event.key == pygame.K_RETURN:
							return profiles[selected]["id"]
			d2 = repeater.tick_held()
			if d2 is not None:
				selected = (selected + d2) % len(profiles)
			clock.tick(FPS)

	selected_id, screen = run_secondary_selector(
		screen, title, SELECTOR_WINDOW_SIZE, _runner
	)
	return selected_id, screen


def confirm_exit_secondary(screen):
	def _runner(screen):
		clock = pygame.time.Clock()
		selected = 1
		options = ["No", "Si"]
		repeater = MenuArrowRepeater()
		while True:
			render_lines = (
				["Confirmar salida", "Deseas cerrar el HUD?"]
				+ options
				+ ["Flechas + Enter | Esc"]
			)
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
			draw_centered_text(
				screen, font, "Deseas cerrar el HUD?", y=title_y + line_gap
			)
			for index, option in enumerate(options):
				prefix = ">" if index == selected else " "
				draw_centered_text(
					screen,
					font,
					f"{prefix} {option}",
					y=title_y + line_gap * (3 + index),
				)
			draw_centered_text(
				screen,
				font,
				"Flechas + Enter | Esc",
				y=screen.get_height() - max(20, line_gap),
			)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return False
				if event.type == pygame.KEYDOWN:
					if event.key in (
						pygame.K_UP,
						pygame.K_DOWN,
						pygame.K_LEFT,
						pygame.K_RIGHT,
					):
						dnav = repeater.consume_keydown(event)
						if dnav is not None:
							selected = (selected + dnav) % len(options)
					else:
						repeater.reset()
						if event.key == pygame.K_ESCAPE:
							return False
						elif event.key == pygame.K_RETURN:
							return options[selected] == "Si"
			d2 = repeater.tick_held()
			if d2 is not None:
				selected = (selected + d2) % len(options)
			clock.tick(FPS)

	confirmed, screen = run_secondary_selector(
		screen, "Confirmar salida", CONFIRM_WINDOW_SIZE, _runner
	)
	return confirmed, screen


def confirm_keyboard_remap_secondary(screen):
	def _runner(screen):
		clock = pygame.time.Clock()
		selected = 0
		options = ["No", "Si", "Cancelar y volver"]
		repeater = MenuArrowRepeater()
		while True:
			render_lines = (
				["Modo teclado", "Quieres remapear teclas?"]
				+ options
				+ ["Flechas + Enter | Esc"]
			)
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
			draw_centered_text(
				screen, font, "Quieres remapear teclas?", y=title_y + line_gap
			)
			for index, option in enumerate(options):
				prefix = ">" if index == selected else " "
				draw_centered_text(
					screen,
					font,
					f"{prefix} {option}",
					y=title_y + line_gap * (3 + index),
				)
			draw_centered_text(
				screen,
				font,
				"Flechas + Enter | Esc",
				y=screen.get_height() - max(20, line_gap),
			)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return False
				if event.type == pygame.KEYDOWN:
					if event.key in (
						pygame.K_UP,
						pygame.K_DOWN,
						pygame.K_LEFT,
						pygame.K_RIGHT,
					):
						dnav = repeater.consume_keydown(event)
						if dnav is not None:
							selected = (selected + dnav) % len(options)
					else:
						repeater.reset()
						if event.key == pygame.K_ESCAPE:
							return "cancelar"
						elif event.key == pygame.K_RETURN:
							if options[selected] == "Si":
								return "si"
							if options[selected] == "No":
								return "no"
							return "cancelar"
			d2 = repeater.tick_held()
			if d2 is not None:
				selected = (selected + d2) % len(options)
			clock.tick(FPS)

	confirmed, screen = run_secondary_selector(
		screen, "Remapeo teclado", CONFIRM_WINDOW_SIZE, _runner
	)
	return confirmed, screen


def choose_keyboard_device_secondary(screen, current_path):
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

		repeater = MenuArrowRepeater()
		while True:
			lines_for_fit = (
				["Teclado global (sin foco)"]
				+ [label for label, _ in options[:6]]
				+ ["Flechas + Enter | Esc"]
			)
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
				draw_centered_text(
					screen,
					font,
					f"{prefix} {trimmed}",
					y=start_y + visible_index * line_gap,
				)

			draw_centered_text(
				screen,
				font,
				"Flechas + Enter | Esc",
				y=screen.get_height() - max(20, line_gap),
			)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return "cancelar", current_path
				if event.type == pygame.KEYDOWN:
					if event.key in (
						pygame.K_UP,
						pygame.K_DOWN,
						pygame.K_LEFT,
						pygame.K_RIGHT,
					):
						dnav = repeater.consume_keydown(event)
						if dnav is not None:
							selected = (selected + dnav) % len(options)
					else:
						repeater.reset()
						if event.key == pygame.K_ESCAPE:
							return "cancelar", current_path
						elif event.key == pygame.K_RETURN:
							return "ok", options[selected][1]
			d2 = repeater.tick_held()
			if d2 is not None:
				selected = (selected + d2) % len(options)
			clock.tick(FPS)

	result, screen = run_secondary_selector(
		screen, "Teclado global", SELECTOR_WINDOW_SIZE, _runner
	)
	return result, screen


# Aliases privados (compat main.py)
_set_window_size = set_window_size
_count_running_overlay_instances = count_running_overlay_instances
_launch_training_window = launch_training_window
_launch_easteregg_instance = launch_easteregg_instance
_run_secondary_selector = run_secondary_selector
_confirm_exit_secondary = confirm_exit_secondary
_confirm_keyboard_remap_secondary = confirm_keyboard_remap_secondary
_choose_keyboard_device_secondary = choose_keyboard_device_secondary
