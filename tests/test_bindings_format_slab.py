#!/usr/bin/env python3
"""
Contrato formato_* en JSON de bindings (perfil):

- Legado: "formato_6": { "Arriba": int, "LP": int, ... }  (mapa plano)
- Nuevo: "formato_6": {
    "bindings": { ... mismas claves ... },
    "hud_layout": { "elements": {...}, "mode_overrides": {...} },
    "button_icons": { "LP": "ruta/relativa.png", ... }
  }

Checklist manual: exportar ZIP y comprobar carpeta bindings/ con los cuatro JSON.
"""

import json
import os
import sys
import tempfile
import zipfile
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ENGINE)

from profiles.bindings_storage import unpack_format_slab, pack_format_slab, set_slice, get_slice
from config import (
	icon_stem_for_label,
	PROFILE_KEY_BINDINGS_FILENAME,
	PROFILE_HITBOX_BINDINGS_FILENAME,
	PROFILE_MIXBOX_BINDINGS_FILENAME,
	PROFILE_JOYSTICK_BINDINGS_FILENAME,
)


def test_unpack_flat_roundtrip():
	slab = {"Arriba": 1, "LP": 2, "SELECT": None, "START": None}
	b, h, i = unpack_format_slab(slab)
	assert h is None and i == {}
	assert b.get("LP") == 2


def test_pack_nested_roundtrip():
	flat = {"LP": 1, "SELECT": None, "START": None}
	hud = {"elements": {"dirs_group": {"x": 10, "y": 85}}, "mode_overrides": {}}
	icons = {"LP": "icons/x.png"}
	packed = pack_format_slab(flat, hud, icons)
	b, h, i = unpack_format_slab(packed)
	assert b["LP"] == 1
	assert h and h["elements"]["dirs_group"]["x"] == 10
	assert i.get("LP") == "icons/x.png"


def test_set_slice_preserves_hud():
	tree = {}
	tree = set_slice(tree, "formato_6", {"LP": 1})
	tree["formato_6"] = pack_format_slab(
		get_slice(tree, "formato_6"),
		{"elements": {"dirs_group": {"x": 5, "y": 85}}, "mode_overrides": {}},
		{},
	)
	tree = set_slice(tree, "formato_6", {"LP": 2, "MP": 3})
	assert get_slice(tree, "formato_6")["LP"] == 2
	_, h, _ = unpack_format_slab(tree.get("formato_6"))
	assert h["elements"]["dirs_group"]["x"] == 5


def test_ns_icons_four_vs_eight():
	assert icon_stem_for_label("ns", "HK", 4) == "a"
	assert icon_stem_for_label("ns", "TR", 8) == "l"


def test_zip_import_restores_bindings_from_bindings_folder():
	"""ZIP con bindings/key_bindings.json debe dejar LP=99123 en disco tras import."""
	from profiles.profile_export import import_profile_from_zip
	from profiles.profile_store import _default_profile, _normalize_profile

	slab6 = {
		"LP": 99123,
		"MP": 1,
		"MK": 1,
		"LK": 1,
		"HK": 1,
		"HP": 1,
		"SELECT": None,
		"START": None,
		"Arriba": 1,
		"Abajo": 1,
		"Izquierda": 1,
		"Derecha": 1,
	}
	with tempfile.TemporaryDirectory() as tmp:
		zpath = os.path.join(tmp, "imp.zip")
		zroot = os.path.join(tmp, "zsrc")
		os.makedirs(os.path.join(zroot, "bindings"), exist_ok=True)
		with open(os.path.join(zroot, "profile.json"), "w", encoding="utf-8") as f:
			json.dump(
				{
					"name": "UniqueZipImp42",
					"id": "zipimp_42",
					"button_count": 6,
					"input_mode": "teclado",
				},
				f,
			)
		with open(os.path.join(zroot, "bindings", PROFILE_KEY_BINDINGS_FILENAME), "w", encoding="utf-8") as f:
			json.dump({"formato_6": slab6}, f)
		for name in (
			PROFILE_HITBOX_BINDINGS_FILENAME,
			PROFILE_MIXBOX_BINDINGS_FILENAME,
			PROFILE_JOYSTICK_BINDINGS_FILENAME,
		):
			with open(os.path.join(zroot, "bindings", name), "w", encoding="utf-8") as f:
				json.dump({"formato_6": {}}, f)
		with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
			for root, _, files in os.walk(zroot):
				for fn in files:
					fp = os.path.join(root, fn)
					zf.write(fp, os.path.relpath(fp, zroot))

		profiles_root = os.path.join(tmp, "profiles")
		tpl_root = os.path.join(tmp, "templates")
		index_path = os.path.join(tmp, "profiles_index.json")
		os.makedirs(profiles_root, exist_ok=True)
		os.makedirs(tpl_root, exist_ok=True)

		seed = _normalize_profile(_default_profile("p_seed", "Seed", 6), 1)
		profile_data = {
			"active_profile": seed["id"],
			"profiles": [seed],
			"window_mode": "normal",
			"capture_mode": "normal",
			"ui_font_family": seed.get("ui_font_family", "IBM Plex Mono"),
			"extensions": {},
			"backups_enabled": False,
			"backup_prompt_completed": True,
			"xdg_mirror_enabled": False,
		}

		with patch("config.PROFILES_DIR", profiles_root), patch(
			"profiles.profile_store.PROFILES_DIR", profiles_root
		), patch("profiles.profile_export.PROFILES_DIR", profiles_root), patch(
			"profiles.bindings_storage.PROFILES_DIR", profiles_root
		), patch("profiles.profile_store.PROFILES_PATH", index_path), patch(
			"profiles.bindings_storage.BINDING_TEMPLATES_DIR", tpl_root
		), patch("profiles.profile_store.ensure_contract_dirs", lambda: None):
			out = import_profile_from_zip(zpath, profile_data)

		assert out is not None
		kbf = os.path.join(profiles_root, out["id"], PROFILE_KEY_BINDINGS_FILENAME)
		with open(kbf, "r", encoding="utf-8") as f:
			data = json.load(f)
		assert get_slice(data, "formato_6")["LP"] == 99123


def main():
	test_unpack_flat_roundtrip()
	test_pack_nested_roundtrip()
	test_set_slice_preserves_hud()
	test_ns_icons_four_vs_eight()
	test_zip_import_restores_bindings_from_bindings_folder()
	print("OK: test_bindings_format_slab")


if __name__ == "__main__":
	main()
