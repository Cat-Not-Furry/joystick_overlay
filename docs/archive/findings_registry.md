# Registro global de hallazgos — Joystick Overlay

**Fuente de verdad** para IDs `SEC-*`, `REL-*`, `ARCH-*`, `OPS-*`, `DOC-*` compartidos entre `hud_overlay` y `hud_owerlay`. Normas: [audit_contract_v1.md](../developer/audit_contract_v1.md). Vista sistema × plataforma: [parity_matrix.md](parity_matrix.md).

```
last_sync_linux: b31d5d7 (2026-05-14)
last_sync_windows: pendiente Fase 2 (hud_owerlay)
```

## Índice rápido

| ID | P | global_status | PAR |
|----|---|---------------|-----|
| [SEC-001](#sec-001--pipeline-zip-inconsistente) | P0 | PARCIAL | PAR-005A |
| [SEC-002](#sec-002--input_state-sin-sincronización) | P0 | PARCIAL | — |
| [SEC-003](#sec-003--lock-de-migración-no-atómico) | P1 | PARCIAL | PAR-001 |
| [REL-001](#rel-001--versión-runtime--metadatos) | P1 | PARCIAL | PAR-002 |
| [ARCH-001](#arch-001--monolitos-entrypoints-linux) | P2 | PARCIAL | — |
| [ARCH-002](#arch-002--deuda-mantenibilidad-windows) | P2 | PENDIENTE | — |
| [OPS-001](#ops-001--sin-cicd) | P1 | PARCIAL | — |
| [OPS-002](#ops-002--canal-release--changelog) | P2 | PARCIAL | PAR-005B |
| [OPS-003](#ops-003--higiene-repo--tooling) | P3 | PARCIAL | — |
| [DOC-001](#doc-001--drift-repository_layout-windows) | P2 | PENDIENTE | — |

### Migración desde informes locales

| Origen Linux | Origen Windows | ID global |
|--------------|----------------|-----------|
| Top-5 P0 ZIP / `update.sh` | AUD-2-001 | SEC-001 |
| Top-5 P0 `input_state` | — | SEC-002 |
| P1 migration lock | — | SEC-003 |
| — | AUD-2-002 | REL-001 |
| Q-01, Q-02 | — | ARCH-001 |
| — | AUD-1-002 | ARCH-002 |
| Sin `.github/workflows` | — | OPS-001 |
| PAR-005B / sin CHANGELOG | — | OPS-002 |
| Sin ruff/radon | AUD-6-001 | OPS-003 |
| — | AUD-3-001 | DOC-001 |

---

### SEC-001 — Pipeline ZIP inconsistente

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P0 |
| causality | Confirmado (Linux); Confirmado (Windows, Fase 2) |
| linked_par | PAR-005A |
| parity_layer | Prohibida |
| drift_permitido | No |
| linux_manifestation | `scripts/update.sh` usa `scripts/safe_zip_update_extract.py` (SEC-001 mitigado 2026-05-26) |
| windows_manifestation | `install/windows/` (p. ej. `install_ops`): `extractall` en instalador — ver AUD-2-001 en hud_owerlay |
| impact_runtime | Alto |
| impact_release | Alto |
| impact_maintainability | Bajo |
| impact_security | Alto |
| evidence | Estática |
| reproducible | Desconocido |
| confidence | 0.90 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

---

### SEC-002 — input_state sin sincronización

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P0 |
| causality | Confirmado |
| linked_par | — |
| parity_layer | Canónica (concurrencia) |
| drift_permitido | No |
| linux_manifestation | `core/input_state_sync.py` + lock en `maps/input_reader.py`; snapshot en `main.py` (SEC-002 mitigado 2026-05-26) |
| windows_manifestation | N/E (backend distinto; no equivaler a evdev) |
| impact_runtime | Alto |
| impact_release | Medio |
| impact_maintainability | Medio |
| impact_security | Alto |
| evidence | Estática |
| reproducible | Desconocido |
| confidence | 0.85 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

---

### SEC-003 — Lock de migración no atómico

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P1 |
| causality | Confirmado |
| linked_par | PAR-001 |
| parity_layer | Canónica |
| drift_permitido | No |
| linux_manifestation | `data_migrations._acquire_migration_lock`: `fcntl.flock` exclusivo (SEC-003 mitigado 2026-05-26) |
| windows_manifestation | PENDIENTE — verificar equivalente en `hud_owerlay` |
| impact_runtime | Medio |
| impact_release | Medio |
| impact_maintainability | Bajo |
| impact_security | Medio |
| evidence | Estática |
| reproducible | No |
| confidence | 0.88 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

---

### REL-001 — Versión runtime / metadatos

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P1 |
| causality | Confirmado (Linux); Inferido (Windows hasta Fase 2) |
| linked_par | PAR-002 |
| parity_layer | Canónica |
| drift_permitido | No |
| linux_manifestation | `.joystick_version` en raíz vs `pyproject.toml` — alineados en `b31d5d7`; vigilar drift en portes |
| windows_manifestation | AUD-2-002 — completar rutas en hud_owerlay |
| impact_runtime | Bajo |
| impact_release | Medio |
| impact_maintainability | Bajo |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.75 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

---

### ARCH-001 — Monolitos entrypoints (Linux)

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P2 |
| causality | Confirmado |
| linked_par | — |
| parity_layer | — (mantenibilidad) |
| drift_permitido | Sí |
| linux_manifestation | `main.py` 1359 LOC; `arcade/engine/render/profile_config_menu.py` 1038 LOC (Q-01, Q-02); CC radon: `run_hud_layout_editor` era CC=100 (2026-05-26), refactorizado a CC≤10 en `1b0eaf2` — ver [audit_cc_menu.md](audit_cc_menu.md) |
| windows_manifestation | N/E |
| impact_runtime | Bajo |
| impact_release | Bajo |
| impact_maintainability | Alto |
| impact_security | Bajo |
| evidence | Estática + Runtime (pytest, radon post-refactor) |
| reproducible | Sí |
| confidence | 0.95 |
| last_verified | hud_overlay `1b0eaf2` / 2026-05-26 |

---

### ARCH-002 — Deuda mantenibilidad (Windows)

| Campo | Valor |
|-------|-------|
| global_status | PENDIENTE |
| severity_global | P2 |
| causality | Confirmado (Windows) |
| linked_par | — |
| parity_layer | — (mantenibilidad) |
| drift_permitido | Sí |
| linux_manifestation | N/E |
| windows_manifestation | AUD-1-002: función ~409 líneas — completar ruta en Fase 2 |
| impact_runtime | Bajo |
| impact_release | Bajo |
| impact_maintainability | Alto |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Desconocido |
| confidence | — |
| last_verified | pendiente hud_owerlay |

---

### OPS-001 — Sin CI/CD

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P1 |
| causality | Confirmado |
| linked_par | — |
| parity_layer | Canónica (release) |
| drift_permitido | No |
| linux_manifestation | `.github/workflows/ci.yml` pytest+doc links+version check (OPS-001 PARCIAL Linux 2026-05-26) |
| windows_manifestation | PENDIENTE — según AUD dimensión 5/6 |
| impact_runtime | — |
| impact_release | Alto |
| impact_maintainability | Medio |
| impact_security | Medio |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.99 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

---

### OPS-002 — Canal release / CHANGELOG

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P2 |
| causality | Confirmado |
| linked_par | PAR-005B |
| parity_layer | Canónica (release) |
| drift_permitido | No |
| linux_manifestation | Sin CHANGELOG; política de actualización en campo incompleta (L-OPS-003-P) |
| windows_manifestation | PENDIENTE — PAR-005B producto |
| impact_runtime | — |
| impact_release | Alto |
| impact_maintainability | Bajo |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.90 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

---

### OPS-003 — Higiene repo / tooling

| Campo | Valor |
|-------|-------|
| global_status | PARCIAL |
| severity_global | P3 |
| causality | Confirmado |
| linked_par | — |
| parity_layer | — (higiene) |
| drift_permitido | Sí |
| linux_manifestation | Sin `[tool.ruff]` / `radon` en `pyproject.toml` (Q-04 ámbito tooling) |
| windows_manifestation | AUD-6-001: Git/port sin commit — detalle en Fase 2 |
| impact_runtime | — |
| impact_release | Bajo |
| impact_maintainability | Medio |
| impact_security | Bajo |
| evidence | Estática |
| reproducible | Sí |
| confidence | 0.92 |
| last_verified | hud_overlay `b31d5d7` / 2026-05-18 |

---

### DOC-001 — Drift repository_layout (Windows)

| Campo | Valor |
|-------|-------|
| global_status | PENDIENTE |
| severity_global | P2 |
| causality | Confirmado (Windows) |
| linked_par | — |
| parity_layer | Canónica (docs) |
| drift_permitido | No |
| linux_manifestation | N/E |
| windows_manifestation | AUD-3-001 — `repository_layout` vs árbol real |
| impact_runtime | — |
| impact_release | Bajo |
| impact_maintainability | Medio |
| impact_security | — |
| evidence | Estática |
| reproducible | Sí |
| confidence | — |
| last_verified | pendiente hud_owerlay |
