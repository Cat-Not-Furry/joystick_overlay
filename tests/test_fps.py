#!/usr/bin/env python3
"""
Mide FPS durante una sesión HUD.
Requiere display (X11) o SDL_VIDEODRIVER=dummy para CI.
Uso: SDL_VIDEODRIVER=dummy python tests/test_fps.py
"""

import os
import sys
import threading
import time

# Headless antes de importar pygame
if "SDL_VIDEODRIVER" not in os.environ:
	os.environ["SDL_VIDEODRIVER"] = "dummy"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ENGINE)

DURATION_SEC = 3
MIN_FPS_RATIO = 0.75  # Al menos 75% del FPS objetivo


def _run_hud_loop(screen, profile_data, stop_event, frame_count, target_fps):
	"""Bucle HUD simplificado para medir FPS."""
	import pygame
	from config import FPS, TOURNAMENT_FPS, get_button_labels, get_background_color
	from render import draw_hud, load_icons, load_system_icons, set_stick_color, set_stick_colors, set_button_colors
	from render import set_controller_style, set_render_mode, set_input_layout

	profile = profile_data.get("active_profile")
	profiles = profile_data.get("profiles", [])
	active = next((p for p in profiles if p.get("id") == profile), profiles[0] if profiles else {})
	if not active:
		active = {"button_count": 6, "input_mode": "teclado", "joystick_bindings": {},
			"key_bindings": {}, "joystick_color": [0, 255, 0], "capture_mode": "normal"}

	button_count = active.get("button_count", 6)
	labels = get_button_labels(button_count)
	input_state = {"stick": [0, 0], "buttons": [False] * len(labels), "select": False, "start": False}

	load_icons(button_count, {}, enable_icons=False)
	load_system_icons(active)
	set_stick_color(active.get("joystick_color", [0, 255, 0]))
	set_stick_colors(
		active.get("joystick_knob_color", active.get("joystick_color", [0, 255, 0])),
		[0, 0, 0], [255, 255, 255]
	)
	set_button_colors(
		active.get("button_color_inactive", [80, 80, 80]),
		active.get("button_color_active", [255, 0, 0]),
	)
	set_controller_style("default")
	set_render_mode("normal")
	set_input_layout("stick")

	tournament_mode = False
	target_fps[0] = TOURNAMENT_FPS if tournament_mode else FPS
	clock = pygame.time.Clock()
	bg = get_background_color(active.get("capture_mode", "normal"))

	while not stop_event.is_set():
		screen.fill(bg)
		draw_hud(screen, input_state, button_count)
		pygame.display.flip()
		frame_count[0] += 1
		clock.tick(target_fps[0])


def main():
	import pygame
	from config import FPS, SCREEN_WIDTH, SCREEN_HEIGHT

	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
	profile_data = {
		"active_profile": "default",
		"profiles": [{
			"id": "default",
			"button_count": 6,
			"input_mode": "teclado",
			"joystick_bindings": {},
			"key_bindings": {},
			"joystick_color": [0, 255, 0],
			"button_icons": {},
			"capture_mode": "normal",
		}],
	}

	stop_event = threading.Event()
	frame_count = [0]
	target_fps = [FPS]

	thread = threading.Thread(
		target=_run_hud_loop,
		args=(screen, profile_data, stop_event, frame_count, target_fps),
		daemon=True,
	)
	thread.start()
	time.sleep(DURATION_SEC)
	stop_event.set()
	thread.join(timeout=2)

	actual_fps = frame_count[0] / DURATION_SEC
	expected = target_fps[0]
	min_acceptable = expected * MIN_FPS_RATIO

	print("FPS medidos: {:.1f} (objetivo: {}, mínimo aceptable: {:.0f})".format(
		actual_fps, expected, min_acceptable
	))
	if actual_fps < min_acceptable:
		print("FALLO: FPS por debajo del mínimo.")
		sys.exit(1)
	print("OK: FPS dentro del rango esperado.")
	sys.exit(0)


if __name__ == "__main__":
	main()
