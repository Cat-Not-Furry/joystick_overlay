# Matriz de pruebas — reset de datos

Herramienta operativa para **PAR-003**: marcar resultado y evidencia después de ejecutar.

| Caso | Variante | Input / comando | Esperado | Bloqueante | Resultado | Evidencia |
|------|----------|-----------------|----------|-------------|-----------|-----------|
| Confirmación CLI | L | `--reset-data` (+ confirmación) | Pide confirmación antes de tocar disco | Sí | | |
| Worker sin UI | L | `--do-reset-data` | Ejecuta reset sin HUD interactivo | Sí | | |
| Cancelación | L | `n` ante confirmación | No borra datos | Sí | | |
| Idempotencia | L | dos `--do-reset-data` seguidos | Exit estable; disco coherente con contrato | Sí | | |
| Logs | L | post reset | `user/reset.log` actualizado/existe según política | Sí | PASS | `2026-05-03` — `tail -n5 user/reset.log` tras `--do-reset-data` (Linux dummy driver) |
| Sin TTY | W | (pendiente en Windows) | Error claro o fallback documentado | Sí | | |

Tras operaciones que dejen `user/` vacío o inicial, la versión en `user/.data_version` y las migraciones por manifiesto vuelven a aplicarse según arranque y carga de perfiles; ver **[migrations.md](migrations.md)**.

## Criterio de éxito global

- `USER_DIR` bajo proyecto coherente con [data_contract_v1.md](data_contract_v1.md) tras cada caso bloqueante.
- `profiles_index.json` reconciliable con carpetas si aplica test.
- Códigos de salida coherentes (`0` éxito, distinto para fallo esperado).

