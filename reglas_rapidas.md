# Reglas Rapidas

Usa estas reglas por defecto en tareas del dia a dia.

## Alcance
- No cambiar arquitectura ni logica del programa sin autorizacion explicita.
- Si hay duda de alcance, preguntar antes de ejecutar.
- Prioridad: documentacion ( y docs tecnicas).

## Cambios de codigo
- Solo se permite codigo dentro de .
- Si el cambio es importante, nuevo o complejo: pedir confirmacion primero.
- No tocar proyectos fuera de .

## Propuestas obligatorias en cambios relevantes
- Resumen del cambio.
- Pros.
- Contras.
- Posibles errores o regresiones.
- Pregunta final de autorizacion.

## Seguridad y configuracion
- Variables sensibles solo en  no versionado.

## Calidad de salida
- Mantener soluciones simples y accionables.
- Explicar como validar cada cambio.
- Si no se puede validar algo, declararlo de forma explicita.

## Flujo de trabajo con el usuario
- El agente implementa cambios en codigo/documentacion local.
- El usuario es quien realiza `git push` a GitHub.
- El agente no debe hacer `push` ni despliegues, salvo autorizacion explicita.
- Si una validacion depende de Render/GitHub, entregar checklist claro para que el usuario la ejecute.
