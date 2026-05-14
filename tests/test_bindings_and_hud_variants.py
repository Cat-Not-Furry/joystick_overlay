#!/usr/bin/env python3
"""
Tests de claves de formato (bindings/HUD) — no requieren pytest.

Checklist manual (ejecutar tú: app + flujos reales):
- Perfil con formatos 4 / 6 / 8: teclado, hitbox, mixbox: mapear y verificar que legacy_bindings refleja solo el slice activo.
- Variante 4A: alternar layout_four_variant_4a y comprobar teclas/HUD distintos (formato_4 vs formato_4a).
- Joystick: mapeo vacío pide remap; tras mapear, sync a legacy_joystick_bindings antes de sesión.
- Editor HUD: guardar en un formato, cambiar button_count/4A y comprobar que el otro formato conserva posiciones.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ENGINE)

from config import get_active_bindings_format_key, get_hud_layout_variant_key
from profiles.hud_layout import (
	merge_hud_layout_variant,
	normalize_hud_layout_section,
	effective_hud_layout_elements_for_variant,
)


def test_active_format_key_4a():
	assert get_active_bindings_format_key(button_count=4, layout_four_variant_4a=True) == "formato_4a"
	assert get_active_bindings_format_key(button_count=4, layout_four_variant_4a=False) == "formato_4"
	assert get_active_bindings_format_key(button_count=6, layout_four_variant_4a=True) == "formato_6"


def test_hud_variant_key_aligns_with_bindings():
	assert get_hud_layout_variant_key(4, True) == "formato_4a"
	assert get_hud_layout_variant_key(8, False) == "formato_8"


def test_merge_hud_variant_roundtrip():
	base = {"version": 1, "base_resolution": [375, 175], "elements": {}, "mode_overrides": {}}
	merged = merge_hud_layout_variant(
		base,
		"formato_6",
		{"dirs_group": {"x": 40, "y": 85}},
		{},
	)
	n = normalize_hud_layout_section(merged)
	assert n is not None
	eff = effective_hud_layout_elements_for_variant(n, "formato_6")
	assert eff["elements"]["dirs_group"]["x"] == 40


def main():
	test_active_format_key_4a()
	test_hud_variant_key_aligns_with_bindings()
	test_merge_hud_variant_roundtrip()
	print("OK: test_bindings_and_hud_variants")


if __name__ == "__main__":
	main()
