# Contribuir a Joystick Overlay

Gracias por interesarte en el proyecto. Este documento resume el flujo práctico; la licencia y el uso de IA están en documentos enlazados abajo.

## Entorno

- Python **3.9+** (ver [`pyproject.toml`](pyproject.toml)).
- Clona el repo y, si usas `venv`, instala dependencias: `pip install -r requirements.txt`.
- Desarrollo extra (métricas, pytest): `pip install -r tests/requirements-dev.txt`.

## Documentación

- Índice por audiencia: [`docs/README.md`](docs/README.md).
- Contrato de datos y migraciones: [`docs/developer/data_contract_v1.md`](docs/developer/data_contract_v1.md), [`docs/developer/migrations.md`](docs/developer/migrations.md).
- Contribución con asistencia de IA (texto legal): [`docs/developer/ai_contribution_rules.md`](docs/developer/ai_contribution_rules.md).

## Tests y calidad

- Carpeta canónica: **`tests/`** (guía en [`tests/README.md`](tests/README.md)). Algunos forks o historiales pueden mencionar `test/` en singular; en este árbol las pruebas viven bajo `tests/`.
- Comprobación rápida de enlaces relativos en Markdown del repo:

  ```bash
  python3 scripts/check_doc_links.py
  ```

## Estilo de cambios

- Cambios **acotados** al problema o mejora descrita; evita refactors masivos mezclados con correcciones.
- Sigue el estilo existente (imports, nombres, comentarios en español donde ya lo esté el fichero).
- Si tocas rutas de datos o versiones, actualiza o revisa `docs/developer/` en el mismo PR cuando aplique.

## Capturas para la documentación

La carpeta [`docs/assets/screenshots/`](docs/assets/screenshots/) está reservada para imágenes referenciadas desde las guías (p. ej. HUD u OBS). Solo añade binarios si aportan valor claro y tamaño razonable; enlaza con rutas relativas desde el `.md` correspondiente.

## Licencia

El proyecto se distribuye bajo **GPL-3.0** — ver [`LICENSE`](LICENSE).
