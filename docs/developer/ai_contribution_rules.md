# 12 reglas de uso de IA para proyectos GPL-3

Este documento adapta las 12 reglas de la comunidad del kernel Linux sobre contribuciones asistidas por IA a proyectos con licencia GPL-3.

## Como reutilizar este documento

Para usar este documento en otro repositorio, reemplaza estos placeholders:

- `[PROYECTO]`
- `[RUTA_LICENSE]`
- `[ENLACE_CONTRIBUTING]`
- `[POLITICA_COMPATIBILIDAD]`

Si el proyecto usa `GPL-3.0-only`, conserva ese texto. Si usa `GPL-3.0-or-later`, sustituye de forma consistente en todas las reglas.

## Alcance

Estas reglas aplican a contribuciones versionadas (commits, parches, PR/MR) asistidas por IA en `[PROYECTO]`.

## Principios fundamentales (Normas 1-3)

1. Compatibilidad de licencia  
   Todo codigo generado o modificado con asistencia de IA debe ser compatible con la licencia principal del proyecto (GPL-3). Debe alinearse con `[RUTA_LICENSE]` y con `[POLITICA_COMPATIBILIDAD]`.

2. Identificadores SPDX  
   Cada archivo fuente nuevo o modificado de forma sustancial debe llevar encabezado SPDX correcto y coherente con la licencia del proyecto.

3. Reglas de licencia del proyecto  
   Se deben seguir todas las reglas legales y de contribucion definidas en `[ENLACE_CONTRIBUTING]`, `[RUTA_LICENSE]` y politicas internas aplicables (copyright, terceros, redistribucion, NOTICE, etc.).

## Responsabilidad humana (Normas 4-5)

4. Prohibicion de firma por IA  
   Un agente de IA no puede agregar `Signed-off-by` ni equivalentes legales de certificacion de autoria/origen.

5. Revision y responsabilidad humana  
   La persona que envia el cambio debe revisar el codigo, validar la licencia, agregar su `Signed-off-by` cuando aplique y asumir la responsabilidad legal y tecnica completa.

## Atribucion y trazabilidad (Normas 6-12)

6. Trazabilidad con `Assisted-by`  
   Toda contribucion asistida por IA debe incluir una linea `Assisted-by:` en el commit o en la plantilla de PR/MR, con nombre del asistente, modelo/version y herramientas no triviales usadas.

7. No incluir herramientas basicas  
   No listar utilidades basicas en `Assisted-by` (por ejemplo: `git`, `gcc`, `make`, editores de texto).

8. Ejemplo de atribucion valida  
   `Assisted-by: NombreAsistente:modelo-version coccinelle sparse`

9. Transparencia obligatoria  
   La etiqueta `Assisted-by` es obligatoria para facilitar trazabilidad y permitir revision adicional por mantenedores.

10. Prohibicion de firmas parciales por IA  
    La IA no puede firmar el codigo bajo ninguna etiqueta que implique certificacion legal de origen.

11. Trazabilidad suficiente  
    La atribucion debe incluir la informacion relevante sobre IA y herramientas auxiliares no triviales para que la revision sea reproducible y auditable.

12. Cumplimiento estricto  
    El equipo de desarrollo debe cumplir estas reglas para proteger calidad, legalidad y mantenimiento, evitando aportes de baja calidad generados sin criterio humano.

## Nota practica SPDX para scripts Bash

En scripts Bash, usa el encabezado de licencia sin romper el shebang:

```bash
#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
```

Si el proyecto declara `GPL-3.0-or-later`, usa ese identificador de forma consistente.

## Recomendacion de plantilla para commits asistidos por IA

Ejemplo minimo:

```text
feat: descripcion del cambio

Assisted-by: NombreAsistente:modelo-version coccinelle sparse
Signed-off-by: Nombre Humano <correo@ejemplo.com>
```

`Signed-off-by` siempre lo agrega una persona.
