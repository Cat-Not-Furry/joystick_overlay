# Bitácora de variantes HUD / Joystick Overlay

## Nota de checkout (leer primero)

- **`hud_owerlay` (Windows)** y **`hud_overlay` (Linux, slug Git)** son **repositorios Git distintos**; el **nombre de producto** orientado al usuario es **Joystick Overlay**. Esta bitácora puede vivir en ambos repos como contrato de paridad.
- Si este archivo está en **Linux**, la **Parte B** es el inventario verificable en el árbol actual; la **Parte A** describe Windows y debe contrastarse con **`hud_owerlay`**.
- Si está en **`hud_owerlay` (Windows)**, ocurre lo inverso: la **Parte A** es la fuente verificable local; la **Parte B** resume Linux y no se valida contra los archivos de este árbol.

## Propósito y límites del documento

- Registra **qué** se hace o debe hacerse, **por qué** importa y **en qué estado** está respecto a la paridad entre variantes.
- **No** describe procedimientos largos (comandos, pasos de build). Eso vive en la documentación de cada repo (p. ej. `README.md` en Linux; empaquetado Windows en `constructor.md` cuando exista en `hud_owerlay`).
- Objetivo de paridad: misma **funcionalidad de producto**. Divergencias explícitas: **SO**, **librerías** y **backend** necesarios para el mismo comportamiento observable.

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
| Windows | `joystick_owerlay`; producto **Joystick Owerlay** | Inventario principal Windows; cola hacia Linux. |
| Linux | `joystick_overlay` (slug Git); producto **Joystick Overlay** | Inventario principal Linux; cola hacia Windows. Replica branding en Windows. |

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

### Clasificación de impacto (obligatoria)

- `CRÍTICO` (Core parity): rompe comportamiento visible, soporte o continuidad del producto.
- `MEDIO` (Operational parity): afecta operación diaria (CLI, instalación, actualización básica).
- `BAJO` (Nice-to-have): mejoras de UX o robustez que no rompen el flujo principal.

## Pares de paridad (contrato ejecutable)

Esta tabla es la fuente de verdad para decidir trabajo cross-repo. Si un `PAR-*` está `ROTO`, no debe cerrarse sprint de paridad sin plan activo para ese par.

| ID | Windows | Linux | Estado | Impacto | Nota |
|----|---------|-------|--------|---------|------|
| PAR-001 | `W-20260425-001` | `L-20260425-001-P` | PARCIAL | CRÍTICO | Linux ya centraliza `USER_DIR`/versiones y migración idempotente; falta espejo final en Windows y cierre de contrato cross-repo. |
| PAR-002 | `W-20260425-002` | `L-20260425-002-P` | OK | MEDIO | Linux ya expone `--version` y `--show-reset-log`. |
| PAR-003 | `W-20260425-003` | `L-20260425-003-P` | PARCIAL | CRÍTICO | Linux ya implementa `--reset-data` + `--do-reset-data`; falta validación cruzada de UX equivalente en Windows. |
| PAR-004 | `W-20260425-004` | `L-20260425-004` | OK | CRÍTICO | Contrato de eventos/hooks alineado. |
| PAR-005A | `W-OPS-003` (mecánica) | `L-OPS-003-P-mechanics` | OK | CRÍTICO | Actualización técnica: `update.sh`, ZIP whitelist, preservación `user/`, logs, validaciones de assets (`update.sh` / UI). |
| PAR-005B | `W-OPS-003` (producto en campo) | `L-OPS-003-P-product` | PARCIAL | CRÍTICO | Canal de distribución, comunicación al usuario, rollback «de producto» verificable entre repos. Solo **OK** con canal definido + política de comunicación + rollback verificable. |
| PAR-006 | `W-20260426-001` | `L-20260426-001` | PARCIAL | MEDIO | Instalación equivalente en intención, distinta por SO. |
| PAR-007 | `W-PAR-L004` | `L-PREFLIGHT` | PARCIAL | BAJO | Preflight y mensajes preventivos aún no normalizados. |

### Regla de ejecución de paridad

- Prioridad operativa fija: primero `CRÍTICO`, luego `MEDIO`, después `BAJO`.
- No cerrar iteración de paridad con `PAR-*` críticos en `ROTO` sin registrar decisión explícita en historial.
- Cada cambio en un repo debe actualizar, en la misma sesión, al menos: `PAR-*` afectado + estado de la cola cruzada (`A.3` o `B.3`).

### Regla de área PAR-005

- **PAR-005A** (mecánica) y **PAR-005B** (producto / actualización en campo) se evalúan por separado.
- El estado del área «Actualización en campo (política de producto)» sigue **PAR-005B**.
- PAR-005A debe estar **OK** antes de considerar cerrar PAR-005B en **OK**.

---

## Parte A — Windows (`joystick_owerlay`)

### A.1 Inventario por estado (solo qué)

En checkout **`joystick_owerlay`**, la tabla siguiente es el inventario **Windows** (hecho = implementado aquí; pendiente = ops, release o paridad frente a la cola L→W de la Parte B).

**Hecho — código y artefactos presentes en este repo**

| ID | Qué | Evidencia en `hud_owerlay` |
|----|-----|----------------------------|
| W-20260425-001 | Persistencia en Windows hasta alinear rebranding: datos bajo `%APPDATA%\joystick_owerlay` en árbol heredado; **objetivo v1** mismo contrato que Linux (`%LOCALAPPDATA%\joystick_overlay`, `.joystick_version`, sin rescate `hud_overlay`). | `config/config.py` (Windows), `utils/versioning.py`, `version.txt`; contrato [`data_contract_v1.md`](../developer/data_contract_v1.md) |
| W-20260425-002 | CLI única: arranque HUD, `configure`, `torneo`, `doctor`, `--version`, `--show-reset-log`. | `cli.py`, `doctor.py` |
| W-20260425-003 | Reset de datos en dos fases: `--reset-data` (interactivo) y `--do-reset-data` (worker, p. ej. sin UI de captura). | `main.py` (parser y rutas tempranas) |
| W-20260425-004 | Historial de input y runtime de extensiones con hook de evento integrado al lector de input. | `core/input_history.py`, `core/extensions_runtime.py`, `maps/input_reader.py` |
| W-20260426-001 | Instalador Inno, scripts de instalación/actualización por ZIP e icono bajo `install/`. | `install/installer.iss`, `install/install_windows.bat`, `install/update_windows.bat`; icono **`joystick_overlay.ico`** en Linux canon; el espejo Windows debe usar el mismo nombre al portar artefactos. |
| W-UPD-ZIP-001 | Actualización aplicada desde ZIP con lista acotada de carpetas y archivos raíz (base para política de campo). | `install/update_windows.bat` |

**Pendiente — release/ops y revisión cruzada con Linux**

| ID | Qué |
|----|-----|
| W-OPS-001 | Validación completa en VM Windows: build, instalación, desinstalación, reset y diagnóstico. |
| W-OPS-002 | Cierre de release: GUID del instalador, versión alineada instalador ↔ runtime, política AV si aplica. |
| W-OPS-003 | Política y UX de actualización **en campo** para quien no desarrolla (documentación, canal de ZIP/build, comprobaciones post-update); el script ZIP existe pero falta el cierre de producto. |
| W-PAR-L001 | Paridad **instalación**: revisión cruzada de accesos claros a HUD / config / torneo tras instalar (objetivo L-20260426-001). |
| W-PAR-L002 | Paridad **CLI / documentación**: revisión cruzada de que las entradas de producto coincidan en intención con Linux (objetivo L-20260426-002). |
| W-PAR-L003 | Paridad **actualización**: alinear intención operativa entre `update_windows.bat`, instalador y lo documentado para Linux (objetivo L-20260426-003). |
| W-PAR-L004 | Opcional: **preflight** de instalación con mensajes claros si el entorno no es apto (espíritu de validación gráfica en Linux, sin copiar APIs). |

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
Fecha: 2026-04-25  
Qué: Persistencia de perfiles y metadatos de versión en ruta de usuario Windows.  
Por qué: Instalación en `Program Files` no debe requerir escritura en runtime.  
Portabilidad Linux: `portado` (Linux canon: **`RUNTIME_VERSION_PATH`** → `.joystick_version`; perfiles **`user/`** y espejo `~/.local/share/joystick_overlay` según `storage_mode`; no hay `utils/versioning.py` / `version.txt` como Windows).  
Evidencia Windows: `config/config.py`, `utils/versioning.py`, `version.txt` (en `joystick_owerlay`).

**W-20260425-002** — Estado: `hecho` (Windows)  
Fecha: 2026-04-25  
Qué: Diagnóstico y utilidades CLI sin arrancar la app gráfica cuando corresponda.  
Por qué: Soporte y reproducibilidad.  
Portabilidad Linux: `portado` (`cli.py` con `run|config|tournament|doctor`, `--help`, `--version`, `--show-reset-log`; `doctor.py` orientado a `/dev/input` y sesión gráfica).  
Evidencia Windows: `cli.py`, `doctor.py` (en `hud_owerlay`).

**W-20260425-003** — Estado: `hecho` (Windows)  
Fecha: 2026-04-25  
Qué: Borrado seguro de datos de usuario con confirmación separada del proceso que ejecuta el borrado.  
Por qué: Evitar bloqueos de archivos y pérdida de foco en captura.  
Portabilidad Linux: `portado` (`main.py`: `--reset-data`, `--do-reset-data`; ver matriz [`reset_matrix.md`](../developer/reset_matrix.md)).  
Evidencia Windows: `main.py` (en `hud_owerlay`).

**W-20260425-004** — Estado: `hecho` (Windows)  
Fecha: 2026-04-25  
Qué: Trazabilidad de input y extensión por hooks sin acoplar a la UI.  
Por qué: Base para análisis y extensiones.  
Portabilidad Linux: `portado` (`core/input_history.py`, `core/extensions_runtime.py`, uso en `main.py`, `maps/input_reader.py`).  
Evidencia Windows: mismos módulos en `hud_owerlay`.

**W-20260426-001** — Estado: `hecho` (Windows)  
Fecha: 2026-04-26  
Qué: Instalación y actualización como piezas bajo `install/`.  
Por qué: Un solo lugar para artefactos de empaquetado Windows.  
Portabilidad Linux: `n/a` (instalación por SO: scripts shell y `.desktop` en Linux).  
Evidencia Windows: `install/installer.iss`, `install/install_windows.bat`, `install/update_windows.bat`, `install/joystick_overlay.ico` (al portar nombre de icono en el espejo).

**W-UPD-ZIP-001** — Estado: `hecho` (Windows)  
Fecha: 2026-04-26  
Qué: Aplicar actualización desde un ZIP con copia acotada de módulos y carpetas del proyecto.  
Por qué: Base técnica para W-OPS-003 sin depender solo de reemplazo manual de archivos.  
Portabilidad Linux: `n/a` (mecánica distinta; ver Parte B).  
Evidencia Windows: `install/update_windows.bat`.

**W-PAR-L001** — Estado: `pendiente`  
Fecha: —  
Qué: Revisión cruzada post-instalación: usuario localiza HUD, config y torneo con la misma claridad relativa que en Linux.  
Por qué: Paridad de producto entre repos.  
Portabilidad Linux: ver cola B.3 (`L-20260426-001`).  
Evidencia: — (checklist / notas de release).

**W-PAR-L002** — Estado: `pendiente`  
Fecha: —  
Qué: Revisión cruzada de superficie CLI y documentación frente a Linux.  
Por qué: Mismas entradas de producto donde aplique.  
Portabilidad Linux: ver cola B.3 (`L-20260426-002`).  
Evidencia: —

**W-PAR-L003** — Estado: `pendiente`  
Fecha: —  
Qué: Revisión cruzada del flujo operativo de actualización (ZIP, instalador, mensajes al usuario).  
Por qué: Paridad de intención con `update.sh` / UI Linux.  
Portabilidad Linux: ver cola B.3 (`L-20260426-003`).  
Evidencia: —

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

**W-OPS-002** — Estado: `pendiente`  
Fecha: —  
Qué: Identidad de instalación y versión publicada alineadas con política de release.  
Por qué: Upgrades y soporte.  
Portabilidad Linux: `n/a`.  
Evidencia: —

**W-OPS-003** — Estado: `pendiente` (Windows)  
Fecha: —  
Qué: Política de actualización de binarios en Windows para usuarios finales (canal, comprobaciones, comunicación).  
Por qué: Desacoplar del flujo solo-desarrollador; W-UPD-ZIP-001 cubre solo el mecanismo técnico.  
Portabilidad Linux: `en_progreso` (equivalente funcional en repo Linux; detalle en Parte B).  
Evidencia Windows: `install/update_windows.bat`, `install/installer.iss` (hasta cerrar política de release).

### A.3 Cola Windows → Linux (qué portar; sin cómo)

| ID origen | Qué debe existir en Linux | Estado cola |
|-----------|---------------------------|-------------|
| W-20260425-001 | Misma política de datos de usuario y versión coherente con instalación Linux. | En progreso |
| W-20260425-002 | Misma superficie de diagnóstico y flags de soporte acordados donde aplique. | En progreso |
| W-20260425-003 | Misma semántica de reset en dos fases. | Pendiente |
| W-20260425-004 | Mismo contrato de evento e historial + hooks. | Portado |
| W-20260426-001 | — | n/a |
| W-UPD-ZIP-001 | Equivalente funcional de aplicar ZIP acotado (si aplica al modelo de release Linux). | En progreso / n/a según distro |
| W-OPS-003 | Equivalente funcional de actualización operativa para usuarios finales. | En progreso |

---

## Parte B — Linux (`joystick_overlay`)

### B.1 Inventario por estado (solo qué; verificado en este árbol)

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
| L-20260425-001-P | Rutas de datos migradas a contrato `USER_DIR` + `.data_version`; pendiente convergencia final de política en ambos repos. |
| L-20260425-002-P | Resuelto en Linux: `cli.py` ya incluye `--version` y `--show-reset-log`; validar espejo documental en Windows. |
| L-20260425-003-P | Resuelto parcialmente: Linux ya implementa reset en dos fases; pendiente validación cruzada de semántica operativa. |
| L-OPS-003-P | Política de actualización en campo para usuarios sin git (ZIP documentado; falta cierre ops tipo W-OPS-003). |

### B.2 Registro de ítems Linux (plantilla)

**L-20260426-001** — Estado: `hecho`  
Fecha: 2026-04-26  
Qué: Instalación accesible (launcher + menú + comprobaciones de entorno gráfico).  
Por qué: Paridad funcional con «instalado y localizable» en Windows.  
Portabilidad Windows: `pendiente` (revisión cruzada de accesos equivalentes).  
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
Portabilidad Windows: `pendiente` (alinear política con `update_windows.bat` / instalador).  
Evidencia: `update.sh`, `render/profile_config_menu.py`.

**L-20260425-004** — Estado: `hecho`  
Fecha: 2026-04-25  
Qué: Historial estructurado y hooks de extensión en el loop de input.  
Por qué: Paridad con W-20260425-004.  
Portabilidad Windows: `portado` (origen Windows; mantener contrato).  
Evidencia: `core/input_history.py`, `core/extensions_runtime.py`, `main.py`, `maps/input_reader.py`.

**L-20260425-001-P** — Estado: `pendiente`  
Fecha: —  
Qué: Datos de usuario y versión en ubicación estable fuera del árbol de desarrollo (equivalente a W-20260425-001).  
Por qué: Instalación en sitio de solo lectura o multi-usuario.  
Portabilidad Windows: `portado` (asumido hecho en Windows).  
Evidencia parcial: `.joystick_version`; `profiles/profile_store.py` y `config/config.py` (`PROFILES_PATH`, etc.).

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
Portabilidad Windows: `pendiente`.  
Evidencia: `update.sh`, UI de actualización; falta definición de release Linux.

### B.3 Cola Linux → Windows (qué revisar en Windows; sin cómo)

*Ningún ítem sin **criterio de cierre** explícito.*

| ID / objetivo | Qué revisar en Windows | Criterio de cierre | Verificación | Estado cola | Fecha |
|---------------|------------------------|--------------------|--------------|-------------|-------|
| L-20260426-001 | Accesos HUD / config / torneo tras instalación. | Menú/accesos visibles **Joystick Overlay**: abrir ejecutable principal, configuración y torneo sin línea de comandos | Instalador + acceso directos | Pendiente revisión cruzada | — |
| L-20260426-002 | CLI / entradas de producto. | Misma superficie observable: comandos equivalentes **`joystick-overlay`** y subcomandos documentados (`config`, `tournament`, `doctor`, `--version`, `--help`) | Lista en README instalador vs `doctor` | Pendiente revisión cruzada | — |
| L-20260426-003 | Update + logs desde UI donde exista. | `Actualizar overlay` no borra `USER_DIR` del proyecto; log en `user/update.log` o ruta documentada | Prueba manual + lectura log | Pendiente revisión cruzada | — |
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
| 2026-04-26 | Impacto: PAR-005 \| Transición: ROTO -> PARCIAL \| Evidencia: `update.sh`, `render/profile_config_menu.py`. |
| 2026-04-27 | Bloque: gobernanza de bitácora \| Antes: solo ítems narrativos y tablero PAR \| Después: sección «Registro por bloques» con plantilla antes/después/motivo y tabla de bloques previstos del plan fusionado \| Motivo: trazabilidad por entrega y alineación con `control_estilo_e_iconos_736cb9a6.plan.md`. |
| 2026-04-27 | Acta auditoría híbrida (`auditoría_todos_híbridos`): cierre de brechas shell/docs + tests de rutas; ver tabla siguiente. |
| 2026-05-03 | Rebranding producto **Joystick Overlay** en Linux canon: ejecutable/lanzador **`joystick-overlay`**, rutas externas `joystick_overlay`, archivo **`.joystick_version`**, variables **`JOYSTICK_*`**, `.desktop`/icono instalación; docs en **`docs/`** (contrato, matriz reset, esta bitácora). **Sin** migración automatizada desde rutas `hud_overlay`/`hud-overlay`/`HUD_*`; ver `docs/developer/data_contract_v1.md` §6. |
| 2026-05-03 | Seguimiento Windows (`hud_owerlay`): replicar branding (binario **`joystick-overlay`**, rutas **`%LOCALAPPDATA%\joystick_overlay`** o equivalente acordado, instalador, iconos `.ico`, texto UI). Lista de chequeo técnico mínimo: (1) grep sin `hud-overlay` residual en lanzadores; (2) espejo mismo contrato datos v1 donde aplique; (3) no reintroducir rescate desde árboles antiguos `hud_overlay` si el contrato vetado así. |
| 2026-05-13 | README reestructurado (hitos, usuario/streamer, ZIP **`bindings/`**); endurecimiento seguridad (ZIP perfil, resolver, `update.sh`, `flock`); sección README «Seguridad y archivos no confiables»; [security_model.md](../security/security_model.md); `tests/test_zip_security.py`; hitos narrativos archivados en [Archivo README (hitos antiguos)](#archivo-readme-hitos-antiguos). |
| 2026-05-14 | `LICENSE` (GPL-3) en raíz; `pyproject.toml` declara licencia vía archivo `LICENSE`; `MANIFEST.in` incluye `LICENSE`; README enlaza a licencia y corrige markdown (`bindings/`, modos de captura, `XDG_*` / `JOYSTICK_*`, tabla de entrypoints). |

---

## Checklist rebranding para Windows (`hud_owerlay`)

Aplicar en el repo Windows al portar canon Linux:

1. Renombrar ejecutable lanzador **`joystick-overlay`** y actualizar Inno/bat igual que `install.sh` Linux.
2. Rutas `%LOCALAPPDATA%\...\joystick_overlay\...` alineadas a contrato [`data_contract_v1.md`](../developer/data_contract_v1.md) (solo espejo/externo).
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
