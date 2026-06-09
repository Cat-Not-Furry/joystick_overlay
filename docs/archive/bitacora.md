# Bitácora de variantes HUD / Joystick Overlay

## Nota de checkout (leer primero)

- **`hud_owerlay` (Windows)** y **`hud_overlay` (Linux, slug Git)** son **repositorios Git distintos**; el **nombre de producto** orientado al usuario es **Joystick Overlay**. Esta bitácora puede vivir en ambos repos como contrato de paridad.
- Si este archivo está en **Linux (`hud_overlay`)**, la **Parte B** es el inventario verificable en el árbol actual; la **Parte A** describe Windows y debe contrastarse con **`hud_owerlay`**.
- Si está en **Windows (`hud_owerlay`)**, ocurre lo inverso: la **Parte A** es la fuente verificable local; la **Parte B** resume Linux y no se valida contra los archivos de ese árbol.
- Al copiar esta bitácora a Windows, **no invertir los IDs** (`PAR-*`, `L-*`, `W-*`): solo invertir qué parte es verificable localmente y completar la evidencia Windows.

## Propósito y límites del documento

- Registra **qué** se hace o debe hacerse, **por qué** importa y **en qué estado** está respecto a la paridad entre variantes.
- **No** describe procedimientos largos (comandos, pasos de build). Eso vive en la documentación de cada repo (p. ej. `README.md` en Linux; empaquetado Windows en `constructor.md` cuando exista en `hud_owerlay`).
- **Paridad** = equivalencia **funcional y contractual observable** (no equivalencia interna de implementación). Ver [audit_contract_v1.md](../developer/audit_contract_v1.md) § Modelo de paridad por capas.
- Linux (`hud_overlay`) define **invariantes** upstream; Windows (`hud_owerlay`) hace **adaptación contractual** del mismo producto (no «copiar Linux» línea a línea).
- Clasificación por sistema: [parity_matrix.md](parity_matrix.md) (`tipo`, `paridad`, `drift_permitido`, `motivo_plataforma`).

## Registro por bloques (antes / después / motivo)

Para mejoras alineadas al plan unificado y para que el historial sea auditable:

- Cada **bloque** de trabajo cerrado (o cada entrega lógica equivalente a un PR) debe quedar anotado con **cuatro columnas**: **Bloque** (nombre corto), **Antes**, **Después**, **Motivo** (una sola línea de texto).
- Si el cambio toca paridad entre repos: en la misma fila o justo debajo, indicar **PAR-*** afectado y, si aplica, **transición de estado** del tablero (p. ej. `ROTO → PARCIAL`).
- Las filas pueden vivir **aquí** (tabla acumulativa) y/o repetirse como línea en **Historial de sincronización** con el mismo criterio.

### Plantilla (copiar y rellenar)

| Bloque | Antes | Después | Motivo |
|--------|-------|---------|--------|
| | | | |

### Ejemplo de redacción (formato; no afirma un hecho concreto hasta fechar la implementación)

| Bloque | Antes | Después | Motivo |
|--------|-------|---------|--------|
| Datos canon + espejo perfiles | Un solo `USER_DIR` bajo `~/.local/share/...` para perfiles operativos. | Perfiles operativos bajo `PROJECT_ROOT/user/profiles/`; copia de respaldo en `~/.local/share/joystick_overlay/user/profiles/` tras cada guardado. | Portable + recuperación si se borra el árbol del proyecto. |

### Bloques previstos por el plan fusionado (rellenar al implementar)

| Bloque | Antes | Después | Motivo |
|--------|-------|---------|--------|
| Estilos e iconos (`mvs` / `cps` / `ns` / `ps` / `xbox`, `icon_pack_locked`) | `playstation`/`switch`/`xbox` sin packs dedicados. | Estilos canónicos + `icon_stem_for_label` / mapeos en `config`; menú sincroniza pack si no fijado. | PAR-001 estética HUD alineada a packs en disco. |
| Resolver y caché sin I/O en caliente | `resolve_icon` releía JSON en cada botón. | Caché de metadatos por perfil + rutas resueltas; invalidación en guardado. | Cumplir A.5 sin I/O repetida. |
| Índice de perfiles (FS fuente de verdad, esquema mínimo) | Índice con `path`; entradas huérfanas. | `profiles_index.json` solo `id`+`name`; reconciliación con carpetas bajo `user/profiles/`. | A.1: FS autoridad. |
| Nombre libre de perfil + menú Renombrar | Solo `name` implícito al crear. | Acción «Renombrar perfil» edita `name`; `id` sigue siendo carpeta. | A.2 UI sin tocar rutas. |
| Editor HUD: joystick y cada botón independientes (A.12) | Grupos `dirs_group` / `buttons_group` en `hud_layout_editor`. | `button_positions` por label + stick; `button_pixel_offsets` en render. | A.12 granularidad en pantalla. |
| Migración / reset / CLI / preflight | `USER_DIR` solo XDG; reset borraba todo. | Canon `PROJECT_ROOT/user/`; copia XDG→proyecto si falta índice; reset con `pre_reset_*`; bump `data_version` 3. | Híbrido C + A.7/A.8. |
| Pantalla «Backups locales» (bienvenida + menú) | Copias siempre antes de sobrescribir perfil. | Primera ejecución pregunta Si/No; si No avisa que puede activar en Configuración; `backups_enabled` en índice y toggle «Backups locales». | Consentimiento y control del usuario (PAR-UX backups). |
| Espejo XDG `.../joystick_overlay/user/profiles/` (opcional) | Espejo siempre tras cada guardado. | Misma bienvenida + toggle «Espejo datos sistema»; `xdg_mirror_enabled` en índice; si No no se escribe bajo `~/.local/share/...` (paridad ruta Windows en `%LOCALAPPDATA%\joystick_overlay\...`). | No romper convención XDG como ubicación posible; no obligar escritura fuera del proyecto. |
| README + ZIP perfiles (`bindings/`) | README y notas viejas: ZIP con `profile.json` + `icons/`; `hud_layout` solo en `profile.json`. | README documenta ZIP con `bindings/*.json` (cuatro nombres canónicos), metadato `profile_version` en export; HUD/iconos por formato en sidecars (`arcade/engine/profiles/`). | Documentación única para import/export y portado Windows. |
| Seguridad ZIP / FS / updater | `extractall` + chequeo debil; resolver con cwd; `cp -a` en update; sin lock al guardar indice. | `safe_zip_extract`; iconos import bajo `user/profiles/<id>/icons/`; `safe_paths` + resolver endurecido; `update.sh` scan + `cp -rL` + `flock`; `profiles_index.lock` al guardar; [security_model.md](../security/security_model.md). | Reducir ZIP slip / symlinks / traversal y carreras en datos de usuario. |
| Licencia GPLv3 + metadatos paquete | Sin `LICENSE` en raíz o sin `license` en `pyproject.toml`. | Archivo `LICENSE` (texto GPL-3) en raíz; `license = { file = "LICENSE" }` en `pyproject.toml`; `MANIFEST.in` incluye `LICENSE`; README enlaza a [LICENSE](../../LICENSE). | Redistribución y sdist completos para clones y Windows. |

## Ámbitos

| Variante | Repositorio / árbol | Rol de esta bitácora en cada checkout |
|----------|---------------------|----------------------------------------|
| Windows | `hud_owerlay`; producto **Joystick Overlay** | Inventario principal Windows; cola hacia Linux. |
| Linux | `hud_overlay` (slug Git); producto **Joystick Overlay**; rutas externas `joystick_overlay` | Inventario principal Linux; cola hacia Windows como adaptación contractual. |

---

## Gobernanza de auditoría y hallazgos técnicos

Normas y estado cross-repo (no sustituyen este documento):

| Documento | Rol |
|-----------|-----|
| [audit_contract_v1.md](../developer/audit_contract_v1.md) | Severidad P0–P3, capas canónica/adaptable/prohibida, ladder, plantilla |
| [findings_registry.md](findings_registry.md) | IDs globales SEC/REL/ARCH/OPS/DOC |
| [parity_matrix.md](parity_matrix.md) | Sistema × Linux × Windows (`matrix_version: 2`, columnas de capa) |
| [audit_report.md](audit_report.md) | Instantánea por commit (no sobrescribe PAR ni registry) |

**Reglas:**

- **`PAR-*`** = paridad de producto (tablero y pares más abajo).
- **`SEC-*` / `REL-*` / `ARCH-*` / `OPS-*` / `DOC-*`** = hallazgos técnicos globales; la bitácora solo **referencia** el ID, no redefine el problema.
- **`L-*` / `W-*`** = evidencia local o ítem de cola, no IDs de hallazgo global.
- Reclasificación **por sistema** (no por diff de código): [parity_matrix.md](parity_matrix.md) — campos `tipo` / `drift_permitido`.

### Hallazgos globales referenciados (Linux, activos)

| ID | P | global_status | Registry |
|----|---|---------------|----------|
| SEC-001 | P0 | PARCIAL | [SEC-001](findings_registry.md#sec-001--pipeline-zip-inconsistente) |
| SEC-002 | P0 | PARCIAL | [SEC-002](findings_registry.md#sec-002--input_state-sin-sincronización) |
| SEC-003 | P1 | PARCIAL | [SEC-003](findings_registry.md#sec-003--lock-de-migración-no-atómico) |
| OPS-001 | P1 | PARCIAL | [OPS-001](findings_registry.md#ops-001--sin-cicd) |
| OPS-002 | P2 | PARCIAL | [OPS-002](findings_registry.md#ops-002--canal-release--changelog) |
| ARCH-001 | P2 | PARCIAL | [ARCH-001](findings_registry.md#arch-001--monolitos-entrypoints-linux) |

### Anexo isomórfico (8 secciones)

Resumen → Restricciones → Hallazgos (registry) → Riesgo residual → Paridad (matrix) → Plan P0–P3 → Confianza → Estado release. Detalle en [audit_contract_v1.md](../developer/audit_contract_v1.md) § Estructura isomórfica.

---

## Estado global de paridad (tablero ejecutivo)

Lectura rápida para decidir prioridades de implementación y evitar desviaciones entre repos.

| Área | Estado | Impacto |
|------|--------|---------|
| Core (input history + hooks) | OK | CRÍTICO |
| Datos de usuario y versionado runtime | PARCIAL | CRÍTICO |
| Reset de datos en dos fases | PARCIAL | CRÍTICO |
| Actualización en campo (política de producto / PAR-005B) | PARCIAL | CRÍTICO |
| CLI de soporte | PARCIAL | MEDIO |
| Instalación y accesos de entrada | PARCIAL | MEDIO |
| Preflight UX (mensajes preventivos) | PARCIAL | BAJO |

### Semáforo de estados (obligatorio)

- `OK`: ambas variantes cumplen el mismo resultado de producto.
- `PARCIAL`: existe implementación en ambos lados, pero falta equivalencia funcional o cierre de producto.
- `ROTO`: solo una variante cumple, o la diferencia afecta directamente al usuario.

Para auditorías técnicas y dimensiones no evaluadas, usar además `PENDIENTE`, `N/E` y `DRIFT` según [audit_contract_v1.md](../developer/audit_contract_v1.md). El release readiness se expresa con el ladder (`LOCAL_READY` … `HARDENED`), no con veredictos sueltos («Condicionado», «no listo»).

### Clasificación de impacto (obligatoria)

- `CRÍTICO` (Core parity): rompe comportamiento visible, soporte o continuidad del producto.
- `MEDIO` (Operational parity): afecta operación diaria (CLI, instalación, actualización básica).
- `BAJO` (Nice-to-have): mejoras de UX o robustez que no rompen el flujo principal.

## Pares de paridad (contrato ejecutable)

Esta tabla es la fuente de verdad para decidir trabajo cross-repo. Si un `PAR-*` está `ROTO`, no debe cerrarse sprint de paridad sin plan activo para ese par.

| ID | Windows | Linux | Estado | Impacto | tipo | drift_permitido | Nota |
|----|---------|-------|--------|---------|------|-----------------|------|
| PAR-001 | `W-20260425-001` | `L-20260425-001-P` | PARCIAL | CRÍTICO | Adapted | Sí | Persistencia lógica alineada; rutas AppData vs `user/` — ver matrix fila Persistencia. |
| PAR-002 | `W-20260425-002` | `L-20260425-002-P` | OK | MEDIO | Canonical | No | `--version`, `--show-reset-log`. |
| PAR-003 | `W-20260425-003` | `L-20260425-003-P` | PARCIAL | CRÍTICO | Canonical | No | Reset dos fases en código (E1); validación cruzada UX Windows pendiente (**W-OPS-001**). |
| PAR-004 | `W-20260425-004` | `L-20260425-004` | OK | CRÍTICO | Canonical | No | Contrato de eventos/hooks alineado. |
| PAR-005A | `W-UPD-ZIP-001` / `cli --update --zip` | `L-OPS-003-P-mechanics` | OK | CRÍTICO | Transitional | No | Mecánica L/W OK (`safe_zip_extract` runtime + install W 0.3.2); PAR-005B producto en campo sigue PARCIAL. |
| PAR-005B | `W-OPS-003` (producto en campo) | `L-OPS-003-P-product` | PARCIAL | CRÍTICO | Canonical | No | Canal release / comunicación usuario (OPS-002). |
| PAR-006 | `W-20260426-001` | `L-20260426-001` | PARCIAL | MEDIO | Adapted | Sí | Instalación: `install.sh` vs `install/windows/`. |
| PAR-007 | `W-PAR-L004` | `L-PREFLIGHT` | PARCIAL | BAJO | Canonical | No | Preflight y mensajes preventivos. |

### Regla de ejecución de paridad

- Prioridad operativa fija: primero `CRÍTICO`, luego `MEDIO`, después `BAJO`.
- No cerrar iteración de paridad con `PAR-*` críticos en `ROTO` sin registrar decisión explícita en historial.
- Cada cambio en un repo debe actualizar, en la misma sesión, al menos: `PAR-*` afectado + estado de la cola cruzada (`A.3` o `B.3`).

### Regla de área PAR-005

- **PAR-005A** (mecánica) y **PAR-005B** (producto / actualización en campo) se evalúan por separado.
- El estado del área «Actualización en campo (política de producto)» sigue **PAR-005B**.
- PAR-005A debe estar **OK** antes de considerar cerrar PAR-005B en **OK**.

---

## Parte A — Windows (`hud_owerlay`)

Referencia verificada: release **0.3.2** (gate P0/P1/P2, 2026-05-26). Contraste con Linux `a19edb8`.

### A.1 Inventario por estado (solo qué)

En checkout **`hud_owerlay`**, la tabla siguiente es el inventario **Windows** (hecho = implementado aquí; pendiente = ops, release o paridad frente a la cola L→W de la Parte B). En Linux, esta Parte A es evidencia externa contrastada con el gate 0.3.2.

**Hecho — código y artefactos presentes en `hud_owerlay` (0.3.2)**

| ID | Qué | Evidencia en `hud_owerlay` |
|----|-----|----------------------------|
| W-20260425-001 | Persistencia Windows v1: `%LOCALAPPDATA%\joystick_owerlay\user\` o `user\` portable; manifiesto `install_manifest.json`; branding producto **Joystick Overlay**. | `arcade/engine/config/config.py`, `data_contract_windows_v1.md` (en `hud_owerlay`), `.joystick_version` **0.3.2** |
| W-20260425-002 | CLI única: `run`, `config`, `tournament`, `doctor`, `--version`, `--show-reset-log`, `--update --zip`. | `cli.py`, `doctor.py` |
| W-20260425-003 | Reset de datos en dos fases: `--reset-data` (interactivo) y `--do-reset-data` (worker). | `main.py` (parser y rutas tempranas) |
| W-20260425-004 | Historial de input y runtime de extensiones con hook de evento integrado al lector de input. | `arcade/engine/core/input_history.py`, `extensions_runtime.py`, `maps/input_reader.py` |
| W-20260426-001 | Instalación Python bajo `install/windows/` (`install_ops`, setup/uninstall); payload ZIP con `safe_zip_extract` (**SEC-001** mitigado). Legado Inno/`.bat` solo referencia histórica. | `install/windows/install_ops.py`, `install/joystick_overlay.ico`; [parity_matrix](parity_matrix.md) |
| W-UPD-ZIP-001 | Actualización desde ZIP (`cli --update --zip`, whitelist, preserva `user/`); UI *Actualizar overlay* en menú config. | `cli.py`, `arcade/engine/utils/safe_zip_extract.py`, `render/profile_config/handlers/advanced.py` |
| W-GATE-032 | Gate release 0.3.2: SEC-003 lock (`msvcrt`), CI (`.github/workflows/ci.yml`), política Win32 (ventana fija, sin opciones WM), ARCH-002 B (`render/profile_config/`). | `CHANGELOG.md` [0.3.2] Windows, `findings_registry.md`, `parity_matrix.md` |

**Pendiente — release/ops y revisión cruzada con Linux**

| ID | Qué |
|----|-----|
| W-OPS-001 | Validación manual en Windows real (Fase 4): build, instalación, desinstalación, reset, diagnóstico, ciclo HUD→Config→Salir. |
| W-OPS-002 | Cierre de release: GUID instalador, versión instalador ↔ runtime (runtime **0.3.2** alineado; falta cierre instalador publicado). |
| W-OPS-003 | Política y UX de actualización **en campo** (canal ZIP/build, comunicación usuario, post-update); mecánica cubierta por W-UPD-ZIP-001. |
| W-PAR-L001 | Paridad **instalación**: revisión cruzada de accesos HUD / config / torneo tras instalar (objetivo L-20260426-001). |
| W-PAR-L002 | Paridad **CLI / documentación**: superficie CLI alineada; cierre con VM/instalador pendiente (objetivo L-20260426-002). |
| W-PAR-L003 | Paridad **actualización**: revisión cruzada flujo ZIP + log `user/update.log` vs `update.sh` Linux (objetivo L-20260426-003). |
| W-PAR-L004 | Opcional: **preflight** de instalación con mensajes claros si el entorno no es apto. |

### A.2 Registro de ítems (plantilla largo plazo)

```text
[ID]  Estado: hecho | pendiente | descartado
      Fecha: YYYY-MM-DD
      Qué: (una frase, resultado observable)
      Por qué: (negocio / riesgo / paridad)
      Portabilidad Linux: pendiente | en_progreso | portado | n/a | descartado
      Evidencia si hecho: ruta o módulo (no comandos)
```

**W-20260425-001** — Estado: `hecho` (Windows)  
Fecha: 2026-04-25; revisado 2026-05-26  
Qué: Persistencia de perfiles y metadatos bajo contrato Windows v1; versión runtime **0.3.2** alineada.  
Por qué: Instalación en `Program Files` no debe requerir escritura en runtime.  
Portabilidad Linux: `portado` (Linux: `PROJECT_ROOT/user/` + `.joystick_version`; espejo XDG opcional).  
Evidencia Windows: `arcade/engine/config/config.py`, `data_contract_windows_v1.md`, `.joystick_version` (en `hud_owerlay`).

**W-20260425-002** — Estado: `hecho` (Windows)  
Fecha: 2026-04-25; revisado 2026-05-26  
Qué: Diagnóstico y utilidades CLI (`run`, `config`, `tournament`, `doctor`, `--version`, `--show-reset-log`, `--update --zip`).  
Por qué: Soporte y reproducibilidad.  
Portabilidad Linux: `portado` (misma superficie observable; `doctor` adaptado a Win32).  
Evidencia Windows: `cli.py`, `doctor.py` (en `hud_owerlay`).

**W-20260425-003** — Estado: `hecho` (código); validación UX `pendiente`  
Fecha: 2026-04-25; revisado 2026-05-26  
Qué: Borrado seguro de datos con `--reset-data` y worker `--do-reset-data`.  
Por qué: Evitar bloqueos de archivos y pérdida de foco en captura.  
Portabilidad Linux: `portado` (`main.py`: `--reset-data`, `--do-reset-data`). Cierre PAR-003: **W-OPS-001**.  
Evidencia Windows: `main.py` (en `hud_owerlay`).

**W-20260425-004** — Estado: `hecho` (Windows)  
Fecha: 2026-04-25; revisado 2026-05-26  
Qué: Trazabilidad de input y extensión por hooks sin acoplar a la UI.  
Por qué: Base para análisis y extensiones.  
Portabilidad Linux: `portado`.  
Evidencia Windows: `arcade/engine/core/input_history.py`, `extensions_runtime.py`, `maps/input_reader.py`.

**W-20260426-001** — Estado: `hecho` (Windows)  
Fecha: 2026-04-26; revisado 2026-05-26  
Qué: Instalador Python (`install/windows/`); extracción payload con `safe_zip_extract` (**SEC-001** mitigado).  
Por qué: Un solo lugar para empaquetado Windows acorde al port.  
Portabilidad Linux: `n/a` (`install.sh` + `.desktop` en Linux).  
Evidencia Windows: `install/windows/install_ops.py`, `install/joystick_overlay.ico`.

**W-UPD-ZIP-001** — Estado: `hecho` (Windows)  
Fecha: 2026-04-26; revisado 2026-05-26  
Qué: Actualización desde ZIP con `extract_zip_safely`, whitelist y preservación de `user/`; entrada UI en menú config.  
Por qué: Base técnica PAR-005A; W-OPS-003 cubre política de producto.  
Portabilidad Linux: mecánica equivalente (`update.sh` + UI Linux).  
Evidencia Windows: `cli.py`, `render/profile_config/handlers/advanced.py`, `safe_zip_extract.py`.

**W-GATE-032** — Estado: `en_progreso` (código cerrado; Fase 4 humano pendiente)  
Fecha: 2026-05-26  
Qué: Gate release Windows **0.3.2** — SEC-001 install, SEC-003 lock, REL-001, CI, update UI, política Win32 sin WM tiling, ARCH-002 B.  
Por qué: Paridad contractual **Adapted** frente a Linux `a19edb8`.  
Portabilidad Linux: `n/a` (Linux define invariantes upstream).  
Evidencia Windows: `CHANGELOG.md` [0.3.2], `findings_registry.md`, `parity_matrix.md`.

**W-PAR-L001** — Estado: `pendiente`  
Fecha: —  
Qué: Revisión cruzada post-instalación: usuario localiza HUD, config y torneo con la misma claridad relativa que en Linux.  
Por qué: Paridad de producto entre repos.  
Portabilidad Linux: ver cola B.3 (`L-20260426-001`).  
Evidencia: — (checklist / notas de release).

**W-PAR-L002** — Estado: `revisión documental hecha` (VM instalador pendiente)  
Fecha: 2026-05-18; revisado 2026-05-26  
Qué: Superficie CLI y `docs/user/` Win32 alineadas con intención Linux.  
Por qué: PAR-002 OK; cierre operativo con instalador en VM.  
Portabilidad Linux: ver cola B.3 (`L-20260426-002`).  
Evidencia Windows: `cli.py`, `docs/user/installation.md`, `docs/user/quick_start.md`.

**W-PAR-L003** — Estado: `en_progreso`  
Fecha: 2026-05-26  
Qué: Revisión cruzada del flujo de actualización (selector ZIP + `cli --update --zip` + log).  
Por qué: Paridad de intención con `update.sh` / UI Linux.  
Portabilidad Linux: ver cola B.3 (`L-20260426-003`).  
Evidencia Windows: menú *Actualizar overlay*, `user/update.log`.

**W-PAR-L004** — Estado: `pendiente` (opcional)  
Fecha: —  
Qué: Preflight de instalación o primer arranque con mensajes claros si el entorno no es apto.  
Por qué: Reducir soporte silencioso.  
Portabilidad Linux: ver B.3 (`L-PREFLIGHT`).  
Evidencia: —

**W-OPS-001** — Estado: `pendiente`  
Fecha: —  
Qué: Cierre de validación manual en entorno Windows real.  
Por qué: Garantía antes de distribución.  
Portabilidad Linux: `n/a`.  
Evidencia: —

**W-OPS-002** — Estado: `en_progreso`  
Fecha: 2026-05-26  
Qué: Identidad de instalación y versión publicada alineadas con política de release.  
Por qué: Upgrades y soporte.  
Portabilidad Linux: `n/a`.  
Evidencia Windows: `.joystick_version` / `pyproject.toml` / `version.txt` → **0.3.2**; `scripts/check_version_alignment.py` en CI.

**W-OPS-003** — Estado: `pendiente` (producto en campo; PAR-005B)  
Fecha: —  
Qué: Política de actualización para usuarios finales (canal ZIP/build, comunicación, post-update).  
Por qué: W-UPD-ZIP-001 cubre mecánica; falta cierre de producto en campo.  
Portabilidad Linux: `en_progreso` (L-OPS-003-P).  
Evidencia Windows: `cli.py --update --zip`, `constructor.md`, `docs/user/installation.md`.

### A.3 Cola Windows → Linux (qué portar; sin cómo)

*Criterios de cierre, verificación y fechas: ver cola inversa **B.3** (Linux → Windows). Esta tabla resume intención W→L sin duplicar columnas.*

| ID origen | Qué debe existir en Linux | Estado cola |
|-----------|---------------------------|-------------|
| W-20260425-001 | Misma política de datos de usuario y versión coherente con instalación Linux. | En progreso (PAR-001; ver B.3) |
| W-20260425-002 | Misma superficie de diagnóstico y flags de soporte acordados donde aplique. | Portado (Linux); revisión doc Windows — PAR-002 OK |
| W-20260425-003 | Misma semántica de reset en dos fases. | Portado (Linux); validación cruzada Windows — PAR-003 / B.3 |
| W-20260425-004 | Mismo contrato de evento e historial + hooks. | Portado |
| W-20260426-001 | — | n/a |
| W-UPD-ZIP-001 | Equivalente funcional de aplicar ZIP acotado. | Portado mecánica L/W (PAR-005A OK); producto — PAR-005B |
| W-GATE-032 | — | n/a (gate documental W 0.3.2) |
| W-OPS-003 | Equivalente funcional de actualización operativa para usuarios finales. | En progreso (PAR-005B; ver B.3) |

---

## Parte B — Linux (`hud_overlay`)

### B.1 Inventario por estado (solo qué; verificado en este árbol)

Esta sección es la **base Linux** que se pasa a Windows como contrato observable. En `hud_owerlay`, no debe leerse como instrucciones para copiar implementación, sino como lista de invariantes y evidencias Linux a contrastar con la adaptación Windows.

**Hecho**

| ID | Qué |
|----|-----|
| L-20260426-001 | Instalación orientada a usuario: `install.sh` (venv, launcher **`joystick-overlay`**, `.desktop`, icono `joystick_overlay.ico`, variables `JOYSTICK_OVERLAY_ASSUME_GRAPHICS` / `JOYSTICK_DESKTOP_TERMINAL`). |
| L-20260426-002 | Lanzamiento unificado: `run.sh` → `cli.py` con comandos `run`, `config`, `tournament`, `doctor`, `-h`/`--help`. |
| L-20260426-003 | Actualización: `update.sh` (git y modo ZIP con whitelist); desde UI «Actualizar overlay» (`render/profile_config_menu.py`). |
| L-20260425-004 | Historial de input y hooks (`core/input_history.py`, `core/extensions_runtime.py`, integración en `main.py`). |
| L-RUNTIME-V | Archivo `.joystick_version` en raíz como referencia de versión runtime (contrato [`../developer/data_contract_v1.md`](../developer/data_contract_v1.md); README raíz). |

**Pendiente / parcial (paridad con Windows u ops)**

| ID | Qué |
|----|-----|
| L-20260425-001-P | Linux: canon `PROJECT_ROOT/user/` + `.data_version` y migraciones cerrados; pendiente cierre PAR-001 cross-repo (Windows: rebranding + espejo `%LOCALAPPDATA%`). |
| L-20260425-002-P | Resuelto en Linux: `cli.py` ya incluye `--version` y `--show-reset-log`; validar espejo documental en Windows. |
| L-20260425-003-P | Hecho en código Linux (reset dos fases); validación cruzada Windows pendiente (PAR-003). |
| L-OPS-003-P | Política de actualización en campo para usuarios sin git (ZIP documentado; falta cierre ops tipo W-OPS-003). |

### B.2 Registro de ítems Linux (plantilla)

**L-20260426-001** — Estado: `hecho`  
Fecha: 2026-04-26  
Qué: Instalación accesible (launcher + menú + comprobaciones de entorno gráfico).  
Por qué: Paridad funcional con «instalado y localizable» en Windows.  
Portabilidad Windows: `pendiente` (revisión cruzada accesos; **W-OPS-001** / W-PAR-L001).  
Evidencia: `install.sh`, `install/joystick-overlay.desktop`, `install/joystick-overlay-config.desktop`, `install/joystick-overlay-tournament.desktop`, `install/joystick_overlay.ico`.

**L-20260426-002** — Estado: `hecho`  
Fecha: 2026-04-26  
Qué: Punto de entrada CLI para ejecutar HUD, config, torneo y doctor.  
Por qué: Paridad con superficie operativa Windows.  
Portabilidad Windows: `n/a` (misma idea, otra forma).  
Evidencia: `run.sh`, `cli.py`, `doctor.py`.

**L-20260426-003** — Estado: `hecho`  
Fecha: 2026-04-26  
Qué: Actualización del código sin mezclar datos sensibles por defecto (whitelist / git).  
Por qué: Paridad de intención con W-OPS-003.  
Portabilidad Windows: `en_progreso` (W: `cli --update --zip` + UI menú; revisión cruzada **W-PAR-L003**).  
Evidencia: `update.sh`, `render/profile_config_menu.py` (Linux); `cli.py`, `render/profile_config/` (Windows).

**L-20260425-004** — Estado: `hecho`  
Fecha: 2026-04-25  
Qué: Historial estructurado y hooks de extensión en el loop de input.  
Por qué: Paridad con W-20260425-004.  
Portabilidad Windows: `portado` (origen Windows; mantener contrato).  
Evidencia: `core/input_history.py`, `core/extensions_runtime.py`, `main.py`, `maps/input_reader.py`.

**L-20260425-001-P** — Estado: `hecho (Linux); paridad cross-repo pendiente`  
Fecha: 2026-05-03 (canon Linux); — (cierre PAR-001)  
Qué: Canon operativo bajo `PROJECT_ROOT/user/`, versionado (`data_version`, `.joystick_version`), migraciones y espejo opcional XDG; equivalente funcional a W-20260425-001.  
Por qué: Contrato portable + recuperación; PAR-001 sigue PARCIAL hasta rebranding y espejo AppData en Windows.  
Portabilidad Windows: `pendiente` (rebranding checklist § «Checklist rebranding»).  
Evidencia Linux: `config/config.py`, `core/data_migrations.py`, `profiles/profile_store.py`, acta 2026-04-27.

**L-20260425-002-P** — Estado: `hecho (cerrado en código)`  
Fecha: 2026-05-03  
Qué: Flags CLI `--version` y `--show-reset-log` alineados con Windows.  
Por qué: Soporte homogéneo entre variantes.  
Portabilidad Windows: `hecho` (asumido en Windows).  
Evidencia: `cli.py` (`get_runtime_version`, `RESET_LOG_PATH`).  
Nota histórica: [OBSOLETO] Texto anterior afirmaba «ausencia en cli.py»; corregido por verificación de código.

**L-20260425-003-P** — Estado: `hecho (cerrado en código)`  
Fecha: 2026-05-03  
Qué: Reset de datos en dos fases (`--reset-data` / `--do-reset-data`).  
Por qué: Misma semántica de seguridad operativa.  
Portabilidad Windows: `hecho` (asumido en Windows); **pendiente validación cruzada Windows** para PAR-003.  
Evidencia: `main.py` (parser temprano y `_do_reset_data`).  
Nota histórica: [OBSOLETO] Texto anterior afirmaba ausencia de `reset-data` en `main.py`; corregido por verificación de código.

**L-OPS-003-P** — Estado: `en_progreso`  
Fecha: —  
Qué: Cierre de política de actualización para usuarios finales (más allá de git/zip en repo).  
Por qué: Paridad con W-OPS-003.  
Portabilidad Windows: `en_progreso` (mecánica W alineada; producto en campo pendiente **W-OPS-003**).  
Evidencia: `update.sh`, UI de actualización; `cli.py --update --zip` en Windows.

### B.3 Cola Linux → Windows (qué revisar en Windows; sin cómo)

*Ningún ítem sin **criterio de cierre** explícito.*

| ID / objetivo | Qué revisar en Windows | Criterio de cierre | Verificación | Estado cola | Fecha |
|---------------|------------------------|--------------------|--------------|-------------|-------|
| L-20260426-001 | Accesos HUD / config / torneo tras instalación. | Menú/accesos visibles **Joystick Overlay**: abrir ejecutable principal, configuración y torneo sin línea de comandos | Instalador + acceso directos | Pendiente revisión cruzada | — |
| L-20260426-002 | CLI / entradas de producto. | Misma superficie observable: comandos equivalentes **`joystick-overlay`** y subcomandos documentados (`config`, `tournament`, `doctor`, `--version`, `--help`) | Lista en README instalador vs `doctor` | Pendiente revisión cruzada | — |
| L-20260426-003 | Update + logs desde UI donde exista. | `Actualizar overlay` no borra `USER_DIR` del proyecto; log en `user/update.log` o ruta documentada | Prueba manual + lectura log | En progreso (W: selector ZIP + `cli --update --zip` 0.3.2) | 2026-05-26 |
| L-20260426-002 (install UX) | Preflight instalación. | Mensaje claro si no hay sesión gráfica (equivalente funcional a `install.sh`, no igualdad API) | Instalador en máquina headless-safe | Pendiente revisión cruzada | — |
| L-PREFLIGHT | Validación previa arranque. | Equivalente espíritu `install.sh` / doctor | Lista smoke | Opcional | — |

---

## Historial de sincronización (solo hitos)

| Fecha | Qué |
|-------|-----|
| 2026-04-26 | Definición de bitácora solo-QUÉ; inventario Windows; colas explícitas. |
| 2026-04-26 | Ajuste por checkout: Parte B inventariada desde `hud_overlay`; colas W↔L alineadas a evidencia de código; ítems paridad CLI/reset/datos. |
| 2026-04-26 | Parte A Windows: tablas hecho/pendiente con evidencia en `hud_owerlay`; ítems W-UPD-ZIP-001 y W-PAR-L*; repos explícitos como árboles distintos. |
| 2026-04-26 | Impacto: PAR-001 \| Transición: ROTO -> PARCIAL \| Evidencia: `config/config.py`, `core/data_migrations.py`, `profiles/profile_store.py`. |
| 2026-04-26 | Impacto: PAR-002 \| Transición: PARCIAL -> OK \| Evidencia: `cli.py`. |
| 2026-04-26 | Impacto: PAR-003 \| Transición: ROTO -> PARCIAL \| Evidencia: `main.py`, `cli.py`. |
| 2026-04-26 | Impacto: PAR-005 \| Transición: ROTO -> PARCIAL \| Evidencia: `update.sh`, `render/profile_config_menu.py`. *(Histórico; ver 2026-05-13 para desglose PAR-005A/B.)* |
| 2026-04-27 | Bloque: gobernanza de bitácora \| Antes: solo ítems narrativos y tablero PAR \| Después: sección «Registro por bloques» con plantilla antes/después/motivo y tabla de bloques previstos del plan fusionado \| Motivo: trazabilidad por entrega y alineación con `control_estilo_e_iconos_736cb9a6.plan.md`. |
| 2026-05-13 | Impacto: PAR-005 \| Transición: mecánica ROTO→**OK** (**PAR-005A**); producto en campo sigue **PARCIAL** (**PAR-005B**). Tablero «Actualización en campo» = PAR-005B, no ROTO global. Evidencia: `update.sh`, `safe_zip_extract`, `profiles_index.lock`, [security_model.md](../security/security_model.md). |
| 2026-04-27 | Acta auditoría híbrida (`auditoría_todos_híbridos`): cierre de brechas shell/docs + tests de rutas; ver tabla siguiente. |
| 2026-05-03 | Rebranding producto **Joystick Overlay** en Linux canon: ejecutable/lanzador **`joystick-overlay`**, rutas externas `joystick_overlay`, archivo **`.joystick_version`**, variables **`JOYSTICK_*`**, `.desktop`/icono instalación; docs en **`docs/`** (contrato, matriz reset, esta bitácora). **Sin** migración automatizada desde rutas `hud_overlay`/`hud-overlay`/`HUD_*`; ver `docs/developer/data_contract_v1.md` §6. |
| 2026-05-03 | Seguimiento Windows (`hud_owerlay`): adaptar branding al contrato observable (binario **`joystick-overlay`**, rutas **`%LOCALAPPDATA%\joystick_overlay`** o equivalente acordado, instalador, iconos `.ico`, texto UI). Lista de chequeo técnico mínimo: (1) grep sin `hud-overlay` residual en lanzadores; (2) contrato datos Windows alineado donde aplique; (3) no reintroducir rescate desde árboles antiguos `hud_overlay` si el contrato vetado así. |
| 2026-05-13 | README reestructurado (hitos, usuario/streamer, ZIP **`bindings/`**); endurecimiento seguridad (ZIP perfil, resolver, `update.sh`, `flock`); sección README «Seguridad y archivos no confiables»; [security_model.md](../security/security_model.md); `tests/test_zip_security.py`; hitos narrativos archivados en [Archivo README (hitos antiguos)](#archivo-readme-hitos-antiguos). |
| 2026-05-14 | `LICENSE` (GPL-3) en raíz; `pyproject.toml` declara licencia vía archivo `LICENSE`; `MANIFEST.in` incluye `LICENSE`; README enlaza a licencia y corrige markdown (`bindings/`, modos de captura, `XDG_*` / `JOYSTICK_*`, tabla de entrypoints). |
| 2026-05-18 | Gobernanza auditoría isomórfica \| Antes: PAR + informe con vocabulario propio (Q-01, P0 sueltos) \| Después: `audit_contract_v1`, `findings_registry`, `parity_matrix`; W-20260426-001 alineado a `install/windows/` \| Motivo: IDs SEC globales y comparación Linux↔Windows sin sesgo. |
| 2026-05-18 | Modelo capas paridad v1.1 \| Antes: matrix sin `tipo`/`drift_permitido` \| Después: § capas en contrato + `parity_matrix` v2 + columnas PAR críticos \| Motivo: separar contrato observable de implementación (adaptación contractual upstream). |
| 2026-05-25 | Corrección para traslado a Windows \| Antes: mezcla de slug real, rutas externas y producto en la Parte Linux/Windows \| Después: `hud_overlay`/`hud_owerlay` como repos, `joystick_overlay` como ruta externa, Parte B marcada como base Linux verificable \| Motivo: copiar bitácora a Windows sin invertir IDs ni confundir implementación con contrato. |
| 2026-05-26 | Runtime agente + auditoría CC/menú \| Nuevo: [agent_runtime_v1.md](../developer/agent_runtime_v1.md) (`.venv`, `tests/.tvenv`, niveles B–E); [audit_cc_menu.md](audit_cc_menu.md); smoke `test_main_menu_smoke.py`; refactor CC `hud_layout_editor.py` \| Motivo: ejecución reproducible del agente sin tocar `venv/` de usuario. |
| 2026-05-26 | Hardening backlog P0/P1 \| SEC-001 `safe_zip_update_extract.py`; SEC-002 `input_state_sync`; SEC-003 `fcntl` migration lock; OPS-001 `.github/workflows/ci.yml`; merge `hud_layout.py`; REL-001 `check_version_alignment.py` \| Motivo: cerrar capa prohibida Linux y subir a `CI_MIN`. |
| 2026-05-26 | Beta **0.3.2** \| `CHANGELOG.md`; versión alineada; ruff en `pyproject.toml`; CI gates (pytest/links/version) + métricas warn (ruff/radon/CBO); `agent_runtime_v1` política `.venv`/`tests/.tvenv` permitidos \| Motivo: release beta Linux del fork a largo plazo. |
| 2026-05-26 | ARCH-001 Fase A \| Nuevo `arcade/engine/app/` (`ui/modals`, `secondary_flows`, `startup`, `debug_menu`, `window_mode`); modales compartidos con `profile_config_menu`; `main.py` fachada con re-exports \| Motivo: reducir monolito entrypoint sin romper tests/CLI. |
| 2026-05-26 | ARCH-001 Fase B \| `app/main_menu.py` (`show_main_menu`, `AppContext`, `MainMenuState`); `app/hud_setup.py` (setup interactivo/no interactivo + flujos mapeo teclado/joystick); `main.py` re-exporta menú y delega setup a `hud_setup` \| Motivo: separar menú y pre-sesión HUD del bucle principal; 29 pytest + smoke menú OK. |
| 2026-05-26 | ARCH-001 Fase C \| `app/hud_session/` (`events`, `context`, `loop`, `session`); `run_hud_session` extraído; `main.py` ~140 LOC (fachada + `main()`); re-export `run_hud_session` para `tournament.py` \| Motivo: aislar bucle HUD y orquestación de sesión; 29 pytest + import smoke tournament OK. |
| 2026-05-26 | ARCH-001 Fase D \| `run_main_menu_until_action` + `drive_menu_frame` / `drive_menu_loop_until_action` unifican menú; `show_main_menu` deprecado (wrapper en `main.py`); `main()` usa `_drive_menu_frame` compartido \| Motivo: eliminar bucle duplicado `show_main_menu` vs `MainMenuState`; gate auto 29 pytest + `check_doc_links` OK (`tests/.tvenv`, dummy). |
| 2026-05-26 | profile_config → `app/profile_config/` \| `menu.py`, `helpers.py`, `handlers/` (general, devices, visual, profiles_io, advanced); `change_icon` unificado; shim `render/profile_config_menu.py`; re-export en `render/__init__.py` \| Motivo: trocear monolito ~768 LOC; 29 pytest + `check_doc_links` OK. |
| 2026-05-26 | Windows Fase 2 (`hud_owerlay`) \| `linux_ref` → `a19edb8`; repos documentados en `windows_parity_rollout.md`; `parity_matrix` + `findings_registry` sincronizados \| Motivo: cierre auditoría comparativa L↔W (gate documental). |
| 2026-05-26 | Windows gate **0.3.2** (`hud_owerlay`, **W-GATE-032**) \| Antes: SEC-001 `install_ops.extractall`, REL-001 drift 1.0.0/0.3.1, sin CI, update vía `update.sh` inexistente, opciones WM en menú \| Después: `safe_zip_extract` install+runtime, versión 0.3.2, CI mínima, `cli --update --zip` + UI, política Win32 ventana fija, `render/profile_config/` \| Motivo: paridad contractual Adapted frente a Linux `a19edb8`; Fase 4 humano pendiente (**W-OPS-001**). |
| 2026-05-26 | Backlog priorizado \| Ítems 1–10 y 13 cerrados Linux; #5 editor usa `merged_layout_elements_for_profile`; [backlog_status.md](backlog_status.md) \| Motivo: inventario post ARCH-001/Fase 2; abiertos W SEC-001 install y WM real. |

### Checklist cierre ARCH-001 Fase D (menú / WM)

`execution_level`: D · `venv_used`: `tests/.tvenv` (auto), WM real pendiente humano

| # | Check | Entorno | Estado |
|---|-------|---------|--------|
| 1 | `pytest tests/test_main_menu_smoke.py` | `tests/.tvenv` + dummy | OK (2026-05-26) |
| 2 | Menú aislado dummy (misma ruta que smoke) | `tests/.tvenv` + dummy | OK vía ítem 1 |
| 3 | Menú sin parpadeo anómalo | WM real, sin dummy | **Pendiente humano** |
| 4 | `main.py`: HUD → config → salir | `.venv` o `tests/.tvenv` | **Pendiente humano** |
| 5 | Resize ventana en menú | WM real (Linux) / **N/A Win32** (ventana fija) | **Pendiente humano** (solo Linux WM) |
| 6 | `tournament.py` import / arranque | `tests/.tvenv` | OK import smoke |
| 7 | `doctor.py` | `tests/.tvenv` | OK (exit 0, avisos input esperados en sandbox) |

---

## Checklist rebranding para Windows (`hud_owerlay`)

Aplicar en el repo Windows al adaptar el canon observable Linux:

1. Exponer ejecutable/lanzador visible **`joystick-overlay`** y actualizar instalador/bat con semántica equivalente a Linux, no implementación idéntica.
2. Rutas `%LOCALAPPDATA%\...\joystick_overlay\...` alineadas al contrato de datos Windows (`data_contract_windows_v1.md` en `hud_owerlay`; Linux: [`data_contract_v1.md`](../developer/data_contract_v1.md)).
3. Archivo/o versión runtime **`.joystick_version`** (sin depender de `.hud_version`).
4. Prefijos **`JOYSTICK_`** para variables entorno públicas instalador/doctor.
5. Íconos y `.desktop`/accesos con nombre visible **Joystick Overlay**.

---

## Acta: auditoría `config-hybrid-storage` y `migrations-main-cli-tests` (2026-04-27)

Referencia: criterios del plan de auditoría (todos híbridos); el acta vive aquí para no duplicar el fichero del plan.

| Todo / ámbito | Veredicto | Evidencia | Seguimiento |
|---------------|-----------|-----------|---------------|
| **config-hybrid-storage** (runtime) | Completado | `config/config.py`: `PROJECT_USER_DIR`, `USER_DIR`, `get_user_dir`, `BACKUP_PROFILES_ROOT`, `ensure_contract_dirs`. Consumidores sin canon XDG hardcodeado como operativo. | Ninguno. |
| **config-hybrid-storage** (shell/docs) | Cerrado en esta entrega | `update.sh`: `USER_DIR="$BASE_DIR/user"`, `UPDATE_LOG` bajo ese árbol (alineado con `UPDATE_LOG_PATH`). `README.md`: ruta de log de actualización documentada como `user/update.log` + nota de espejo XDG. | Revisar si otros `.md` fuera del repo deben reflejar lo mismo. |
| **migrations-main-cli-tests** (Python) | Completado | `core/data_migrations.py`, `main.py`, `cli.py`, `doctor.py`, `configure.py`, `tournament.py` usan constantes de `config`. | Ninguno. |
| **migrations-main-cli-tests** (tests) | Completado | `tests/test_config_paths.py`: `get_user_dir` resuelve a `PROJECT_ROOT/user`; distinto de `BACKUP_PROFILES_ROOT`. `tests/test_hud_layout.py` incluye layout y rejilla MVS 8. | Ejecutar `python tests/test_config_paths.py` y `python tests/test_hud_layout.py` en CI o local al cambiar rutas. |
| Rutas legacy en código | Sin canon XDG como `USER_DIR` en `.py` / `.sh` | `_external_data_root()` usa **`joystick_overlay`** (espejo). Sin rescate automatizado rutas HUD antiguas (contrato v1 §6). | Ver `README.md` + [`data_contract_v1.md`](../developer/data_contract_v1.md). |
| UI menú + layout 4A (2026-05) | Renombre in-game **Joystick Overlay** / **Configuración** / **Salir**; caption `WINDOW_CAPTION_APP`; perfil `layout_four_variant_4a` (TAB en Dispositivos con 4 botones). | Agente no ejecuta pytest ni overlay; validar menú, TAB y HUD 4 vs 4A en local. | `main.py`, `config.py`, `profile_config_menu.py`, `hud_layout.py`. |

---

## Archivo README (hitos antiguos)

Texto conservado del README anterior (referencia histórica; el estado operativo está en Parte B y en el Historial).

### (Junio 2025) Cosas arregladas

Se redimensionó el tamaño de la ventana del fightstick. Se corrigió el tamaño de las letras y la interfaz acorde al tamaño de la ventana. Se corrigió el error de `main.py` (no cargaba `key_bindings.json`); ya no era necesario remapear en la opción del teclado salvo que se eliminara el archivo, igual que `joystick_bindings.json` (ambos en `json/` en esa época).

### (Agosto 2025) Cosas arregladas

Se arregló parcialmente la transparencia (necesita filtros como en OBS). Se mejoró el código: cada ventana se puede cerrar con el foco o con Esc. Se dio utilidad a `utils.py` para configuraciones repetidas. Se implementó un entorno virtual y `requirements.txt`.

### (Marzo 2026) Actualización

Apartado de fuente monoespaciada (`JetBrainsMono`, `FiraCode`, `Hack`; por defecto JetBrainsMono). UI en regular y etiquetas de botones en negrita. Fallback de fuente si falta el archivo local. Estilo PlayStation sin icono: abreviaciones (SQ, TRI, O, X, R1, L1, etc.). Opción «Seleccionar…» para icono con selector nativo Linux y validación máx. 512×512.

**Layout Hitbox y perfiles ZIP (marzo 2026 en README):** direccionales en curva descendente y botones de acción en curva ascendente; exportar/importar ZIP desde configuración con resolución de conflictos. Análisis de complejidad con `python tests/run_cyclomatic.py` (umbral CC≤10).

---

## Referencia «cómo» (fuera de esta bitácora)

- Linux: `README.md` (instalación, doctor, actualización, **Para el streamer** / OBS, tabla de hitos, [LICENSE](../../LICENSE)); contrato datos [`data_contract_v1.md`](../developer/data_contract_v1.md); índice [`README` de esta carpeta](../README.md) (antes `docs/INDEX.md`).
- Windows: `constructor.md` en `hud_owerlay` cuando exista en ese repo (no replicado obligatoriamente en Linux).
