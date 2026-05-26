# Matriz de paridad técnica — Linux ↔ Windows

Complementa el tablero `PAR-*` de [bitacora.md](bitacora.md). Hallazgos globales: [findings_registry.md](findings_registry.md). Normas: [audit_contract_v1.md](../developer/audit_contract_v1.md) (§ Modelo de paridad por capas).

```
matrix_version: 2
parity_layers: 2026-05-18
linux_ref: b31d5d7 (2026-05-14)
windows_ref: completar en Fase 2 (hud_owerlay)
```

## Leyenda de columnas

| Columna | Significado |
|---------|-------------|
| Sistema | Tema técnico o de producto |
| Linux / Windows | Estado en esa plataforma (`OK`, `PARCIAL`, `PENDIENTE`, `DRIFT`, `N/E`) |
| Estado | Lectura cross-repo |
| `tipo` | `Canonical` \| `Adapted` \| `Transitional` ([audit_contract_v1](../developer/audit_contract_v1.md)) |
| `paridad` | `Exacta` \| `Funcional` \| `Pendiente` |
| `drift_permitido` | `Sí` \| `No` — drift de **plataforma** permitido o prohibido |
| `motivo_plataforma` | `evdev` \| `AppData` \| `Win32` \| `installer` \| `—` |
| linked_par / linked_sec | IDs de seguimiento |

## Matriz

| Sistema | Linux | Windows | Estado | tipo | paridad | drift_permitido | motivo_plataforma | linked_par | linked_sec | Notas |
|---------|-------|---------|--------|------|---------|-----------------|-------------------|------------|------------|-------|
| Update ZIP (runtime) | OK (mecánica PAR-005A) | PARCIAL (cli seguro; install pendiente) | Transicional | Transitional | Pendiente | No | installer | PAR-005A, PAR-005B | SEC-001 | Linux: `safe_zip` perfil vs `unzip` en update |
| Versión runtime | OK | DRIFT | Divergencia contractual | Canonical | Pendiente | No | — | PAR-002 | REL-001 | Completar evidencia W en Fase 2 |
| Input backend | evdev | keyboard | Adaptado válido | Adapted | Funcional | Sí | evdev | — | — | No es deuda; backends distintos |
| Persistencia canon `user/` | OK | OK (código) | Adaptado válido | Adapted | Funcional | Sí | AppData | PAR-001 | — | Misma lógica; rutas OS distintas |
| Reset dos fases | implementado | pendiente validación | PARCIAL | Canonical | Pendiente | No | — | PAR-003 | — | Linux `--reset-data` / `--do-reset-data` |
| Hooks / input history | OK | OK | Igual | Canonical | Exacta | No | — | PAR-004 | — | |
| CLI soporte | OK | PARCIAL | PARCIAL | Canonical | Pendiente | No | — | PAR-002 | — | |
| Instalación / accesos | install.sh | install/windows | PARCIAL | Adapted | Funcional | Sí | installer | PAR-006 | — | Evidencia W: `install/windows/` |
| Preflight UX | PARCIAL | PARCIAL | PARCIAL | Canonical | Pendiente | No | — | PAR-007 | — | |
| CI / QA automatizado | ausente | según AUD | PARCIAL | Canonical | Pendiente | No | — | — | OPS-001 | |
| ZIP perfil (import) | OK | PENDIENTE | PARCIAL | Canonical | Pendiente | No | — | — | — | Política en security_model |
| Monolitos / deuda LOC | PARCIAL | PARCIAL | PARCIAL | Canonical | Pendiente | Sí | — | — | ARCH-001, ARCH-002 | Deuda mantenibilidad, no prohibida |
| Canal release usuario | PARCIAL | PARCIAL | PARCIAL | Canonical | Pendiente | No | — | PAR-005B | OPS-002 | |
| Tooling / higiene Git | PARCIAL | PENDIENTE | PARCIAL | Canonical | Funcional | Sí | — | — | OPS-003 | Higiene/tooling |
| Docs layout vs árbol | OK | PENDIENTE | PARCIAL | Canonical | Pendiente | No | — | — | DOC-001 | Solo Windows en AUD-3-001 |

## Capa prohibida activa (violaciones `drift_permitido: No`)

- **SEC-001** — Pipeline ZIP/update semánticamente incoherente (L: `unzip` en update; W: install pendiente de alinear).
- **SEC-002** — Concurrencia `input_state` sin lock (Linux; manifestación Windows N/E).
- **SEC-003** — Lock de migración no atómico (canónica datos).
- **REL-001** — Drift versión runtime / metadatos release.

## Tablero PAR (resumen; detalle en bitácora)

| PAR | Linux | Windows (bitácora) | Impacto |
|-----|-------|-------------------|---------|
| PAR-001 | PARCIAL | PARCIAL | CRÍTICO |
| PAR-002 | OK | OK | MEDIO |
| PAR-003 | PARCIAL | PARCIAL | CRÍTICO |
| PAR-004 | OK | OK | CRÍTICO |
| PAR-005A | OK | PARCIAL | CRÍTICO |
| PAR-005B | PARCIAL | PARCIAL | CRÍTICO |
| PAR-006 | PARCIAL | PARCIAL | MEDIO |
| PAR-007 | PARCIAL | PARCIAL | BAJO |

## Sincronización

- **Fase A (este repo):** `matrix_version: 2` + reclasificación por capas.
- **Fase B (`hud_owerlay`):** [windows_parity_rollout.md](windows_parity_rollout.md) — completar columna Windows y reclasificar filas locales.
