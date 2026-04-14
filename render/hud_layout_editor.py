# render/hud_layout_editor.py
# Editor visual de posicion HUD (coords base) sobre la misma ventana.

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, get_hud_scale, get_button_labels
from profiles.hud_layout import (
	default_dirs_ref_base,
	default_buttons_ref_base,
	normalize_hud_layout_section,
	resolve_hud_layout_offsets,
)
from utils import draw_centered_text, build_responsive_font
from render.hud_renderer import (
	draw_hud,
	load_icons,
	set_stick_color,
	set_stick_colors,
	set_button_colors,
	set_controller_style,
	set_render_mode,
	set_input_layout,
	set_hitbox_alt_layout,
)


def _profile_layout_key(profile):
	mode = profile.get("input_mode", "teclado")
	if mode == "mixbox":
		return "mixbox"
	if mode == "hitbox":
		return "hitbox"
	return "stick"


def _apply_profile_visual(profile, button_count):
	load_icons(button_count, profile.get("button_icons"), enable_icons=True)
	set_stick_color(profile.get("joystick_color", [0, 255, 0]))
	set_stick_colors(
		profile.get("joystick_knob_color", profile.get("joystick_color", [0, 255, 0])),
		profile.get("joystick_bar_color", [0, 0, 0]),
		profile.get("joystick_ring_color", [255, 255, 255]),
	)
	set_button_colors(
		profile.get("button_color_inactive", [80, 80, 80]),
		profile.get("button_color_active", [255, 0, 0]),
	)
	set_controller_style(profile.get("controller_style", "default"))
	set_render_mode("normal")
	layout = (
		"mixbox"
		if profile.get("input_mode") == "mixbox"
		else ("hitbox" if profile.get("input_mode") == "hitbox" else "stick")
	)
	set_input_layout(layout)
	set_hitbox_alt_layout(profile.get("hitbox_alt_layout", False))


def _working_layout_dict(dirs_xy, buttons_xy):
	return {
		"version": 1,
		"base_resolution": [SCREEN_WIDTH, SCREEN_HEIGHT],
		"elements": {
			"dirs_group": {"x": int(dirs_xy[0]), "y": int(dirs_xy[1])},
			"buttons_group": {"x": int(buttons_xy[0]), "y": int(buttons_xy[1])},
		},
		"mode_overrides": {},
	}


def _screen_to_base(pos, scale):
	return (float(pos[0]) / scale, float(pos[1]) / scale)


def _clamp_base(xy):
	return (
		max(0, min(SCREEN_WIDTH, xy[0])),
		max(0, min(SCREEN_HEIGHT, xy[1])),
	)


def _snap_val(v, grid):
	if grid <= 0:
		return v
	return round(v / grid) * grid


def run_hud_layout_editor(screen, active_profile, window_mode="floating_hint"):
	"""
	Editor de layout HUD. Guarda en active_profile['hud_layout'] con S.
	Retorna True si guardo, False si cancelo.
	"""
	button_count = active_profile.get("button_count", 6)
	layout_key = _profile_layout_key(active_profile)
	d_def = default_dirs_ref_base(layout_key)
	b_def = default_buttons_ref_base(button_count, layout_key)
	raw = active_profile.get("hud_layout")
	norm = normalize_hud_layout_section(raw) if raw is not None else None
	if norm and norm.get("elements"):
		merged = dict(norm.get("elements", {}))
		ov = norm.get("mode_overrides", {}).get(layout_key, {})
		for k, v in ov.items():
			merged[k] = dict(v)
		dg = merged.get("dirs_group", {"x": int(d_def[0]), "y": int(d_def[1])})
		bg = merged.get("buttons_group", {"x": int(b_def[0]), "y": int(b_def[1])})
		dirs_xy = (float(dg["x"]), float(dg["y"]))
		buttons_xy = (float(bg["x"]), float(bg["y"]))
	else:
		dirs_xy = (d_def[0], d_def[1])
		buttons_xy = (b_def[0], b_def[1])

	snap_on = False
	snap_grid = 4
	active_handle = 0
	dragging = None
	clock = pygame.time.Clock()
	nlab = len(get_button_labels(button_count))
	preview_state = {"stick": [0.0, 0.0], "buttons": [False] * nlab}
	_apply_profile_visual(active_profile, button_count)

	def _preview_profile():
		p = dict(active_profile)
		p["hud_layout"] = _working_layout_dict(dirs_xy, buttons_xy)
		return p

	def _layout_offsets_for_preview():
		return resolve_hud_layout_offsets(
			_preview_profile(),
			screen.get_width(),
			screen.get_height(),
			layout_key,
			button_count,
		)

	def _handle_positions_screen(scale):
		dx = int(dirs_xy[0] * scale)
		dy = int(dirs_xy[1] * scale)
		bx = int(buttons_xy[0] * scale)
		by = int(buttons_xy[1] * scale)
		return (dx, dy), (bx, by)

	while True:
		sw, sh = screen.get_width(), screen.get_height()
		scale = get_hud_scale(sw, sh)
		(dsx, dsy), (bsx, bsy) = _handle_positions_screen(scale)
		r = max(10, int(14 * scale))

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return False
				if event.key == pygame.K_s:
					active_profile["hud_layout"] = _working_layout_dict(
						dirs_xy, buttons_xy
					)
					return True
				if event.key == pygame.K_r:
					dirs_xy = (d_def[0], d_def[1])
					buttons_xy = (b_def[0], b_def[1])
				if event.key == pygame.K_TAB:
					active_handle = (active_handle + 1) % 2
				if event.key == pygame.K_g:
					snap_on = not snap_on
				if event.key == pygame.K_1:
					snap_grid = 4
				if event.key == pygame.K_2:
					snap_grid = 8
				step = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
				if event.key == pygame.K_LEFT:
					if active_handle == 0:
						dirs_xy = (dirs_xy[0] - step, dirs_xy[1])
					else:
						buttons_xy = (buttons_xy[0] - step, buttons_xy[1])
				elif event.key == pygame.K_RIGHT:
					if active_handle == 0:
						dirs_xy = (dirs_xy[0] + step, dirs_xy[1])
					else:
						buttons_xy = (buttons_xy[0] + step, buttons_xy[1])
				elif event.key == pygame.K_UP:
					if active_handle == 0:
						dirs_xy = (dirs_xy[0], dirs_xy[1] - step)
					else:
						buttons_xy = (buttons_xy[0], buttons_xy[1] - step)
				elif event.key == pygame.K_DOWN:
					if active_handle == 0:
						dirs_xy = (dirs_xy[0], dirs_xy[1] + step)
					else:
						buttons_xy = (buttons_xy[0], buttons_xy[1] + step)
				dirs_xy = _clamp_base(dirs_xy)
				buttons_xy = _clamp_base(buttons_xy)
				if snap_on:
					dirs_xy = (
						_snap_val(dirs_xy[0], snap_grid),
						_snap_val(dirs_xy[1], snap_grid),
					)
					buttons_xy = (
						_snap_val(buttons_xy[0], snap_grid),
						_snap_val(buttons_xy[1], snap_grid),
					)
					dirs_xy = _clamp_base(dirs_xy)
					buttons_xy = _clamp_base(buttons_xy)
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				mx, my = event.pos
				if (mx - dsx) ** 2 + (my - dsy) ** 2 <= r * r:
					dragging = "dirs"
				elif (mx - bsx) ** 2 + (my - bsy) ** 2 <= r * r:
					dragging = "buttons"
			elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				dragging = None
			elif event.type == pygame.MOUSEMOTION and dragging:
				bx, by = _screen_to_base(event.pos, scale)
				bx, by = _clamp_base((bx, by))
				if snap_on:
					bx = _snap_val(bx, snap_grid)
					by = _snap_val(by, snap_grid)
					bx, by = _clamp_base((bx, by))
				if dragging == "dirs":
					dirs_xy = (bx, by)
				else:
					buttons_xy = (bx, by)

		lo = _layout_offsets_for_preview()
		bg = (20, 20, 30)
		screen.fill(bg)
		draw_hud(screen, preview_state, button_count, layout_offsets=lo)

		pygame.draw.circle(
			screen, (0, 200, 255) if active_handle == 0 else (100, 100, 120), (dsx, dsy), r, 2
		)
		pygame.draw.circle(
			screen, (255, 180, 0) if active_handle == 1 else (100, 100, 120), (bsx, bsy), r, 2
		)

		ddr = pygame.Rect(dsx - r, dsy - r, 2 * r, 2 * r)
		bbr = pygame.Rect(bsx - r, bsy - r, 2 * r, 2 * r)
		if ddr.colliderect(bbr):
			pygame.draw.rect(screen, (200, 60, 60), ddr.inflate(8, 8), 2)

		hud_lines = [
			"Editor posicion HUD",
			"Tab: grupo | Flechas: mover | Shift: paso 10",
			"G: snap | 1: rejilla 4 | 2: rejilla 8",
			"S: guardar | Esc: cancelar | R: restablecer",
			f"Snap: {'on' if snap_on else 'off'} ({snap_grid}px)",
		]
		font, line_gap = build_responsive_font(
			screen,
			hud_lines,
			base_size=14,
			min_size=10,
			max_size=18,
			base_resolution=(460, 320),
			max_height_ratio=0.25,
		)
		ly = 6
		for i, line in enumerate(hud_lines):
			draw_centered_text(screen, font, line, y=ly + i * line_gap)

		pygame.display.flip()
		clock.tick(60)
