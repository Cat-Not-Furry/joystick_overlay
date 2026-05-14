#!/usr/bin/env python3
"""Sanidad de rutas híbridas (canon bajo proyecto)."""

import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "arcade", "engine")
sys.path.insert(0, ENGINE)

from config import BACKUP_PROFILES_ROOT, PROJECT_ROOT, get_user_dir


def test_user_dir_under_project_root():
	ud = Path(get_user_dir()).resolve()
	root = Path(PROJECT_ROOT).resolve()
	assert ud == root / "user"


def test_backup_root_distinct_from_user_dir():
	assert Path(get_user_dir()).resolve() != Path(BACKUP_PROFILES_ROOT).resolve()


def main():
	test_user_dir_under_project_root()
	test_backup_root_distinct_from_user_dir()
	print("OK: test_config_paths")


if __name__ == "__main__":
	main()
