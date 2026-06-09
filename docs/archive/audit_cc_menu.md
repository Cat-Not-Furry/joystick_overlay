# Auditoría CC + menú — instantánea

```
schema: audit_contract_v1
commit: 1b0eaf2
fecha: 2026-05-26
repo: hud_overlay
execution_level: B+C+D
venv_used: tests/.tvenv
```

Complementa [audit_report.md](audit_report.md); no sustituye el registry ni la bitácora PAR.

Normas: [audit_contract_v1.md](../developer/audit_contract_v1.md) · Runtime: [agent_runtime_v1.md](../developer/agent_runtime_v1.md)

---

## 1. Resumen

| Área | Resultado |
|------|-----------|
| Pytest unitario | **27/27** OK (incl. `test_main_menu_smoke` tras implementación del plan) |
| Smoke FPS | OK — 60.3 FPS (objetivo 60, mínimo 45) |
| Smoke recursos | OK — 46.7 MB RAM, 18.2% CPU |
| Menú aislado | Estable en dummy; 0 `VIDEORESIZE` en 3 s; ESC → `salir` (ARCH-001 Fase D: `run_main_menu_until_action` + `drive_menu_frame` unificado con `main()`) |
| DIT / CBO | OK |
| Complejidad ciclomática | Post-refactor: `run_hud_layout_editor` CC=**7** (antes 100); `_hit_test_editor_handle` + `_apply_editor_drag_motion` extraídos de `_handle_editor_mouse` |

**Veredicto:** sin bloqueo funcional inmediato; deuda de mantenibilidad alta en editor HUD (ARCH-001).

---

## 2. Restricciones

- Entorno: `tests/.tvenv` (Python 3.14.5), `SDL_VIDEODRIVER=dummy` en tests gráficos.
- No se modificó `venv/` de usuario ni `install.sh` / `run.sh` / `update.sh`.
- Parpadeo en WM real no evaluado (solo dummy SDL).

### Evidencia ejecutada

| Comando | Nivel | Exit |
|---------|-------|------|
| `tests/.tvenv/bin/python3 -m pytest tests/ -v` | B | 0 |
| `tests/.tvenv/bin/python3 tests/run_cyclomatic.py` | C | 1 |
| `tests/.tvenv/bin/python3 tests/run_cbo.py` | C | 0 |
| `tests/.tvenv/bin/python3 tests/run_dit.py` | C | 0 |
| `SDL_VIDEODRIVER=dummy tests/.tvenv/bin/python3 tests/test_fps.py` | D | 0 |
| `SDL_VIDEODRIVER=dummy tests/.tvenv/bin/python3 tests/test_resource_usage.py` | D | 0 |

---

## 3. Hallazgos

### ARCH-001 (parcial) — Complejidad ciclomática editor HUD

| Campo | Valor |
|-------|-------|
| ID | ARCH-001 |
| Severidad | P2 |
| Causalidad | Confirmado (radon) |
| Evidencia | Runtime + Estática |

**Top violaciones CC (umbral 10):**

| Función | Archivo | CC |
|---------|---------|-----|
| `run_hud_layout_editor` | `arcade/engine/render/hud_layout_editor.py` | 100 |
| `_init_editor_state` | `arcade/engine/profiles/hud_layout.py` | 27 |
| `resolve_hud_layout_offsets` | `arcade/engine/profiles/hud_layout.py` | 25 |
| `apply_config_manifest_migrations` | `arcade/engine/core/data_migrations.py` | 24 |
| `_handle_main_menu_key` | `main.py` | 15 |

**Acción P0 (este plan):** refactor solo `hud_layout_editor.py` — **cerrado**: `run_hud_layout_editor` CC=7.

**Diferido P1:** unificar merge layout en `hud_layout.py`.

### Menú principal — smoke estable (dummy)

| Campo | Valor |
|-------|-------|
| Evidencia | Runtime, `JOYSTICK_DEBUG_MENU=1` |
| Redraw | ~25 Hz en dummy; sin storm de resize |
| Riesgo parpadeo WM | Incertidumbre — no reproducido en dummy |

---

## 4. Riesgo residual

- **Funcional:** bajo (tests verdes).
- **Mantenibilidad:** alto en editor HUD hasta cerrar refactor CC.
- **Regresión layout:** media durante refactor; mitigada con `test_hud_layout.py` (11 tests).

---

## 5. Paridad

Sin impacto cross-repo directo. ARCH-001 es mantenibilidad Linux; ver [findings_registry.md](findings_registry.md).

---

## 6. Plan de acción

| P | Acción | Estado |
|---|--------|--------|
| P0 | Refactor `run_hud_layout_editor` | Cerrado (CC=7) |
| P1 | Unificar `_init_editor_state` / `resolve_hud_layout_offsets` | Diferido |
| P2 | `test_main_menu_smoke.py` automatizado | Implementado |
| P2 | Documentar `agent_runtime_v1.md` | Implementado |

---

## 7. Confianza

| Hallazgo | confidence |
|----------|------------|
| CC violaciones | 0.95 (radon reproducible) |
| Menú estable dummy | 0.85 |
| Parpadeo WM real | 0.40 (no medido) |

---

## 8. Estado release (ladder)

**`LOCAL_READY`** — uso local y auditorías con agente autorizado; CC del editor sigue como deuda ARCH-001.
