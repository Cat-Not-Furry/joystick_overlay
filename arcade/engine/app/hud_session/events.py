# events.py — eventos y resize del bucle HUD

import time

import pygame

from app.debug_menu import debug_count_set_mode, debug_count_videoresize
from app.secondary_flows import launch_easteregg_instance, launch_training_window
from config import (
	EASTEREGG_MULTI_INSTANCE_KEY,
	MIN_WINDOW_HEIGHT,
	MIN_WINDOW_WIDTH,
	VIDEORESIZE_COOLDOWN_MS,
	VIDEORESIZE_TOLERANCE_PX,
)
from core.extensions_runtime import emit_hook
from training import (
	clear_sequence,
	has_sequence,
	sequence_to_dict,
	start_playback,
	start_recording,
	stop_recording,
)
from utils import get_last_set_mode_time_ms, track_set_mode


def handle_hud_return_key(keys, training_state):
	"""Maneja tecla RETURN en HUD: Backspace+Enter lanza training, Enter solo hace playback."""
	if keys[pygame.K_BACKSPACE]:
		if has_sequence(training_state):
			launch_training_window(sequence_to_dict(training_state))
		return
	if training_state["status"] == "recording":
		stop_recording(training_state)
	if has_sequence(training_state):
		start_playback(training_state)


def handle_hud_tab_key(training_state):
	"""Alterna grabacion con TAB."""
	if training_state["status"] == "recording":
		stop_recording(training_state)
	else:
		start_recording(training_state)


def process_hud_keydown(event, keys, training_state):
	"""Procesa KEYDOWN del bucle HUD. Retorna (running, training_state)."""
	key = event.key
	if key == pygame.K_ESCAPE:
		return False, training_state
	if (
		not getattr(event, "repeat", False)
		and key == pygame.K_EQUALS
		and EASTEREGG_MULTI_INSTANCE_KEY == "equals"
	):
		launch_easteregg_instance()
		return True, training_state
	if key == pygame.K_TAB:
		handle_hud_tab_key(training_state)
		return True, training_state
	if key == pygame.K_RETURN:
		handle_hud_return_key(keys, training_state)
		return True, training_state
	if key == pygame.K_BACKSPACE and not keys[pygame.K_RETURN]:
		clear_sequence(training_state)
	return True, training_state


def process_hud_events(events, keys, training_state):
	"""Procesa eventos del bucle HUD. Retorna (running, pending_resize)."""
	running = True
	pending_resize = None
	for event in events:
		emit_hook(
			"hud_events_polled",
			{"type": int(event.type), "name": pygame.event.event_name(event.type)},
		)
		if event.type == pygame.VIDEORESIZE:
			debug_count_videoresize()
			pending_resize = (event.w, event.h)
		elif event.type == pygame.QUIT:
			running = False
			break
		elif event.type == pygame.KEYDOWN:
			emit_hook(
				"hud_event_keydown",
				{"key": int(event.key), "repeat": bool(getattr(event, "repeat", False))},
			)
			running, training_state = process_hud_keydown(event, keys, training_state)
			if not running:
				break
	return running, pending_resize


def apply_hud_resize(screen, pending_resize, ignore_videoresize):
	"""Aplica resize de ventana si corresponde. Retorna la pantalla (posiblemente nueva)."""
	if pending_resize is None or ignore_videoresize:
		return screen
	now_ms = time.time() * 1000
	if now_ms - get_last_set_mode_time_ms() < VIDEORESIZE_COOLDOWN_MS:
		return screen
	new_w = max(MIN_WINDOW_WIDTH, pending_resize[0])
	new_h = max(MIN_WINDOW_HEIGHT, pending_resize[1])
	cur_w, cur_h = screen.get_size()
	if (
		abs(new_w - cur_w) <= VIDEORESIZE_TOLERANCE_PX
		and abs(new_h - cur_h) <= VIDEORESIZE_TOLERANCE_PX
	):
		return screen
	screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
	track_set_mode()
	debug_count_set_mode()
	return screen


# Aliases privados (compat)
_handle_hud_return_key = handle_hud_return_key
_handle_hud_tab_key = handle_hud_tab_key
_process_hud_keydown = process_hud_keydown
_process_hud_events = process_hud_events
_apply_hud_resize = apply_hud_resize
