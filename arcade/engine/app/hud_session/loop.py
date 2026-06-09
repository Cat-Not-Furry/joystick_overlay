# loop.py — bucle principal HUD (render, input listener, training)

import os
import threading
import time

import pygame

from app.debug_menu import debug_report_videoresize_stats
from app.hud_session.context import hud_frame_render_context
from app.hud_session.events import apply_hud_resize, process_hud_events
from config import FPS, TOURNAMENT_FPS, get_background_color, get_button_labels
from core.assets_resolver import resolve_icons_map
from core.extensions_runtime import emit_hook
from core.input_history import InputHistory
from maps import start_input_listener
from render import (
	draw_hud,
	load_icons,
	load_system_icons,
	set_button_colors,
	set_controller_style,
	set_hitbox_alt_layout,
	set_input_layout,
	set_render_mode,
	set_stick_color,
	set_stick_colors,
)
from training import (
	create_training_state,
	snapshot_if_recording,
	update_playback,
)


def run_hud_main_loop(
	screen,
	input_state,
	button_count,
	profile_data,
	input_mode,
	selected_device_path,
	profile,
	force_tournament,
):
	labels = get_button_labels(button_count)
	tournament_mode = bool(force_tournament)
	resolved_icons = resolve_icons_map(profile["id"], button_count)
	load_icons(button_count, resolved_icons, enable_icons=not tournament_mode)
	load_system_icons(profile)
	set_stick_color(profile["joystick_color"])
	set_stick_colors(
		profile.get("joystick_knob_color", profile["joystick_color"]),
		profile.get("joystick_bar_color", [0, 0, 0]),
		profile.get("joystick_ring_color", [255, 255, 255]),
	)
	set_button_colors(
		profile.get("button_color_inactive", [80, 80, 80]),
		profile.get("button_color_active", [255, 0, 0]),
	)
	set_controller_style(profile.get("controller_style", "default"))
	set_render_mode("tournament" if tournament_mode else "normal")
	layout = (
		"mixbox"
		if input_mode == "mixbox"
		else ("hitbox" if input_mode == "hitbox" else "stick")
	)
	set_input_layout(layout)
	set_hitbox_alt_layout(profile.get("hitbox_alt_layout", False))
	history_cfg = profile_data.get("extensions", {})
	history_max_events = history_cfg.get("input_history_max_events", 1000)
	input_history = InputHistory(max_events=history_max_events)

	def _on_input_state_update(source, state_snapshot):
		changes = input_history.record_snapshot(
			state_snapshot,
			source=source,
			player_id="p1",
		)
		if not changes:
			return
		for change in changes:
			emit_hook("input_state_updated", {"change": change})

	emit_hook(
		"session_start",
		{
			"button_count": button_count,
			"input_mode": input_mode,
			"tournament_mode": bool(tournament_mode),
		},
	)
	threading.Thread(
		target=start_input_listener,
		args=(
			input_mode,
			button_count,
			input_state,
			selected_device_path,
			profile.get("preferred_keyboard_path"),
			_on_input_state_update,
			bool(profile.get("layout_four_variant_4a")),
		),
		daemon=True,
	).start()
	clock = pygame.time.Clock()
	running = True
	bg = get_background_color(profile_data.get("capture_mode", "normal"))
	target_fps = TOURNAMENT_FPS if tournament_mode else FPS
	training_state = create_training_state()
	ignore_videoresize = (
		os.environ.get("JOYSTICK_IGNORE_VIDEORESIZE") == "1"
		or profile_data.get("ignore_videoresize", False)
	)
	while running:
		keys = pygame.key.get_pressed()
		events = pygame.event.get()
		running, pending_resize = process_hud_events(events, keys, training_state)
		input_snap, layout_off = hud_frame_render_context(
			screen, input_state, profile, input_mode, button_count
		)
		snapshot_if_recording(training_state, input_snap)
		if training_state["status"] == "playing":
			update_playback(training_state, input_snap)
		screen.fill(bg)
		emit_hook(
			"hud_frame_pre_render",
			{
				"input_state_snapshot": input_snap,
				"layout_offsets": layout_off,
			},
		)
		draw_hud(screen, input_snap, button_count, layout_offsets=layout_off)
		emit_hook(
			"hud_frame_post_render",
			{"fps_target": target_fps, "history_size": len(input_history.events)},
		)
		pygame.display.flip()
		screen = apply_hud_resize(screen, pending_resize, ignore_videoresize)
		debug_report_videoresize_stats()
		time.sleep(0.005)
		clock.tick(target_fps)
	emit_hook(
		"session_end",
		{
			"button_count": button_count,
			"input_mode": input_mode,
			"history": input_history.to_dict(),
		},
	)


# Aliases privados (compat)
_run_hud_main_loop = run_hud_main_loop
