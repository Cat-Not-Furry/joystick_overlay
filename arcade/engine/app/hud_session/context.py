# context.py — snapshot de input y offsets de layout por frame HUD

from core.input_state_sync import snapshot_input_state
from profiles.hud_layout import resolve_hud_layout_offsets


def hud_layout_key_for_mode(input_mode):
	if input_mode == "mixbox":
		return "mixbox"
	if input_mode == "hitbox":
		return "hitbox"
	return "stick"


def hud_frame_render_context(screen, input_state, profile, input_mode, button_count):
	"""Snapshot thread-safe + offsets de layout para un frame HUD."""
	input_snap = snapshot_input_state(input_state)
	layout_key = hud_layout_key_for_mode(input_mode)
	layout_off = resolve_hud_layout_offsets(
		profile,
		screen.get_width(),
		screen.get_height(),
		layout_key,
		button_count,
	)
	return input_snap, layout_off


# Aliases privados (compat)
_hud_layout_key_for_mode = hud_layout_key_for_mode
_hud_frame_render_context = hud_frame_render_context
