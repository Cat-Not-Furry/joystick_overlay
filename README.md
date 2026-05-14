# Joystick Overlay (Linux)

HUD en Pygame para mostrar stick, direccionales y botones según el perfil (teclado, hitbox, mixbox o joystick). Datos de usuario bajo `user/` en la raíz del proyecto.

## Características

- Perfiles con bindings en JSON, export/import en ZIP, HUD configurable.
- Modos de captura para composición (`normal`, `obs_green` / chroma).
- CLI `joystick-overlay` (run, config, tournament, doctor), actualización por git o ZIP.

## Estado del proyecto

Hitos, paridad Windows/Linux y colas de portado: **[docs/archive/bitacora.md](docs/archive/bitacora.md)**.

## Instalación rápida

```bash
./install.sh
```

Con `venv` manual: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python3 main.py`.

**Más detalles:** [docs/user/installation.md](docs/user/installation.md)

## Uso rápido

```bash
python3 main.py
```

`joystick-overlay doctor` para diagnóstico (Wayland/X11, `input`, pygame/evdev).

**Más detalles:** [docs/user/quick_start.md](docs/user/quick_start.md)

## Documentación

| Audiencia | Enlace |
| --------- | ------ |
| Índice completo | [docs/README.md](docs/README.md) |
| Usuarios (instalación, inicio, incidencias) | [docs/user/](docs/user/) |
| Modo entrenamiento (HUD) | [docs/user/training_mode.md](docs/user/training_mode.md) |
| Modo torneo | [docs/user/tournament_mode.md](docs/user/tournament_mode.md) |
| Streamers (OBS, croma) | [docs/streamer/capture_modes.md](docs/streamer/capture_modes.md) |
| Checklist OBS | [docs/streamer/obs_setup.md](docs/streamer/obs_setup.md) |
| Desarrollo (contrato, alcance, reset, IA) | [docs/developer/](docs/developer/) |
| Estructura del repositorio | [docs/developer/repository_layout.md](docs/developer/repository_layout.md) |
| Seguridad | [docs/security/security_model.md](docs/security/security_model.md) |
| Referencia HUD | [docs/reference/layout_reference.md](docs/reference/layout_reference.md) |
| Archivo / bitácora | [docs/archive/bitacora.md](docs/archive/bitacora.md) |

Índice legacy en la carpeta `docs/`: [docs/INDEX.md](docs/INDEX.md) (apunta al índice principal).

## Requisitos

- Python 3.9+ (ver [pyproject.toml](pyproject.toml)).
- Linux con sesión gráfica para Pygame; lectura de `/dev/input/*` para evdev si aplica.

**Más detalles:** [docs/user/installation.md](docs/user/installation.md)

## Seguridad

ZIP de perfil y de actualización se tratan como **contenido no confiable** (extracción acotada, sin symlinks en rutas sensibles, límites de tamaño).

**Más detalles:** [docs/security/security_model.md](docs/security/security_model.md)

## Extensiones (standby)

Hooks e historial de entrada en [arcade/engine/core/extensions_runtime.py](arcade/engine/core/extensions_runtime.py) y [arcade/engine/core/input_history.py](arcade/engine/core/input_history.py). Sin sistema de plugins completo.

**Más detalles:** [docs/developer/product_scope.md](docs/developer/product_scope.md)

## Contribución y licencia

GPL-3: [LICENSE](LICENSE). Guía de contribución: [CONTRIBUTING.md](CONTRIBUTING.md). Contribución con IA: [docs/developer/ai_contribution_rules.md](docs/developer/ai_contribution_rules.md).

## Créditos

Proyecto orientado al fighting y transmisión; mejoras y forks bienvenidos con crédito si publicas derivados.
