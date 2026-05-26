# Informe de auditoría técnica — Joystick Overlay (Linux)

## Metadatos

| Campo | Valor |
|-------|--------|
| Repositorio | `hud_overlay` (slug Git; producto **Joystick Overlay**) |
| Commit auditado | `b31d5d7` (2026-05-14 — «Mejoras, estructura y formato») |
| Versión declarada | `0.3.1` (`pyproject.toml`); runtime `.joystick_version` en raíz |
| Fecha del informe | 2026-05-18 |
| Alcance | Código producto: `arcade/engine/` (37 módulos `.py`), entrypoints raíz, `configs/`, lectura de `scripts/*.sh`, documentación `docs/` |
| Plataforma objetivo | Linux (X11/Wayland + evdev); paridad Windows vía bitácora (sin abrir `hud_owerlay`) |
| Schema | `audit_contract_v1` — hallazgos canónicos en [findings_registry.md](findings_registry.md) |

### Exclusiones explícitas (metodología)

- **No** se modificó código de producto (salvo este informe).
- **No** se creó ni usó `venv/` del proyecto; **no** `pip install -r requirements.txt`.
- **No** se ejecutó nada en [`scripts/`](../../scripts/) (`install.sh`, `update.sh`, `run.sh`, `check_doc_links.py`).
- **No** se ejecutó nada en [`tests/`](../../tests/) (dimensión 4 no evaluada por ejecución).
- Herramientas `ruff`, `radon`, `bandit` **no** disponibles en el entorno del auditor; análisis basado en lectura estática y `rg`.

---

## Resumen ejecutivo

Joystick Overlay **no es un script improvisado**: tiene contrato de datos versionado, migraciones declarativas, modelo de seguridad documentado y controles ZIP/rutas conscientes. Está **por encima del OSS hobby típico** en persistencia y defensa local frente a archivos hostiles.

Los riesgos principales **no** son RCE remota clásica, sino **madurez operativa**: concurrencia sin sincronizar `input_state`, **dos pipelines ZIP** (Python fuerte vs `unzip` en shell), ausencia de **CI**, y **paridad Windows** incompleta (PAR-001, PAR-003, PAR-005B).

**Estado release (ladder):** [`LOCAL_READY`](../developer/audit_contract_v1.md#release-readiness-ladder) — uso local y clon de confianza con precaución en ZIP de terceros y update. **No** alcanza `CI_MIN` ni `PARITY_CORE` (sin CI; paridad Windows incompleta; SEC-001/SEC-002 abiertos).

### Tabla de cumplimiento (0–100)

| Dimensión | Estado | Nota | Notas breves |
|-----------|--------|------|----------------|
| 1. Calidad del código | Intermedio | 62 | Monolitos `main.py` / menú config; sin linter en repo |
| 2. Seguridad y dependencias | Intermedio–sólido | 74 | ZIP Python maduro; gaps concurrencia y update shell |
| 3. Documentación | Sólido | 78 | `docs/` rico; sin CHANGELOG |
| 4. Pruebas y QA | N/E | — | Excluida por alcance (sin ejecutar `tests/`) |
| 5. Configuración y automatización | Frágil | 38 | Sin `.github/workflows`; `pyproject` mínimo |
| 6. Estructura e higiene Git | Intermedio–sólido | 72 | Layout documentado; agentes locales en `.gitignore` |
| 7. Checklist lanzamiento GitHub | Intermedio | 55 | LICENSE/README OK; falta CI, firma, CHANGELOG |
| 8. Paridad versiones / informe | Intermedio | 70 | Bitácora PAR-* clara; Windows pendiente |

**Puntuación global orientativa** (dimensiones 1–3, 5–8, peso igual): **~66/100**.

### Top 5 hallazgos

1. **SEC-002 (P0)** — `input_state` compartido sin lock entre hilo evdev/teclado y bucle Pygame (`main.py` ~1046, `input_reader.py`).
2. **SEC-001 (P0)** — Asimetría ZIP update: import perfil usa `safe_zip_extract.py`; update usa `unzip` sin límites equivalentes (`scripts/update.sh` ~132). Relacionado: **PAR-005A** OK mecánica parcial; mitigación global **PARCIAL**.
3. **SEC-003 (P1)** — Lock de migración no atómico (`data_migrations.py` `_acquire_migration_lock`: `isfile` + `open`, no `fcntl`/`O_EXCL`).
4. **OPS-001 (P1)** — Sin CI/CD (no existe `.github/workflows`).
5. **ARCH-001 (P2)** — Monolitos: `main.py` 1359 LOC, `profile_config_menu.py` 1038 LOC.

### Índice de migración (IDs locales → globales)

| Origen (este informe) | ID global | P |
|----------------------|-----------|---|
| Top-5 #2 ZIP update | SEC-001 | P0 |
| Top-5 #1 `input_state` | SEC-002 | P0 |
| Top-5 #3 migration lock | SEC-003 | P1 |
| Top-5 #4 sin CI | OPS-001 | P1 |
| Top-5 #5 monolitos | ARCH-001 | P2 |
| Q-01 | ARCH-001 | P2 |
| Q-02 | ARCH-001 | P2 |
| Q-04 excepciones amplias | — | P2 (sin ID global dedicado) |
| Q-07 estilo tabs | — | P2 |
| Sin CHANGELOG / PAR-005B | OPS-002 | P2 |
| Sin ruff/radon | OPS-003 | P3 |
| — (Windows) AUD-2-001 | SEC-001 | P0 |
| — (Windows) AUD-1-002 | ARCH-002 | P2 |
| — (Windows) AUD-2-002 | REL-001 | P1 |
| — (Windows) AUD-6-001 | OPS-003 | P3 |
| — (Windows) AUD-3-001 | DOC-001 | P2 |

Detalle y manifestaciones: [findings_registry.md](findings_registry.md). Vista cross-repo: [parity_matrix.md](parity_matrix.md).

### Confianza (hallazgos migrados)

| ID | Evidencia | Runtime | confidence |
|----|-----------|---------|------------|
| SEC-001 | Estática | No | 0.90 |
| SEC-002 | Estática | No | 0.85 |
| SEC-003 | Estática | No | 0.88 |
| OPS-001 | Estática | No | 0.99 |
| ARCH-001 | Estática | No | 0.95 |

---

## Restricciones de esta auditoría

Ver metadatos. La dimensión 4 documenta existencia de pruebas sin ejecutarlas; el riesgo de regresión HUD/input permanece **no medido** en esta pasada.

---

## 1. Calidad del código

**Estado:** Intermedio

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia | Prioridad |
|----|-----------|----------|-----------|-----------|
| Q-01 | Media | `main.py` concentra menú, HUD, reset, subprocess, detección `/proc`, training | 1359 LOC; ~20 bloques `import`/`from` | P1 |
| Q-02 | Media | `profile_config_menu.py` mezcla UI, update modal, import ZIP, handlers | 1038 LOC | P1 |
| Q-03 | Baja | Sin `TODO`/`FIXME` en `arcade/engine/` | `rg` sin coincidencias | — |
| Q-04 | Baja | Patrón `except Exception` amplio (≥50 usos en engine) | p. ej. `profile_store.py` (9), `input_reader.py` (8), `data_migrations.py` (16) | P2 |
| Q-05 | Baja | Type hints / docstrings incompletos en API pública | Muestreo: `input_reader`, `profile_store` — funciones sin docstring formal | P2 |
| Q-06 | Info | Proyecto mayormente procedural; poco SOLID/OOP aplicable | `StateManager` ligero; sin jerarquías profundas | — |
| Q-07 | Media | Mezcla tabs (engine) y estilo entrypoint raíz | Convención heterogénea | P2 |

### Herramientas

- `ruff` / `radon`: **no ejecutados** (no instalados en entorno auditor).
- Umbral CC≤10 documentado en `tests/run_cyclomatic.py` — **no verificado** en esta pasada.

### Recomendaciones (sin implementar)

- Extraer verticalmente de `main.py`: lifecycle startup, HUD session, reset manager.
- Introducir `[tool.ruff]` en `pyproject.toml` cuando se abra CI (dimensión 5).

---

## 2. Seguridad y dependencias

**Estado:** Intermedio–sólido (local); supply chain débil

### 2.1 Superficies y controles

| Superficie | Confianza | Control observable |
|------------|-----------|-------------------|
| Import ZIP perfil | No confiable | [`safe_zip_extract.py`](../../arcade/engine/utils/safe_zip_extract.py): traversal, symlinks, límites tamaño, chunks 64KiB |
| Update ZIP | No confiable | [`scripts/update.sh`](../../scripts/update.sh): `flock`, `find -P`, whitelist `cp -rL` — **sin** mismos límites que Python |
| Rutas iconos/HUD | Semi-confiable | [`safe_paths.py`](../../arcade/engine/utils/safe_paths.py), [`assets_resolver.py`](../../arcade/engine/core/assets_resolver.py) |
| Subprocess Python | Media | Listas argv; **sin** `shell=True` (`rg` en `*.py`) |
| `/dev/input` | OS | `preferred_*_path` como string sin whitelist estricta (`input_reader.py`) |
| Supply chain | Externa | `git pull --ff-only`; sin firma GPG/Sigstore |

### 2.2 CWE (solo con evidencia en código)

| CWE | Descripción | ¿Aplica? | Evidencia | Prioridad |
|-----|-------------|----------|-----------|-----------|
| CWE-22 | Path traversal | Mitigado (import) / parcial (update) | `safe_zip_extract` L103–109; `update.sh` post-`unzip` | Media |
| CWE-59 | Symlink | Mitigado | ZipInfo `S_IFLNK`; `find -P` en update | Baja–media |
| CWE-367 | TOCTOU | Sí | `resolve_under_root` exige `cand.exists()` L37–38 antes de uso posterior | Media |
| CWE-362 | Race | Sí | `input_state` mutado en hilo daemon; lectura en main loop sin lock | Media |
| CWE-78 | Command injection | Bajo en Python | `subprocess` con listas; update usa `bash` + script fijo | Baja |
| CWE-400 | ZIP bomb | Parcial | Límites en Python; `unzip -q` sin cuota en update | Media |
| CWE-494 | Supply chain | Sí | Sin firma de releases; confianza en origen ZIP/git | Alta (si origen no confiable) |

### 2.3 Subprocess (inventario)

| Ubicación | Invocación | Notas |
|-----------|------------|-------|
| `main.py` ~194, ~217 | `Popen([python, ...])` | Training / easteregg; rutas bajo repo |
| `main.py` ~1322 | `run([python, __file__, --do-reset-data])` | Reset bifurcado |
| `profile_config_menu.py` ~270 | `Popen(["bash", update_script])` | Script fijo bajo `scripts/update.sh` |
| `file_picker.py` / `image_file_picker.py` | `run([zenity|kdialog, ...])` | Binarios del PATH |

### 2.4 Persistencia segura

- Escritura atómica JSON: `mkstemp` + `fsync` + `os.replace` en `profile_store._write_json_atomic` (L74–84).
- Guardado perfiles: `fcntl.flock` exclusivo en `profiles_index.lock` (L478–485) — **advisory** (POSIX).

### 2.5 Dependencias runtime

```
pygame==2.6.1
evdev==1.9.3
```

Superficie pequeña; `evdev` solo Linux. **pip-audit / bandit:** no ejecutados.

### 2.6 Secretos

`rg` password/api_key/secret: solo «token» semántico en configs/schema — **no** credenciales. `.gitignore` excluye `user/`, `venv/`, `*.log`.

### Coherencia con documentación

[`docs/security/security_model.md`](../security/security_model.md) **coincide** con el código revisado en import ZIP, resolver, flock perfiles y política update shell.

---

## 3. Documentación

**Estado:** Sólido

### Presente

- [`README.md`](../../README.md): instalación, CLI, seguridad ZIP, índice `docs/`.
- [`docs/README.md`](../README.md), [`docs/CONTRIBUTING.md`](../CONTRIBUTING.md).
- Contrato: [`docs/developer/data_contract_v1.md`](../developer/data_contract_v1.md).
- Layout: [`docs/developer/repository_layout.md`](../developer/repository_layout.md).
- Seguridad: [`docs/security/security_model.md`](../security/security_model.md).
- Reset: [`docs/developer/reset_matrix.md`](../developer/reset_matrix.md) (matriz operativa PAR-003).
- Paridad: [`docs/archive/bitacora.md`](bitacora.md).
- IA/GPL: [`docs/developer/ai_contribution_rules.md`](../developer/ai_contribution_rules.md).
- Referencias externas: [`docs/reference/external_sources.md`](../reference/external_sources.md).

### Ausente o parcial

| Ítem | Estado |
|------|--------|
| CHANGELOG.md (Keep a Changelog) | Ausente |
| CODE_OF_CONDUCT.md | Ausente |
| Badges CI/coverage en README | Ausente (coherente: sin CI) |
| API Sphinx/MkDocs | N/A (app desktop) |
| `12-reglas-ia-gpl3.md` en raíz | Plantilla con placeholders; canónico relleno en `docs/developer/ai_contribution_rules.md` |

### Enlaces

`scripts/check_doc_links.py` **no ejecutado**. Revisión manual: README enlaza rutas existentes bajo `docs/`.

---

## 4. Pruebas y QA

**Estado:** No evaluada (N/E)

### Inventario (solo referencia; sin ejecución)

| Artefacto | Rol |
|-----------|-----|
| `tests/test_zip_security.py` | ZIP / `safe_paths` |
| `tests/test_config_paths.py` | Canon `user/` vs XDG |
| `tests/test_hud_layout.py`, `test_bindings_*.py` | Layout y bindings |
| `tests/test_menu_minimal.py` | Menú (SDL dummy) |
| `tests/test_fps.py`, `test_resource_usage.py` | Rendimiento |
| `tests/run_cyclomatic.py`, `run_cbo.py`, `run_dit.py` | Métricas (radon) |
| `tests/requirements-dev.txt` | pytest, radon, psutil |

### Riesgo residual

Regresiones en HUD, input thread, migraciones y update **no verificadas** en esta auditoría. Smoke manual recomendado al mantenedor: `joystick-overlay doctor`, HUD, `--reset-data` según [`reset_matrix.md`](../developer/reset_matrix.md).

---

## 5. Configuración y automatización

**Estado:** Frágil

| Ítem | Estado |
|------|--------|
| `pyproject.toml` | Runtime + script `joystick-overlay`; paquetes en `arcade/engine` |
| `[tool.ruff]` / black / mypy | Ausente |
| `.github/workflows` | **Ausente** |
| Dependabot / CodeQL | Ausente |
| pre-commit | Ausente |
| Dev deps | `tests/requirements-dev.txt` (no instalado en auditoría) |

`scripts/update.sh` L192–196 exige `venv/bin/python3` para pip post-update — política de instalación acoplada a venv (solo observado por lectura).

---

## 6. Estructura del repositorio e higiene Git

**Estado:** Intermedio–sólido

### Árbol (resumen)

```
Raíz: main.py, cli.py, configure.py, tournament.py, doctor.py, engine_sys_path.py
arcade/engine/: config, profiles, render, maps, core, utils, training (37 .py)
arcade/assets/: icon packs, .assets_version
configs/: defaults, schema, migrations/
user/: datos operativos (canon, en .gitignore)
docs/, scripts/, install/, tests/
```

Alineado con [`repository_layout.md`](../developer/repository_layout.md).

### `.gitignore`

- `user/`, `venv/`, `__pycache__/`, caches pytest/ruff/mypy.
- Agentes locales: `reglas_rapidas.md`, `analisis_profundo.md`, `indice_agente.md` (no versionados).

### Git (readonly)

- Commit: `b31d5d7`.
- Sin verificación de tags/releases en esta pasada.

---

## 7. Checklist lanzamiento GitHub

**Estado:** Intermedio

| Criterio | Cumple |
|----------|--------|
| LICENSE GPL-3 en raíz | Sí (`LICENSE`, `pyproject.toml`, `MANIFEST.in`) |
| README instalación/uso | Sí |
| Versión en metadatos | Sí (`0.3.1`, `.joystick_version`) |
| CI verde en PR | No (sin CI) |
| CHANGELOG / release notes | No |
| Firma artefactos ZIP | No |
| Tests automatizados en release gate | No (excluidos aquí) |
| READONLY_MODE / auth servidor | N/A |

**Estado release (sección 7):** `LOCAL_READY` — no `CI_MIN` (falta CI, PAR-005B, firma).

---

## 8. Paridad Linux / Windows e informe consolidado

**Estado:** Intermedio (documentado en bitácora)

Fuente: [`bitacora.md`](bitacora.md) (tablero al 2026-05-14+).

| PAR | Estado | Impacto | Nota auditoría |
|-----|--------|---------|----------------|
| PAR-001 | PARCIAL | CRÍTICO | Linux canon `user/` OK; Windows rebranding + AppData pendiente |
| PAR-002 | OK | MEDIO | CLI `--version`, `--show-reset-log` |
| PAR-003 | PARCIAL | CRÍTICO | Linux `--reset-data` / `--do-reset-data`; validación cruzada W pendiente |
| PAR-004 | OK | CRÍTICO | Hooks / input history |
| PAR-005A | OK | CRÍTICO | Mecánica update Linux verificada por lectura |
| PAR-005B | PARCIAL | CRÍTICO | Canal release / comunicación usuario |
| PAR-006 | PARCIAL | MEDIO | install.sh vs Inno |
| PAR-007 | PARCIAL | BAJO | Preflight |

### Bloques previstos (bitácora) — Linux

| Bloque | Estado Linux (observado) |
|--------|--------------------------|
| ZIP / flock / seguridad | Implementado (`safe_*`, `update.sh`, `security_model.md`) |
| Canon `user/` + migraciones | Implementado (`data_version` 5, `data_migrations.py`) |
| GPL + pyproject | Implementado |
| Portar a Windows | Pendiente (checklist rebranding bitácora L377–385) |

---

## Plan de remediación priorizado

| Prioridad | ID | Acción | Dimensión |
|-----------|-----|--------|-----------|
| P0 | SEC-002 | Snapshot inmutable o lock en `input_state` | 1, 2 (CWE-362) |
| P0 | SEC-001 | Unificar extracción update con `safe_zip_extract` o límites equivalentes | 2 (CWE-22/400) |
| P1 | SEC-003 | `fcntl` o `O_EXCL` en `.migration_lock` | 2 |
| P1 | OPS-001 | CI mínima: `test_zip_security`, SDL dummy menú, `check_doc_links` (si se autoriza ejecutar scripts fuera de política read-only) | 4, 5 |
| P1 | — | Cerrar PAR-001/003 en Windows (bitácora B.3) | 8 |
| P2 | ARCH-001 | Refactor vertical `main.py` / menú | 1 |
| P2 | OPS-002 | CHANGELOG; política PAR-005B | 3, 7 |
| P2 | OPS-003 | `ruff`/`radon` en `pyproject` o CI | 1, 5 |

---

## Conclusión

| Pregunta | Respuesta |
|----------|-----------|
| ¿Software serio mantenible? | **Sí**, con deuda en entrypoints y automatización |
| ¿Hardened / enterprise? | **No** |
| ¿Uso local / clon confiable? | **Sí** |
| ¿Release amplio OSS sin más trabajo? | **No** (`LOCAL_READY`, no `CI_MIN` / `PARITY_CORE`) |

La auditoría confirma **intencionalidad arquitectónica** (contrato datos, migraciones, seguridad ZIP perfil, documentación alineada). Los hallazgos pendientes son de **madurez** (concurrencia, CI, paridad Windows, supply chain), no de improvisación total.

---

## Apéndice: comandos y herramientas

### Ejecutados (readonly)

- `git rev-parse --short HEAD`, `git log -1`
- `find arcade/engine -name '*.py' | wc -l`
- `wc -l` en archivos clave
- `rg` / grep: `shell=True`, `eval`, `subprocess`, `TODO`, secretos, `threading`, `fcntl`

### No ejecutados (por alcance o entorno)

- `./install.sh`, `scripts/update.sh`, `scripts/run.sh`, `scripts/check_doc_links.py`
- Cualquier archivo bajo `tests/`
- `python -m venv`, `pip install -r requirements.txt`
- `ruff`, `radon`, `bandit`, `pip-audit`, `pytest`

---

## Referencias internas

- [Contrato de auditoría v1](../developer/audit_contract_v1.md)
- [Registro global de hallazgos](findings_registry.md)
- [Matriz de paridad técnica](parity_matrix.md)
- [Modelo de seguridad](../security/security_model.md)
- [Contrato de datos v1](../developer/data_contract_v1.md)
- [Bitácora de paridad](bitacora.md)
- [Matriz reset](../developer/reset_matrix.md)
- [Plan Fase 2 Windows](windows_parity_rollout.md)
