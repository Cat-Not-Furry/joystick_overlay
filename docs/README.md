# Documentación — Joystick Overlay

Índice por audiencia. El README de la [raíz del repositorio](../README.md) es la entrada rápida; aquí está el detalle y los contratos.

## Usuarios

| Documento | Contenido |
|-----------|-----------|
| [Instalación](user/installation.md) | `install.sh`, venv, integración en el sistema |
| [Inicio rápido](user/quick_start.md) | Ejecutar el HUD y atajos mínimos |
| [Doctor de entorno](user/doctor.md) | `joystick-overlay doctor`, gráficos, evdev |
| [Export / import ZIP de perfil](user/profile_zip.md) | Copia de perfiles, riesgos ZIP |
| [Modo entrenamiento](user/training_mode.md) | Grabación/reproducción de inputs, límites |
| [Modo torneo](user/tournament_mode.md) | `tournament`, FPS, HUD simplificado |
| [Solución de problemas](user/troubleshooting.md) | WM tiling, VIDEORESIZE, evdev, rutas |
| [Índice usuario](user/README.md) | Lista corta de guías `user/` |

## Streamers

| Documento | Contenido |
|-----------|-----------|
| [Modos de captura y OBS](streamer/capture_modes.md) | `normal` / `obs_green`, chroma key, captura por ventana |
| [Checklist OBS](streamer/obs_setup.md) | Fuente ventana, chroma, orden de capas |

## Desarrollo

| Documento | Contenido |
|-----------|-----------|
| [Contrato de datos v1](developer/data_contract_v1.md) | Rutas `user/`, versiones, espejo XDG |
| [Contrato de auditoría v1](developer/audit_contract_v1.md) | Severidad P0–P3, capas de paridad (canónica/adaptable/prohibida), SEC/REL/ARCH/OPS, ladder release |
| [Alcance del producto](developer/product_scope.md) | Qué entra y qué queda fuera |
| [Matriz de reset](developer/reset_matrix.md) | Casos `--reset-data` / `--do-reset-data` |
| [Migraciones de datos](developer/migrations.md) | `configs/migrations/`, manifiestos, `migrate_if_needed` |
| [Estructura del repositorio](developer/repository_layout.md) | Raíz vs `arcade/engine/`, `engine_sys_path` |
| [Reglas de contribución con IA (GPL-3)](developer/ai_contribution_rules.md) | Texto legal y buenas prácticas |
| [Contribuir](CONTRIBUTING.md) | Entorno, tests, estilo, política de citas en doc |
| [Runtime del agente v1](developer/agent_runtime_v1.md) | `.venv`, `tests/.tvenv`, niveles B–E, CI fail/warn |
| [CHANGELOG](../CHANGELOG.md) | Notas de release (Keep a Changelog) |

| Documento | Contenido |
|-----------|-----------|
| [Modelo de confianza](security/security_model.md) | ZIP, rutas, updater, locks |

## Referencia

| Documento | Contenido |
|-----------|-----------|
| [Layout HUD (UX vs datos)](reference/layout_reference.md) | Elementos y coordenadas |
| [Fuentes externas verificables](reference/external_sources.md) | Especificaciones, OWASP, upstream (SDL, OBS, XDG, …) |

## Archivo e historial

| Documento | Contenido |
|-----------|-----------|
| [Bitácora de paridad](archive/bitacora.md) | PAR, colas Windows ↔ Linux, hitos |
| [Registro global de hallazgos](archive/findings_registry.md) | SEC/REL/ARCH/OPS/DOC cross-repo |
| [Matriz de paridad técnica](archive/parity_matrix.md) | Sistema × Linux × Windows |
| [Informe de auditoría (Linux)](archive/audit_report.md) | Instantánea `b31d5d7` / 2026-05-18 |
| [Plan Fase 2 Windows](archive/windows_parity_rollout.md) | Pasos para agente en `hud_owerlay` |
| [Estado backlog priorizado](archive/backlog_status.md) | Cierre ítems 1–16 (P0–P3) post agent_runtime |

## Tests

- [Notas sobre tests](../tests/README.md) (métricas, scripts en `tests/`).
- La carpeta canónica de pruebas es **`tests/`** (singular «test» u otras rutas solo pueden aparecer en forks o historial; no sustituyen a `tests/` en este repositorio).

Comprobación opcional de enlaces en Markdown del repo: `python3 scripts/check_doc_links.py` (ver [CONTRIBUTING.md](CONTRIBUTING.md)).
