# profiles/hud_layout.py
# Normalizacion y resolucion de offsets HUD (coords base + escala).

from copy import deepcopy

from config import (
	SCREEN_WIDTH,
	SCREEN_HEIGHT,
	JOYSTICK_CENTER,
	HITBOX_MIXBOX_DIRECTION_LEFT,
	get_hud_scale,
	get_button_positions,
	get_button_positions_hitbox_mixbox,
)

_SUPPORTED_LAYOUTS = frozenset({"stick", "hitbox", "mixbox"})
_SUPPORTED_ELEMENTS = frozenset({"dirs_group", "buttons_group"})


def _is_num(v):
	return isinstance(v, (int, float))


def _clamp(v, lo, hi):
	return max(lo, min(hi, v))


def _default_base_resolution():
	return [SCREEN_WIDTH, SCREEN_HEIGHT]


def default_dirs_ref_base(input_layout):
	if input_layout in ("hitbox", "mixbox"):
		return (float(HITBOX_MIXBOX_DIRECTION_LEFT), 85.0)
	return (float(JOYSTICK_CENTER[0]), float(JOYSTICK_CENTER[1]))


def default_buttons_ref_base(button_count, input_layout):
	if input_layout in ("hitbox", "mixbox"):
		pts = get_button_positions_hitbox_mixbox(
			button_count, SCREEN_WIDTH, SCREEN_HEIGHT
		)
	else:
		pts = get_button_positions(button_count, SCREEN_WIDTH, SCREEN_HEIGHT)
	if not pts:
		return (195.0, 90.0)
	sx = sum(p[0] for p in pts) / len(pts)
	sy = sum(p[1] for p in pts) / len(pts)
	return (float(sx), float(sy))


def _normalize_point(pt, bw, bh):
	if not isinstance(pt, dict):
		return None
	x, y = pt.get("x"), pt.get("y")
	if not _is_num(x) or not _is_num(y):
		return None
	return {
		"x": int(_clamp(int(x), 0, bw)),
		"y": int(_clamp(int(y), 0, bh)),
	}


def normalize_hud_layout_section(raw):
	"""Normaliza dict hud_layout del perfil. Retorna dict seguro o None."""
	if raw is None:
		return None
	if not isinstance(raw, dict):
		return None
	br = raw.get("base_resolution", _default_base_resolution())
	if (
		not isinstance(br, (list, tuple))
		or len(br) != 2
		or not _is_num(br[0])
		or not _is_num(br[1])
	):
		bw, bh = _default_base_resolution()
	else:
		bw = int(max(1, br[0]))
		bh = int(max(1, br[1]))
	out = {
		"version": int(raw.get("version", 1)),
		"base_resolution": [bw, bh],
		"elements": {},
		"mode_overrides": {},
	}
	els = raw.get("elements", {})
	if isinstance(els, dict):
		for k, pt in els.items():
			if k not in _SUPPORTED_ELEMENTS:
				continue
			n = _normalize_point(pt, bw, bh)
			if n:
				out["elements"][k] = n
	mo = raw.get("mode_overrides", {})
	if isinstance(mo, dict):
		for mode, sub in mo.items():
			if mode not in _SUPPORTED_LAYOUTS or not isinstance(sub, dict):
				continue
			mode_out = {}
			for k, pt in sub.items():
				if k not in _SUPPORTED_ELEMENTS:
					continue
				n = _normalize_point(pt, bw, bh)
				if n:
					mode_out[k] = n
			if mode_out:
				out["mode_overrides"][mode] = mode_out
	return out


def _merged_elements(normalized, input_layout):
	if not normalized:
		return {}
	merged = deepcopy(normalized.get("elements", {}))
	ov = normalized.get("mode_overrides", {}).get(input_layout, {})
	for k, v in ov.items():
		merged[k] = dict(v)
	return merged


def resolve_hud_layout_offsets(profile, screen_w, screen_h, input_layout, button_count):
	"""
	Retorna offsets en pixeles de pantalla para dirs y botones.
	input_layout: stick | hitbox | mixbox
	"""
	if input_layout not in _SUPPORTED_LAYOUTS:
		input_layout = "stick"
	scale = get_hud_scale(screen_w, screen_h)
	d_def = default_dirs_ref_base(input_layout)
	b_def = default_buttons_ref_base(button_count, input_layout)
	dx_off, dy_off = 0, 0
	bx_off, by_off = 0, 0
	raw = None
	if isinstance(profile, dict):
		raw = profile.get("hud_layout")
	norm = normalize_hud_layout_section(raw)
	if norm:
		merged = _merged_elements(norm, input_layout)
		dg = merged.get("dirs_group")
		bg = merged.get("buttons_group")
		if dg:
			dx_off = int((dg["x"] - d_def[0]) * scale)
			dy_off = int((dg["y"] - d_def[1]) * scale)
		if bg:
			bx_off = int((bg["x"] - b_def[0]) * scale)
			by_off = int((bg["y"] - b_def[1]) * scale)
	return {
		"dirs_offset": (dx_off, dy_off),
		"buttons_offset": (bx_off, by_off),
		"scale": scale,
	}
