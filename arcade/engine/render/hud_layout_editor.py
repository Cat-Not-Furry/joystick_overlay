# render/hud_layout_editor.py
# Editor visual de posicion HUD (stick + cada boton en coords base).

import pygame

from config import (
	SCREEN_WIDTH,
	SCREEN_HEIGHT,
	get_hud_scale,
	get_button_labels,
	get_hud_layout_variant_key,
	normalize_controller_style,
	layout_four_variant_4a_from_profile,
)
from profiles.hud_layout import (
	default_dirs_ref_base,
	default_buttons_ref_base,
	default_system_base_by_label,
	default_direction_centers_base,
	resolve_hud_layout_offsets,
	merge_hud_layout_variant,
	hud_layout_dict_for_editor,
	merged_layout_elements_for_profile,
	_default_button_base_by_label,
	layout_base_coords_from_merged,
)

_DIR_EDIT_ORDER = ("LEFT", "UP", "DOWN", "RIGHT")
from utils import draw_centered_text, build_responsive_font
from core.assets_resolver import resolve_icons_map_from_profile_dict
from render.hud_renderer import (
	draw_hud,
	load_icons,
	load_system_icons,
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
	resolved = resolve_icons_map_from_profile_dict(profile, button_count)
	load_icons(button_count, resolved, enable_icons=True)
	load_system_icons(profile)
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


def _working_hud_layout_dict(
	layout_key, button_count, dirs_xy, button_xy_map, sys_xy_map, dir_xy_map=None
):
	els = {
		"dirs_group": {"x": int(dirs_xy[0]), "y": int(dirs_xy[1])},
		"button_positions": {
			lbl: {"x": int(button_xy_map[lbl][0]), "y": int(button_xy_map[lbl][1])}
			for lbl in button_xy_map
		},
		"system_button_positions": {
			sl: {"x": int(sys_xy_map[sl][0]), "y": int(sys_xy_map[sl][1])}
			for sl in ("SELECT", "START")
		},
	}
	if dir_xy_map:
		els["direction_positions"] = {
			k: {"x": int(dir_xy_map[k][0]), "y": int(dir_xy_map[k][1])}
			for k in _DIR_EDIT_ORDER
		}
	out = {
		"version": 1,
		"base_resolution": [SCREEN_WIDTH, SCREEN_HEIGHT],
		"elements": els,
		"mode_overrides": {},
	}
	if layout_key != "stick":
		out["mode_overrides"][layout_key] = dict(els)
	return out


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


def _init_editor_state(layout_key, button_count, raw_profile_hud, active_profile=None):
	ap = active_profile if isinstance(active_profile, dict) else {}
	ctrl = normalize_controller_style(ap.get("controller_style"))
	four_a = layout_four_variant_4a_from_profile(ap)
	d_def = default_dirs_ref_base(layout_key)
	b_def = default_buttons_ref_base(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	base_by = _default_button_base_by_label(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	dsys = default_system_base_by_label(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	labels = get_button_labels(button_count)
	variant_key = get_hud_layout_variant_key(button_count, four_a)
	pseudo_profile = dict(ap)
	if raw_profile_hud is not None:
		pseudo_profile["hud_layout"] = raw_profile_hud
	merged = merged_layout_elements_for_profile(pseudo_profile, layout_key, variant_key)
	hit_alt_i = bool(ap.get("hitbox_alt_layout", False))
	return layout_base_coords_from_merged(
		merged,
		layout_key,
		labels,
		d_def,
		b_def,
		base_by,
		dsys,
		hit_alt=hit_alt_i,
	)


class _HudEditorSession:
	"""Estado mutable del editor HUD (layout, handles, snap, drag)."""

	def __init__(
		self,
		screen,
		active_profile,
		layout_key,
		button_count,
		variant_key,
		labels,
		d_def,
		base_by,
		dsys_default,
		dirs_xy,
		btn_xy,
		sys_xy,
		dir_xy,
		hit_alt_ed,
	):
		self.screen = screen
		self.active_profile = active_profile
		self.layout_key = layout_key
		self.button_count = button_count
		self.variant_key = variant_key
		self.labels = labels
		self.d_def = d_def
		self.base_by = base_by
		self.dsys_default = dsys_default
		self.dirs_xy = dirs_xy
		self.btn_xy = btn_xy
		self.sys_xy = sys_xy
		self.dir_xy = dir_xy
		self.hit_alt_ed = hit_alt_ed
		self.snap_on = False
		self.snap_grid = 4
		nlab = len(labels)
		n_dir = 4 if layout_key in ("hitbox", "mixbox") else 0
		self.nlab = nlab
		self.n_dir = n_dir
		self.idx_first_btn = 1 + n_dir
		self.idx_sys_select = self.idx_first_btn + nlab
		self.idx_sys_start = self.idx_first_btn + nlab + 1
		self.n_handles = 1 + n_dir + nlab + 2
		self.active_handle = 0
		self.dragging = None
		self.preview_state = {
			"stick": [0.0, 0.0],
			"buttons": [False] * nlab,
			"select": False,
			"start": False,
		}

	def preview_profile(self):
		p = dict(self.active_profile)
		w = _working_hud_layout_dict(
			self.layout_key,
			self.button_count,
			self.dirs_xy,
			self.btn_xy,
			self.sys_xy,
			self.dir_xy if self.layout_key in ("hitbox", "mixbox") else None,
		)
		p["hud_layout"] = merge_hud_layout_variant(
			self.active_profile.get("hud_layout"),
			self.variant_key,
			w.get("elements", {}),
			w.get("mode_overrides", {}),
		)
		return p

	def layout_offsets_for_preview(self):
		return resolve_hud_layout_offsets(
			self.preview_profile(),
			self.screen.get_width(),
			self.screen.get_height(),
			self.layout_key,
			self.button_count,
		)

	def screen_pos(self, scale):
		dsx = int(self.dirs_xy[0] * scale)
		dsy = int(self.dirs_xy[1] * scale)
		btn_screen = {
			lbl: (int(self.btn_xy[lbl][0] * scale), int(self.btn_xy[lbl][1] * scale))
			for lbl in self.labels
		}
		ssel = (
			int(self.sys_xy["SELECT"][0] * scale),
			int(self.sys_xy["SELECT"][1] * scale),
		)
		ssta = (
			int(self.sys_xy["START"][0] * scale),
			int(self.sys_xy["START"][1] * scale),
		)
		r = max(10, int(14 * scale))
		return dsx, dsy, btn_screen, ssel, ssta, r

	def dir_screen(self, dk, scale):
		if self.dir_xy is None:
			return (0, 0)
		x, y = self.dir_xy[dk]
		return (int(x * scale), int(y * scale))


def _apply_arrow_step(session, dx, dy, step):
	ah = session.active_handle
	if ah == 0:
		if session.dir_xy is not None:
			for dk in session.dir_xy:
				session.dir_xy[dk] = (
					session.dir_xy[dk][0] + dx * step,
					session.dir_xy[dk][1] + dy * step,
				)
		session.dirs_xy = (
			session.dirs_xy[0] + dx * step,
			session.dirs_xy[1] + dy * step,
		)
	elif session.n_dir and 1 <= ah <= session.n_dir:
		dk = _DIR_EDIT_ORDER[ah - 1]
		session.dir_xy[dk] = (
			session.dir_xy[dk][0] + dx * step,
			session.dir_xy[dk][1] + dy * step,
		)
	elif session.idx_first_btn <= ah < session.idx_first_btn + session.nlab:
		lb = session.labels[ah - session.idx_first_btn]
		session.btn_xy[lb] = (
			session.btn_xy[lb][0] + dx * step,
			session.btn_xy[lb][1] + dy * step,
		)
	elif ah == session.idx_sys_select:
		session.sys_xy["SELECT"] = (
			session.sys_xy["SELECT"][0] + dx * step,
			session.sys_xy["SELECT"][1] + dy * step,
		)
	elif ah == session.idx_sys_start:
		session.sys_xy["START"] = (
			session.sys_xy["START"][0] + dx * step,
			session.sys_xy["START"][1] + dy * step,
		)


def _clamp_and_snap_all(session):
	session.dirs_xy = _clamp_base(session.dirs_xy)
	for lb in session.labels:
		session.btn_xy[lb] = _clamp_base(session.btn_xy[lb])
	session.sys_xy["SELECT"] = _clamp_base(session.sys_xy["SELECT"])
	session.sys_xy["START"] = _clamp_base(session.sys_xy["START"])
	if session.dir_xy is not None:
		for dk in session.dir_xy:
			session.dir_xy[dk] = _clamp_base(session.dir_xy[dk])
	if not session.snap_on:
		return
	grid = session.snap_grid
	session.dirs_xy = (
		_snap_val(session.dirs_xy[0], grid),
		_snap_val(session.dirs_xy[1], grid),
	)
	for lb in session.labels:
		session.btn_xy[lb] = (
			_snap_val(session.btn_xy[lb][0], grid),
			_snap_val(session.btn_xy[lb][1], grid),
		)
	session.sys_xy["SELECT"] = (
		_snap_val(session.sys_xy["SELECT"][0], grid),
		_snap_val(session.sys_xy["SELECT"][1], grid),
	)
	session.sys_xy["START"] = (
		_snap_val(session.sys_xy["START"][0], grid),
		_snap_val(session.sys_xy["START"][1], grid),
	)
	if session.dir_xy is not None:
		for dk in session.dir_xy:
			session.dir_xy[dk] = (
				_snap_val(session.dir_xy[dk][0], grid),
				_snap_val(session.dir_xy[dk][1], grid),
			)
	session.dirs_xy = _clamp_base(session.dirs_xy)
	for lb in session.labels:
		session.btn_xy[lb] = _clamp_base(session.btn_xy[lb])
	session.sys_xy["SELECT"] = _clamp_base(session.sys_xy["SELECT"])
	session.sys_xy["START"] = _clamp_base(session.sys_xy["START"])
	if session.dir_xy is not None:
		for dk in session.dir_xy:
			session.dir_xy[dk] = _clamp_base(session.dir_xy[dk])


def _reset_editor_positions(session):
	session.dirs_xy = (session.d_def[0], session.d_def[1])
	session.btn_xy = {
		lbl: (session.base_by[lbl][0], session.base_by[lbl][1]) for lbl in session.labels
	}
	session.sys_xy = {
		"SELECT": (
			session.dsys_default["SELECT"][0],
			session.dsys_default["SELECT"][1],
		),
		"START": (
			session.dsys_default["START"][0],
			session.dsys_default["START"][1],
		),
	}
	if session.dir_xy is not None:
		dcb = default_direction_centers_base(
			session.d_def[0],
			session.d_def[1],
			session.layout_key,
			session.hit_alt_ed,
		)
		for dk in _DIR_EDIT_ORDER:
			session.dir_xy[dk] = (dcb[dk][0], dcb[dk][1])


def _persist_editor_layout(session):
	w = _working_hud_layout_dict(
		session.layout_key,
		session.button_count,
		session.dirs_xy,
		session.btn_xy,
		session.sys_xy,
		session.dir_xy if session.layout_key in ("hitbox", "mixbox") else None,
	)
	session.active_profile["hud_layout"] = merge_hud_layout_variant(
		session.active_profile.get("hud_layout"),
		session.variant_key,
		w.get("elements", {}),
		w.get("mode_overrides", {}),
	)


_ARROW_KEYS = (
	(pygame.K_LEFT, -1, 0),
	(pygame.K_RIGHT, 1, 0),
	(pygame.K_UP, 0, -1),
	(pygame.K_DOWN, 0, 1),
)


def _handle_editor_keydown(event, session):
	if event.key == pygame.K_ESCAPE:
		return False
	if event.key == pygame.K_s:
		_persist_editor_layout(session)
		return True
	if event.key == pygame.K_r:
		_reset_editor_positions(session)
		return None
	if event.key == pygame.K_TAB:
		session.active_handle = (session.active_handle + 1) % session.n_handles
		return None
	if event.key == pygame.K_g:
		session.snap_on = not session.snap_on
		return None
	if event.key == pygame.K_1:
		session.snap_grid = 4
		return None
	if event.key == pygame.K_2:
		session.snap_grid = 8
		return None
	step = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
	for key, dx, dy in _ARROW_KEYS:
		if event.key == key:
			_apply_arrow_step(session, dx, dy, step)
			break
	_clamp_and_snap_all(session)
	return None


def _point_in_handle(mx, my, cx, cy, radius):
	return (mx - cx) ** 2 + (my - cy) ** 2 <= radius * radius


def _hit_test_editor_handle(mx, my, session, scale, dsx, dsy, btn_screen, ssel, ssta, r):
	if _point_in_handle(mx, my, dsx, dsy, r):
		return "dirs", 0
	if session.dir_xy is not None:
		for i, dk in enumerate(_DIR_EDIT_ORDER):
			dcx, dcy = session.dir_screen(dk, scale)
			if _point_in_handle(mx, my, dcx, dcy, r):
				return dk, 1 + i
	for i, lb in enumerate(session.labels):
		bx, by = btn_screen[lb]
		if _point_in_handle(mx, my, bx, by, r):
			return lb, session.idx_first_btn + i
	for sl, idx, (sx, sy) in (
		("SELECT", session.idx_sys_select, ssel),
		("START", session.idx_sys_start, ssta),
	):
		if _point_in_handle(mx, my, sx, sy, r):
			return sl, idx
	return None, None


def _apply_editor_drag_motion(session, pos, scale):
	bx, by = _screen_to_base(pos, scale)
	bx, by = _clamp_base((bx, by))
	if session.snap_on:
		bx = _snap_val(bx, session.snap_grid)
		by = _snap_val(by, session.snap_grid)
		bx, by = _clamp_base((bx, by))
	if session.dragging == "dirs":
		if session.dir_xy is not None:
			dax = bx - session.dirs_xy[0]
			day = by - session.dirs_xy[1]
			for dk in session.dir_xy:
				session.dir_xy[dk] = (
					session.dir_xy[dk][0] + dax,
					session.dir_xy[dk][1] + day,
				)
		session.dirs_xy = (bx, by)
	elif session.dragging in session.btn_xy:
		session.btn_xy[session.dragging] = (bx, by)
	elif session.dir_xy is not None and session.dragging in session.dir_xy:
		session.dir_xy[session.dragging] = (bx, by)
	elif session.dragging in session.sys_xy:
		session.sys_xy[session.dragging] = (bx, by)


def _handle_editor_mouse(event, session, scale):
	dsx, dsy, btn_screen, ssel, ssta, r = session.screen_pos(scale)
	if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
		mx, my = event.pos
		drag_key, handle_idx = _hit_test_editor_handle(
			mx, my, session, scale, dsx, dsy, btn_screen, ssel, ssta, r
		)
		if drag_key is not None:
			session.dragging = drag_key
			session.active_handle = handle_idx
	elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
		session.dragging = None
	elif event.type == pygame.MOUSEMOTION and session.dragging:
		_apply_editor_drag_motion(session, event.pos, scale)


def _render_editor_frame(screen, session, scale):
	dsx, dsy, btn_screen, ssel, ssta, r = session.screen_pos(scale)
	lo = session.layout_offsets_for_preview()
	screen.fill((20, 20, 30))
	draw_hud(screen, session.preview_state, session.button_count, layout_offsets=lo)

	pygame.draw.circle(
		screen,
		(0, 200, 255) if session.active_handle == 0 else (100, 100, 120),
		(dsx, dsy),
		r,
		2,
	)
	for i, lb in enumerate(session.labels):
		bx, by = btn_screen[lb]
		pygame.draw.circle(
			screen,
			(255, 180, 0)
			if session.active_handle == session.idx_first_btn + i
			else (100, 100, 120),
			(bx, by),
			r,
			2,
		)
	if session.dir_xy is not None:
		dir_colors = (
			(180, 220, 255),
			(255, 200, 120),
			(200, 255, 180),
			(255, 180, 220),
		)
		for i, dk in enumerate(_DIR_EDIT_ORDER):
			dcx, dcy = session.dir_screen(dk, scale)
			pygame.draw.circle(
				screen,
				dir_colors[i] if session.active_handle == 1 + i else (100, 100, 120),
				(dcx, dcy),
				r,
				2,
			)
	ssel_x, ssel_y = ssel
	ssta_x, ssta_y = ssta
	pygame.draw.circle(
		screen,
		(200, 120, 255) if session.active_handle == session.idx_sys_select else (100, 100, 120),
		(ssel_x, ssel_y),
		r,
		2,
	)
	pygame.draw.circle(
		screen,
		(120, 255, 200) if session.active_handle == session.idx_sys_start else (100, 100, 120),
		(ssta_x, ssta_y),
		r,
		2,
	)
	hud_lines = [
		"Editor posicion HUD",
		"Tab: ancla / (L U D R si hitbox-mixbox) / botones / Sel / St | Flechas | Shift: 10",
		"G: snap | 1: rejilla 4 | 2: rejilla 8",
		"S: guardar | Esc: cancelar | R: restablecer",
		f"Snap: {'on' if session.snap_on else 'off'} ({session.snap_grid}px)",
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


def run_hud_layout_editor(screen, active_profile, window_mode="floating_hint"):
	"""
	Editor de layout HUD. Guarda en active_profile['hud_layout'] con S.
	Tab: ancla direccional, cada tecla L U D R (hitbox/mixbox), botones de accion, Select y Start.
	"""
	button_count = active_profile.get("button_count", 6)
	layout_key = _profile_layout_key(active_profile)
	variant_key = get_hud_layout_variant_key(
		button_count, layout_four_variant_4a_from_profile(active_profile)
	)
	labels = get_button_labels(button_count)
	ctrl = normalize_controller_style(active_profile.get("controller_style"))
	four_a = layout_four_variant_4a_from_profile(active_profile)
	d_def = default_dirs_ref_base(layout_key)
	base_by = _default_button_base_by_label(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	dsys_default = default_system_base_by_label(
		button_count, layout_key, ctrl, layout_four_variant_4a=four_a
	)
	editor_hud = hud_layout_dict_for_editor(
		active_profile.get("hud_layout"), variant_key
	)
	dirs_xy, btn_xy, sys_xy, dir_xy = _init_editor_state(
		layout_key, button_count, editor_hud, active_profile
	)
	session = _HudEditorSession(
		screen,
		active_profile,
		layout_key,
		button_count,
		variant_key,
		labels,
		d_def,
		base_by,
		dsys_default,
		dirs_xy,
		btn_xy,
		sys_xy,
		dir_xy,
		bool(active_profile.get("hitbox_alt_layout", False)),
	)
	_apply_profile_visual(active_profile, button_count)
	clock = pygame.time.Clock()

	while True:
		scale = get_hud_scale(screen.get_width(), screen.get_height())
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				result = _handle_editor_keydown(event, session)
				if result is not None:
					return result
			elif event.type in (
				pygame.MOUSEBUTTONDOWN,
				pygame.MOUSEBUTTONUP,
				pygame.MOUSEMOTION,
			):
				_handle_editor_mouse(event, session, scale)
		_render_editor_frame(screen, session, scale)
		clock.tick(60)
