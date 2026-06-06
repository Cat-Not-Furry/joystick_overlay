# Changelog

Todos los cambios notables de **Joystick Overlay** (Linux) se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa [versionado semántico](https://semver.org/lang/es/).

## [Unreleased]

### Planned

- ARCH-001: extracción de `main.py` (Fases A–C) y troceo de `profile_config_menu.py`.
- Paridad Windows (`hud_owerlay`, Fase 2).

## [0.3.2] - 2026-05-26

Beta Linux del fork a largo plazo. Hardening de seguridad y CI mínima con métricas de calidad en modo informativo.

### Added

- CI en `.github/workflows/ci.yml`: pytest (`SDL_VIDEODRIVER=dummy`), `check_doc_links`, `check_version_alignment`.
- Métricas en CI (modo warning): `ruff check`, `run_cyclomatic`, `run_cbo`.
- [docs/developer/agent_runtime_v1.md](docs/developer/agent_runtime_v1.md): política de entornos `.venv` y `tests/.tvenv` para el agente.
- Smoke de menú: `tests/test_main_menu_smoke.py`.
- Extracción ZIP segura en actualizaciones: `scripts/safe_zip_update_extract.py`.
- Sincronización de `input_state`: `arcade/engine/core/input_state_sync.py`.
- Check de alineación de versión: `scripts/check_version_alignment.py`.

### Changed

- Versión runtime y metadatos alineados a **0.3.2** (`.joystick_version`, `pyproject.toml`).
- Merge de layout HUD unificado en `hud_layout.py` (`merged_layout_elements_for_profile`).
- Lock de migraciones con `fcntl.flock` en `data_migrations.py`.
- Refactor de complejidad en `hud_layout_editor.py` y helpers en `main.py` / `data_migrations.py`.

### Security

- **SEC-001** (Linux): `update.sh` deja de usar `unzip` directo.
- **SEC-002** (Linux): race `input_state` mitigada con lock y snapshot por frame.
- **SEC-003** (Linux): lock de migración atómico.

Estado global en [findings_registry.md](docs/archive/findings_registry.md): **PARCIAL** hasta evidencia Windows y CI remota verde.

### Verified (local)

Con `tests/.tvenv` y `SDL_VIDEODRIVER=dummy`:

- `pytest tests/`
- `scripts/check_doc_links.py`
- `scripts/check_version_alignment.py`

Push a remoto y validación en GitHub Actions: a cargo del mantenedor.
