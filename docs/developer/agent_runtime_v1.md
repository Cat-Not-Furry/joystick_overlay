# Runtime del agente v1 — Joystick Overlay (Linux)

**Qué cubre:** qué entorno virtual usar cuando el agente recibe **autorización explícita** para ejecutar tests, scripts o smoke runtime. Complementa [audit_contract_v1.md](audit_contract_v1.md) § Alcance; **no** sustituye la instalación de usuario (`install.sh` → `venv/`).

```
version: 1
fecha: 2026-05-26
repo: hud_overlay
```

## Tres entornos, tres roles

| Ruta | Rol | Quién lo usa |
|------|-----|--------------|
| `venv/` | Instalación de usuario (`install.sh`, `run.sh`, `update.sh`) | Usuario final; agente solo con autorización **nivel E** |
| `.venv/` | Runtime del agente (`pip install -e .`) | Agente con autorización **nivel D+** |
| `tests/.tvenv/` | Tests, métricas, pytest, smokes con `SDL_VIDEODRIVER=dummy` | Agente con autorización **nivel B+** |

Los directorios `.venv/` y `tests/.tvenv/` están en `.gitignore`. El agente **no** debe crear ni reinstalar dependencias salvo que falten y el usuario lo autorice.

## Matriz: autorización → entorno → comando

| Nivel | Nombre | ¿Ejecutar? | Entorno | Ejemplos |
|-------|--------|------------|---------|----------|
| A | Estática | No (por defecto) | — | `rg`, lectura de código, `git status` |
| B | Pytest selectivo | Sí | `tests/.tvenv` | Ver plantillas abajo |
| C | Scripts controlados | Sí | `tests/.tvenv` | `run_cyclomatic.py`, `run_cbo.py`, `scripts/check_doc_links.py` |
| D | Smoke runtime | Sí | `.venv` o `tests/.tvenv` | `test_fps.py`, `cli.py doctor`, menú smoke |
| E | Instalación real | Sí | `venv/` vía `install.sh` | Solo si el usuario lo pide explícitamente |

`tests/.tvenv` incluye dependencias de runtime (`pygame`, `evdev`) además de dev (`pytest`, `radon`, `psutil`). Usar `.venv` cuando haga falta el paquete editable (`joystick-overlay`) o entrypoints instalados con `pip install -e .`.

## Plantillas de comando (canónicas)

Desde la raíz del repositorio:

```bash
# Nivel B — pytest completo
SDL_VIDEODRIVER=dummy tests/.tvenv/bin/python3 -m pytest tests/ -q

# Nivel B — pytest selectivo
SDL_VIDEODRIVER=dummy tests/.tvenv/bin/python3 -m pytest tests/test_zip_security.py -v

# Nivel C — métricas de calidad
tests/.tvenv/bin/python3 tests/run_cyclomatic.py
tests/.tvenv/bin/python3 tests/run_cbo.py
tests/.tvenv/bin/python3 tests/run_dit.py
tests/.tvenv/bin/python3 scripts/check_doc_links.py

# Nivel D — smoke gráfico / runtime
SDL_VIDEODRIVER=dummy tests/.tvenv/bin/python3 tests/test_fps.py
SDL_VIDEODRIVER=dummy tests/.tvenv/bin/python3 tests/test_resource_usage.py
SDL_VIDEODRIVER=dummy .venv/bin/python3 cli.py doctor
```

## Reglas obligatorias para el agente

1. **Nunca** usar `python3` del sistema si existe el venv correspondiente al nivel autorizado.
2. **Nunca** `pip install` sin autorización explícita del usuario.
3. **No** modificar `venv/`, `install.sh`, `run.sh` ni `update.sh` salvo tarea explícita de instalación.
4. En informes y bitácora, documentar por cada ejecución:
   - `execution_level` (B, C, D o E)
   - `venv_used` (ruta relativa: `.venv`, `tests/.tvenv`, `venv`)
   - comando exacto
   - `exit_code`
5. Tests gráficos sin display: exportar `SDL_VIDEODRIVER=dummy` antes del comando.

## Campos en informes de auditoría

Además de los campos del [contrato de auditoría v1](audit_contract_v1.md), incluir cuando hubo ejecución:

| Campo | Ejemplo |
|-------|---------|
| `execution_level` | `B` |
| `venv_used` | `tests/.tvenv` |
| `command` | `tests/.tvenv/bin/python3 -m pytest tests/ -q` |
| `exit_code` | `0` |

## Referencias

- [audit_contract_v1.md](audit_contract_v1.md) — severidad, ladder, exclusión habitual
- [tests/README.md](../../tests/README.md) — estructura de pruebas y métricas
- [installation.md](../user/installation.md) — `venv/` de usuario (`install.sh`)
