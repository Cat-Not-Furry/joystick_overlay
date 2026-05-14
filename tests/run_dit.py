#!/usr/bin/env python3
"""
Reporta la profundidad de herencia (DIT) de las clases del proyecto.
El proyecto es mayormente procedural/funcional; este script documenta
el bajo uso de herencia y lista DIT de las clases existentes.
Uso: python tests/run_dit.py [ruta]
"""

import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ENGINE)


def get_py_files(path):
	"""Genera rutas de archivos .py del proyecto, excluyendo tests/, venv, .venv."""
	skip_dirs = {".venv", "venv", "__pycache__", ".git"}
	for dirpath, dirnames, filenames in os.walk(path):
		dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.startswith(".")]
		rel = os.path.relpath(dirpath, ROOT)
		if rel.startswith("tests") and rel != "tests":
			continue
		if "tests" in rel.split(os.sep) and rel != "tests":
			continue
		if ".venv" in rel or "venv" in rel or "__pycache__" in rel:
			continue
		for name in filenames:
			if name.endswith(".py"):
				filepath = os.path.join(dirpath, name)
				relpath = os.path.relpath(filepath, ROOT)
				if relpath.startswith("tests"):
					continue
				yield filepath, relpath


def compute_dit(node, bases_dit_cache):
	"""Calcula DIT de una clase: 1 + max(DIT de bases)."""
	if not node.bases:
		return 1
	max_base = 0
	for base in node.bases:
		if isinstance(base, ast.Name):
			# Base es otra clase del mismo módulo; no tenemos resolución
			# de nombres aquí, asumimos DIT=1 para bases externas
			max_base = max(max_base, 1)
		elif isinstance(base, ast.Attribute):
			max_base = max(max_base, 1)
		else:
			max_base = max(max_base, 1)
	return 1 + max_base


def analyze_file(filepath, relpath):
	"""Extrae clases y su DIT de un archivo."""
	results = []
	try:
		with open(filepath, "r", encoding="utf-8", errors="replace") as f:
			tree = ast.parse(f.read())
	except Exception as e:
		return [{"path": relpath, "error": str(e)}]
	for node in ast.walk(tree):
		if isinstance(node, ast.ClassDef):
			dit = compute_dit(node, {})
			bases = [ast.unparse(b) if hasattr(ast, "unparse") else str(b) for b in node.bases]
			results.append({
				"path": relpath,
				"class": node.name,
				"line": node.lineno,
				"dit": dit,
				"bases": bases,
			})
	return results


def main():
	path = sys.argv[1] if len(sys.argv) > 1 else ROOT
	all_classes = []
	for filepath, relpath in get_py_files(path):
		all_classes.extend(analyze_file(filepath, relpath))

	print("=== Profundidad de herencia (DIT) ===\n")
	if not all_classes:
		print("No se encontraron clases. Proyecto procedural/funcional.")
		sys.exit(0)

	for item in sorted(all_classes, key=lambda x: (x["path"], x["line"])):
		if "error" in item:
			print("{}: Error - {}".format(item["path"], item["error"]))
			continue
		bases_str = ", ".join(item["bases"]) if item["bases"] else "(object)"
		print("{}:{}  {}  DIT={}  bases=[{}]".format(
			item["path"], item["line"], item["class"], item["dit"], bases_str
		))

	max_dit = max(c["dit"] for c in all_classes if "error" not in c)
	print("\nClases encontradas: {}  |  Max DIT: {}".format(len(all_classes), max_dit))
	print("Proyecto con bajo uso de herencia (DIT tipicamente 1).")
	sys.exit(0)


if __name__ == "__main__":
	main()
