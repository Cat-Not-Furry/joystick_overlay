# Estructura del repositorio (por qué hay raíz y `arcade/engine/`)

Joystick Overlay se distribuye como paquete Python con **entrypoints en la raíz** del clon y el **código importable** bajo `arcade/engine/`.

## Raíz del clon

| Fichero / directorio | Rol |
| -------------------- | --- |
| [`main.py`](../../main.py) | Menú principal, HUD, bucle Pygame. |
| [`cli.py`](../../cli.py) | Comando `joystick-overlay` (`run`, `config`, `tournament`, `doctor`, …). |
| [`configure.py`](../../configure.py), [`tournament.py`](../../tournament.py), [`doctor.py`](../../doctor.py) | Puntos de entrada usados por la CLI o por ejecución directa `python3 …`. |
| [`engine_sys_path.py`](../../engine_sys_path.py) | Inserta `arcade/engine` al inicio de `sys.path` para que `import config`, `import profiles`, etc. resuelvan dentro del paquete. |
| [`pyproject.toml`](../../pyproject.toml) | Metadatos del proyecto, dependencias de runtime, script console `joystick-overlay`. |
| [`requirements.txt`](../../requirements.txt) | Instalación mínima para ejecutar (alineada con runtime). |
| [`configs/`](../../configs/) | Valores por defecto, esquemas JSON, **migraciones** declarativas. |
| [`docs/`](../../docs/) | Documentación versionada. |
| [`install/`](../../install/) | Iconos y plantillas `.desktop` para integración en el escritorio. |
| [`scripts/`](../../scripts/) | `install.sh`, `update.sh`, `run.sh`, utilidades. |
| [`tests/`](../../tests/) | Pruebas y scripts de métricas. |
| [`user/`](../../user/) | Datos de usuario en desarrollo (canon portable; no versionar contenido personal). |

## Paquete bajo `arcade/engine/`

Setuptools declara paquetes con origen en [`arcade/engine`](../../arcade/engine) (`pyproject.toml`: `packages.find.where`). Ahí viven módulos como `config`, `profiles`, `render`, `maps`, `core`, `training`, `utils` — es el **árbol que importa** `main.py` tras `engine_sys_path`.

### `arcade/engine/app/` (ARCH-001)

Orquestación extraída de [`main.py`](../../main.py) (refactor por fases):

| Módulo | Rol |
|--------|-----|
| `app/ui/modals.py` | Modales Pygame compartidos (choice, text, message, update) |
| `app/secondary_flows.py` | Selectores y confirmaciones en la misma superficie |
| `app/startup.py` | Preflight y reset de datos |
| `app/debug_menu.py` | Diagnóstico menú (`JOYSTICK_DEBUG_MENU`) |
| `app/window_mode.py` | Estado modo ventana flotante/normal |
| `app/constants.py` | Tamaños de ventana secundaria |
| `app/main_menu.py` | Menú principal (`run_main_menu_until_action`, `AppContext`, `MainMenuState`, `drive_menu_frame`) |
| `app/hud_setup.py` | Setup HUD interactivo/no interactivo y flujos de mapeo |
| `app/hud_session/` | Bucle HUD (`events`, `context`, `loop`) y `run_hud_session` (`session.py`) |
| `app/profile_config/` | Menú configuración de perfiles (`menu.py`, `handlers/` por sección) |

[`main.py`](../../main.py) conserva `main()` y re-exporta la API pública (`run_main_menu_until_action`, `show_main_menu` deprecado, `run_hud_session`, etc.) para entrypoints y tests.

`open_profile_config_menu` se exporta desde `app/profile_config/`; [`render/__init__.py`](../../arcade/engine/render/__init__.py) re-exporta para compatibilidad.

## Assets

Iconos, plantillas de bindings y presets: [`arcade/assets/`](../../arcade/assets) (versionado en [`arcade/assets/.assets_version`](../../arcade/assets/.assets_version)).

## Resumen

- **No duplicar** lógica entre raíz y `arcade/engine/`: la raíz orquesta; el motor vive bajo `arcade/engine/`.
- Para contribuir: cambia código bajo `arcade/engine/` salvo que el cambio sea explícitamente un entrypoint o script en raíz.

**Más detalles:** [CONTRIBUTING.md](../CONTRIBUTING.md), [contrato de datos](data_contract_v1.md), [tests/README](../../tests/README.md).
