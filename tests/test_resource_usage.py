#!/usr/bin/env python3
"""
Mide uso de CPU y memoria durante una ejecución corta del HUD.
Requiere: pip install psutil
Uso: SDL_VIDEODRIVER=dummy python tests/test_resource_usage.py
"""

import os
import sys
import threading
import time

if "SDL_VIDEODRIVER" not in os.environ:
	os.environ["SDL_VIDEODRIVER"] = "dummy"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ENGINE)

DURATION_SEC = 5
MAX_MEMORY_MB = 200
MAX_CPU_PERCENT = 95


def _run_hud_loop(screen, profile_data, stop_event):
	"""Bucle HUD simplificado."""
	import pygame
	from config import FPS, get_button_labels, get_background_color
	from render import draw_hud, load_icons, load_system_icons, set_stick_color, set_stick_colors, set_button_colors
	from render import set_controller_style, set_render_mode, set_input_layout

	profile = profile_data.get("active_profile")
	profiles = profile_data.get("profiles", [])
	active = next((p for p in profiles if p.get("id") == profile), profiles[0] if profiles else {})
	if not active:
		active = {"button_count": 6, "joystick_color": [0, 255, 0], "capture_mode": "normal"}

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

	clock = pygame.time.Clock()
	bg = get_background_color(active.get("capture_mode", "normal"))

	while not stop_event.is_set():
		screen.fill(bg)
		draw_hud(screen, input_state, button_count)
		pygame.display.flip()
		clock.tick(FPS)


def main():
	try:
		import psutil
	except ImportError:
		print("Instala psutil: pip install psutil==6.1.0")
		sys.exit(2)

	import pygame
	from config import FPS, SCREEN_WIDTH, SCREEN_HEIGHT

	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
	profile_data = {
		"active_profile": "default",
		"profiles": [{
			"id": "default",
			"button_count": 6,
			"joystick_color": [0, 255, 0],
			"button_icons": {},
			"capture_mode": "normal",
		}],
	}

	stop_event = threading.Event()
	thread = threading.Thread(
		target=_run_hud_loop,
		args=(screen, profile_data, stop_event),
		daemon=True,
	)
	thread.start()

	process = psutil.Process()
	memory_samples = []
	cpu_samples = []

	for _ in range(DURATION_SEC * 2):
		memory_samples.append(process.memory_info().rss / (1024 * 1024))
		cpu_samples.append(process.cpu_percent(interval=0.5))
		if stop_event.is_set():
			break

	stop_event.set()
	thread.join(timeout=2)

	memory_mb = memory_samples[-1] if memory_samples else 0
	cpu_avg = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0

	print("Memoria: {:.1f} MB  |  CPU promedio: {:.1f}%".format(memory_mb, cpu_avg))
	print("Umbral memoria: {} MB  |  Umbral CPU: {}%".format(MAX_MEMORY_MB, MAX_CPU_PERCENT))

	failed = False
	if memory_mb > MAX_MEMORY_MB:
		print("FALLO: memoria ({:.1f} MB) excede {} MB.".format(memory_mb, MAX_MEMORY_MB))
		failed = True
	if cpu_avg > MAX_CPU_PERCENT:
		print("FALLO: CPU ({:.1f}%) excede {}%.".format(cpu_avg, MAX_CPU_PERCENT))
		failed = True

	if failed:
		sys.exit(1)
	print("OK: uso de recursos dentro de umbrales.")
	sys.exit(0)


if __name__ == "__main__":
	main()
