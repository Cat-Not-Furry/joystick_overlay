#!/usr/bin/env python3
"""Tests para profiles.hud_layout (sin pygame display)."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ENGINE)

from config import get_button_positions, get_button_labels
from profiles.hud_layout import (
	normalize_hud_layout_section,
	resolve_hud_layout_offsets,
	default_dirs_ref_base,
	default_buttons_ref_base,
	default_system_base_by_label,
	compute_direction_centers_screen,
)


def test_no_hud_layout_zero_offsets():
	p = {"name": "x", "button_count": 6}
	r = resolve_hud_layout_offsets(p, 375, 175, "stick", 6)
	assert r["dirs_offset"] == (0, 0)
	assert r["buttons_offset"] == (0, 0)
	assert len(r["button_pixel_offsets"]) == 6
	assert r["button_pixel_offsets"] == [(0, 0)] * 6
	assert r["system_offset"] == (0, 0)
	assert r["system_button_pixel_offsets"] == [(0, 0), (0, 0)]
	assert r["direction_button_pixel_offsets"] == {}


def test_global_override():
	p = {
		"hud_layout": {
			"version": 1,
			"base_resolution": [375, 175],
			"elements": {
				"dirs_group": {"x": 75, "y": 85},
				"buttons_group": {"x": 200, "y": 90},
			},
		},
		"button_count": 6,
	}
	ddef = default_dirs_ref_base("stick")
	bdef = default_buttons_ref_base(6, "stick")
	r = resolve_hud_layout_offsets(p, 375, 175, "stick", 6)
	assert r["dirs_offset"] == (0, 0)
	dx = int((200 - bdef[0]))
	assert r["buttons_offset"][0] == dx


def test_mode_override_hitbox():
	p = {
		"hud_layout": {
			"elements": {"dirs_group": {"x": 50, "y": 85}},
			"mode_overrides": {
				"hitbox": {"dirs_group": {"x": 45, "y": 90}},
			},
		},
		"button_count": 4,
	}
	ddef = default_dirs_ref_base("hitbox")
	r = resolve_hud_layout_offsets(p, 375, 175, "hitbox", 4)
	ex = int((45 - ddef[0]))
	ey = int((90 - ddef[1]))
	assert r["dirs_offset"] == (ex, ey)


def test_invalid_layout_ignored():
	p = {"hud_layout": "bad", "button_count": 6}
	n = normalize_hud_layout_section("bad")
	assert n is None
	r = resolve_hud_layout_offsets(p, 375, 175, "stick", 6)
	assert r["dirs_offset"] == (0, 0)


def test_regression_no_override_matches_defaults():
	p = {"button_count": 6}
	r = resolve_hud_layout_offsets(p, 375, 175, "stick", 6)
	assert r["dirs_offset"] == (0, 0) and r["buttons_offset"] == (0, 0)
	r2 = resolve_hud_layout_offsets(p, 750, 350, "hitbox", 4)
	assert r2["scale"] == 2.0


def test_mvs_eight_stick_matches_neo_geo_grid():
	"""MVS 8: misma geometría 2x4 que otros estilos; rejilla A C AC AB / B D BD CD."""
	labels = get_button_labels(8)
	assert labels == ["LP", "MP", "HP", "TR", "LK", "MK", "HK", "BR"]
	arc = get_button_positions(8, controller_style="default")
	mvs = get_button_positions(8, controller_style="mvs")
	assert mvs[0] == arc[0]
	assert mvs[1] == arc[4]
	assert mvs[2] == arc[1]
	assert mvs[3] == arc[5]
	assert mvs[4] == arc[3]
	assert mvs[5] == arc[2]
	assert mvs[6] == arc[6]
	assert mvs[7] == arc[7]


def test_system_select_offset_in_base():
	ds = default_system_base_by_label(6, "stick")
	sx = int(ds["SELECT"][0]) + 12
	sy = int(ds["SELECT"][1])
	p = {
		"button_count": 6,
		"hud_layout": {
			"version": 1,
			"base_resolution": [375, 175],
			"elements": {
				"system_button_positions": {"SELECT": {"x": sx, "y": sy}},
			},
		},
	}
	r = resolve_hud_layout_offsets(p, 375, 175, "stick", 6)
	assert r["system_button_pixel_offsets"][0] == (12, 0)
	assert r["system_button_pixel_offsets"][1] == (0, 0)


def test_hitbox_direction_left_pixel_offset():
	dl = compute_direction_centers_screen(375, 175, "hitbox", False, (0, 0))["LEFT"]
	p = {
		"button_count": 4,
		"hud_layout": {
			"mode_overrides": {
				"hitbox": {
					"direction_positions": {
						"LEFT": {"x": int(dl[0]) + 7, "y": int(dl[1])},
					},
				},
			},
		},
	}
	r = resolve_hud_layout_offsets(p, 375, 175, "hitbox", 4)
	assert r["direction_button_pixel_offsets"]["LEFT"] == (7, 0)
	assert r["direction_button_pixel_offsets"]["UP"] == (0, 0)


def test_hud_variant_formato_6_overrides_root():
	p = {
		"button_count": 6,
		"hud_layout": {
			"elements": {"dirs_group": {"x": 10, "y": 85}},
			"variants": {
				"formato_6": {
					"elements": {"dirs_group": {"x": 50, "y": 85}},
				},
			},
		},
	}
	r = resolve_hud_layout_offsets(p, 375, 175, "stick", 6)
	ddef = default_dirs_ref_base("stick")
	ex = int(50 - ddef[0])
	assert r["dirs_offset"] == (ex, 0)


def test_hud_legacy_root_when_variant_absent():
	p = {
		"button_count": 6,
		"hud_layout": {
			"elements": {"dirs_group": {"x": 33, "y": 85}},
			"variants": {
				"formato_4": {"elements": {"dirs_group": {"x": 99, "y": 85}}},
			},
		},
	}
	r = resolve_hud_layout_offsets(p, 375, 175, "stick", 6)
	ddef = default_dirs_ref_base("stick")
	ex = int(33 - ddef[0])
	assert r["dirs_offset"] == (ex, 0)


def test_hud_layout_4a_uses_variant_key():
	ddef = default_dirs_ref_base("stick")
	p = {
		"button_count": 4,
		"layout_four_variant_4a": True,
		"hud_layout": {
			"variants": {
				"formato_4": {"elements": {"dirs_group": {"x": 10, "y": 85}}},
				"formato_4a": {"elements": {"dirs_group": {"x": 60, "y": 85}}},
			},
		},
	}
	r = resolve_hud_layout_offsets(p, 375, 175, "stick", 4)
	assert r["dirs_offset"] == (int(60 - ddef[0]), 0)
	p2 = dict(p)
	p2["layout_four_variant_4a"] = False
	r2 = resolve_hud_layout_offsets(p2, 375, 175, "stick", 4)
	assert r2["dirs_offset"] == (int(10 - ddef[0]), 0)


def main():
	test_no_hud_layout_zero_offsets()
	test_global_override()
	test_mode_override_hitbox()
	test_invalid_layout_ignored()
	test_regression_no_override_matches_defaults()
	test_mvs_eight_stick_matches_neo_geo_grid()
	test_system_select_offset_in_base()
	test_hitbox_direction_left_pixel_offset()
	test_hud_variant_formato_6_overrides_root()
	test_hud_legacy_root_when_variant_absent()
	test_hud_layout_4a_uses_variant_key()
	print("OK: test_hud_layout")


if __name__ == "__main__":
	main()
