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

## Assets

Iconos, plantillas de bindings y presets: [`arcade/assets/`](../../arcade/assets) (versionado en [`arcade/assets/.assets_version`](../../arcade/assets/.assets_version)).

## Resumen

- **No duplicar** lógica entre raíz y `arcade/engine/`: la raíz orquesta; el motor vive bajo `arcade/engine/`.
- Para contribuir: cambia código bajo `arcade/engine/` salvo que el cambio sea explícitamente un entrypoint o script en raíz.

**Más detalles:** [CONTRIBUTING.md](../CONTRIBUTING.md), [contrato de datos](data_contract_v1.md), [tests/README](../../tests/README.md).
