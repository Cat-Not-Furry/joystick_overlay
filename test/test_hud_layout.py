#!/usr/bin/env python3
"""Tests para profiles.hud_layout (sin pygame display)."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from profiles.hud_layout import (
	normalize_hud_layout_section,
	resolve_hud_layout_offsets,
	default_dirs_ref_base,
	default_buttons_ref_base,
)


def test_no_hud_layout_zero_offsets():
	p = {"name": "x", "button_count": 6}
	r = resolve_hud_layout_offsets(p, 375, 175, "stick", 6)
	assert r["dirs_offset"] == (0, 0)
	assert r["buttons_offset"] == (0, 0)


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


def main():
	test_no_hud_layout_zero_offsets()
	test_global_override()
	test_mode_override_hitbox()
	test_invalid_layout_ignored()
	test_regression_no_override_matches_defaults()
	print("OK: test_hud_layout")


if __name__ == "__main__":
	main()
