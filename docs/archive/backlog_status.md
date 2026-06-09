# Estado del backlog priorizado (2026-05-26)

Referencia: plan **Backlog priorizado pendiente**. Normas: [findings_registry.md](findings_registry.md), [parity_matrix.md](parity_matrix.md).

```
linux_ref: a19edb8 (0.3.2)
working_tree: ARCH-001 A–D + profile_config sin commit
verificado: tests/.tvenv, 29 pytest OK (2026-05-26)
```

## Resumen

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| 1 | SEC-001 ZIP `update.sh` | **Cerrado Linux** | `scripts/safe_zip_update_extract.py` + `update.sh` L132 |
| 2 | SEC-002 `input_state` lock | **Cerrado Linux** | `core/input_state_sync.py`; tests `test_input_state_sync.py` |
| 3 | SEC-003 migration lock | **Cerrado Linux** | `fcntl.flock` en `data_migrations._acquire_migration_lock` |
| 4 | OPS-001 CI mínima | **Cerrado Linux** | `.github/workflows/ci.yml` — pytest, doc links, version (fail); ruff/radon/CBO (warn) |
| 5 | Unificar `hud_layout.py` merge | **Cerrado** | `merged_layout_elements_for_profile` usado en editor + `resolve_hud_layout_offsets` |
| 6 | REL-001 version check | **Cerrado Linux** | `scripts/check_version_alignment.py` en CI |
| 7 | ARCH-001 monolitos | **Cerrado Linux** | Fases A–D + `profile_config`; `main.py` ~140 LOC |
| 8 | `_handle_editor_mouse` CC | **Cerrado** | `_hit_test_editor_handle` extraído |
| 9 | `data_migrations` CC + lock | **Cerrado** | `_execute_manifest_migration` + flock |
| 10 | OPS-002 CHANGELOG | **Cerrado Linux** | `CHANGELOG.md` 0.3.2 |
| 11 | DOC-001 Windows | **Cerrado doc** | Fase 2 `hud_owerlay`; `repository_layout` drift abierto en código W |
| 12 | OPS-003 ruff/radon | **Parcial** | CI warn; gate CC global pendiente |
| 13 | Fase 2 Windows | **Cerrado doc** | `parity_matrix` + `findings_registry` sincronizados |
| 14 | Parpadeo WM real | **Pendiente humano** | Dummy SDL no reproduce; ver [audit_cc_menu.md](audit_cc_menu.md) |
| 15 | Unificar `venv/` paths | **Postergado** | Política en [agent_runtime_v1.md](../developer/agent_runtime_v1.md) |
| 16 | Git commit trabajo | **Pendiente usuario** | Working tree sin commit por decisión del mantenedor |

## Abiertos (cross-repo / código Windows)

| ID | Área | Acción siguiente |
|----|------|------------------|
| SEC-001 | Windows install | Sustituir `extractall` en `install/windows/install_ops.py` |
| SEC-003 | Windows migración | Portar `fcntl.flock` o equivalente Win32 |
| REL-001 | Windows | Alinear `.joystick_version` con `pyproject.toml` |
| ARCH-002 | Windows | Refactor `run_hud_layout_editor` ~409 LOC |
| DOC-001 | Windows | Actualizar `repository_layout.md` al árbol real |

## Recomendación siguiente plan ejecutable

**Hardening Windows P0** (SEC-001 install + REL-001) en `hud_owerlay`, o **commit** del trabajo Linux acumulado (ARCH-001, profile_config, docs Fase 2).
