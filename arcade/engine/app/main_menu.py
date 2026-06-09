# main_menu.py — menú principal (Iniciar / Configuración / Salir)

import os
import time

import pygame

from app.debug_menu import (
	debug_count_set_mode,
	debug_count_videoresize,
	debug_menu,
	debug_report_videoresize_stats,
)
from app.secondary_flows import launch_easteregg_instance
from config import (
	WINDOW_CAPTION_APP,
	MIN_WINDOW_WIDTH,
	MIN_WINDOW_HEIGHT,
	VIDEORESIZE_COOLDOWN_MS,
	VIDEORESIZE_TOLERANCE_PX,
	EASTEREGG_ENABLE_MULTI_INSTANCE,
	EASTEREGG_MULTI_INSTANCE_KEY,
)
from core.state_manager import BaseState, StateManager
from utils import (
	draw_centered_text,
	build_responsive_font,
	track_set_mode,
	get_last_set_mode_time_ms,
	MenuArrowRepeater,
)

_MAIN_MENU_ACTION_BY_INDEX = ["iniciar", "configurar", "salir"]


def handle_main_menu_key(event, selected, options_len, repeater=None):
	key = event.key
	if repeater is not None and event.type == pygame.KEYDOWN:
		if key not in (
			pygame.K_UP,
			pygame.K_DOWN,
			pygame.K_LEFT,
			pygame.K_RIGHT,
		):
			repeater.reset()
	if repeater is not None:
		if key in (
			pygame.K_UP,
			pygame.K_DOWN,
			pygame.K_LEFT,
			pygame.K_RIGHT,
		):
			d = repeater.consume_keydown(event)
			if d is not None:
				return (selected + d) % options_len, None
			return selected, None
	if key in (pygame.K_UP, pygame.K_LEFT):
		return (selected - 1) % options_len, None
	if key in (pygame.K_DOWN, pygame.K_RIGHT):
		return (selected + 1) % options_len, None
	if key == pygame.K_ESCAPE:
		return selected, "salir"
	if (
		not getattr(event, "repeat", False)
		and key == pygame.K_EQUALS
		and selected == 0
		and EASTEREGG_MULTI_INSTANCE_KEY == "equals"
	):
		launch_easteregg_instance()
		return selected, None
	if key == pygame.K_RETURN:
		action = _MAIN_MENU_ACTION_BY_INDEX[min(selected, len(_MAIN_MENU_ACTION_BY_INDEX) - 1)]
		return selected, action
	return selected, None


def draw_main_menu(screen, options, selected):
	debug_menu("_draw_main_menu")
	lines = (
		[WINDOW_CAPTION_APP]
		+ options
		+ ["Flechas + Enter"]
		+ ["= en Iniciar HUD: nueva instancia"]
	)
	font, line_gap = build_responsive_font(
		screen,
		lines,
		base_size=30,
		min_size=14,
		max_size=36,
		base_resolution=(screen.get_width(), screen.get_height()),
		max_height_ratio=0.88,
	)
	screen.fill((0, 0, 0))
	title_y = max(28, line_gap)
	base_y = title_y + line_gap
	for index, option in enumerate(options):
		prefix = ">" if index == selected else " "
		draw_centered_text(
			screen, font, f"{prefix} {option}", y=base_y + index * line_gap
		)
	draw_centered_text(screen, font, WINDOW_CAPTION_APP, y=title_y)
	draw_centered_text(
		screen, font, "Flechas + Enter", y=base_y + len(options) * line_gap
	)
	if selected == 0 and EASTEREGG_ENABLE_MULTI_INSTANCE:
		draw_centered_text(
			screen,
			font,
			"=: instancia extra",
			y=screen.get_height() - max(18, line_gap),
		)
	pygame.display.flip()


def process_main_menu_event(event, selected, len_options, ignore_videoresize, repeater=None):
	debug_menu(
		f"evento {pygame.event.event_name(event.type) if hasattr(pygame.event, 'event_name') else event.type} ({getattr(event, 'w', '')}x{getattr(event, 'h', '')})"
	)
	if event.type == pygame.QUIT:
		debug_menu("main_menu FIN -> salir")
		return selected, "salir", None
	if event.type == pygame.VIDEORESIZE:
		if ignore_videoresize:
			debug_report_videoresize_stats()
			return selected, None, None
		debug_count_videoresize()
		return selected, None, (event.w, event.h)
	if event.type == pygame.KEYDOWN and not getattr(event, "repeat", False):
		new_selected, action = handle_main_menu_key(event, selected, len_options, repeater)
		if action:
			debug_menu(f"main_menu FIN -> {action}")
		return new_selected, action, None
	return selected, None, None


def apply_main_menu_resize(screen, pending_resize, ignore_videoresize):
	if pending_resize is None or ignore_videoresize:
		return screen
	now_ms = time.time() * 1000
	if now_ms - get_last_set_mode_time_ms() < VIDEORESIZE_COOLDOWN_MS:
		return screen
	new_w = max(MIN_WINDOW_WIDTH, pending_resize[0])
	new_h = max(MIN_WINDOW_HEIGHT, pending_resize[1])
	cur_w, cur_h = screen.get_size()
	if abs(new_w - cur_w) <= VIDEORESIZE_TOLERANCE_PX and abs(new_h - cur_h) <= VIDEORESIZE_TOLERANCE_PX:
		return screen
	screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
	track_set_mode()
	debug_count_set_mode()
	return screen


def drive_menu_frame(screen, ctx, state_manager, clock, dt=0.016):
	"""Un frame del menú: resize, update, draw, flip y tick."""
	screen = apply_main_menu_resize(
		screen, ctx.pending_menu_resize, ctx.ignore_videoresize_menu()
	)
	debug_report_videoresize_stats()
	state_manager.update(dt)
	state_manager.draw(screen)
	pygame.display.flip()
	time.sleep(0.005)
	clock.tick(60)
	return screen


def drive_menu_loop_until_action(
	screen, profile_data=None, ctx=None, state_manager=None, clock=None
):
	"""Bucle bloqueante hasta acción de menú. Retorna (action, screen)."""
	if ctx is None:
		ctx = AppContext(profile_data)
	elif profile_data is not None:
		ctx.profile_data = profile_data
	if state_manager is None:
		state_manager = StateManager(MainMenuState(), ctx)
	if clock is None:
		clock = pygame.time.Clock()

	debug_menu("run_main_menu_until_action INICIO")
	while ctx.menu_action is None:
		events = pygame.event.get()
		state_manager.handle_events(events)
		if ctx.menu_action is not None:
			break
		screen = drive_menu_frame(screen, ctx, state_manager, clock)

	action = ctx.menu_action
	debug_menu(f"run_main_menu_until_action FIN -> {action}")
	return action, screen


def run_main_menu_until_action(screen, profile_data=None):
	"""Devuelve iniciar | configurar | salir. Usa StateManager internamente."""
	action, _screen = drive_menu_loop_until_action(screen, profile_data=profile_data)
	return action


class AppContext:
	"""Contexto compartido del bucle principal (perfil, resize y acción del menú)."""

	def __init__(self, profile_data):
		self.profile_data = profile_data if profile_data is not None else {}
		self.pending_menu_resize = None
		self.menu_action = None

	def ignore_videoresize_menu(self):
		return (
			os.environ.get("JOYSTICK_IGNORE_VIDEORESIZE") == "1"
			or self.profile_data.get("ignore_videoresize", False)
		)


class MainMenuState(BaseState):
	"""Menú principal (Iniciar / Configuración / Salir) como estado en la misma ventana."""

	def __init__(self):
		self.options = ["Iniciar HUD", "Configuración", "Salir"]
		self.selected = 0
		self._arrow_repeater = MenuArrowRepeater()

	def enter(self, ctx):
		self.selected = 0
		self._arrow_repeater = MenuArrowRepeater()
		debug_menu("MainMenuState enter")

	def handle_events(self, ctx, events):
		ctx.menu_action = None
		ctx.pending_menu_resize = None
		ignore = ctx.ignore_videoresize_menu()
		for event in events:
			new_selected, action, pr = process_main_menu_event(
				event, self.selected, len(self.options), ignore, self._arrow_repeater
			)
			self.selected = new_selected
			if pr is not None:
				ctx.pending_menu_resize = pr
			if action:
				ctx.menu_action = action
		dnav = self._arrow_repeater.tick_held()
		if dnav is not None:
			self.selected = (self.selected + dnav) % len(self.options)
		return None

	def draw(self, ctx, screen):
		draw_main_menu(screen, self.options, self.selected)


# Aliases privados (compat main.py)
_handle_main_menu_key = handle_main_menu_key
_draw_main_menu = draw_main_menu
_process_main_menu_event = process_main_menu_event
_apply_main_menu_resize = apply_main_menu_resize
_drive_menu_frame = drive_menu_frame
_drive_menu_loop = drive_menu_loop_until_action
