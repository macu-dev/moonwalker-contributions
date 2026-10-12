# Proposal

## Why

Hoy el proyecto ofrece un paquete Python y un workflow propio, así que cada persona que quiera mostrar el moonwalker debe copiar la configuración de generación. Una GitHub Action reutilizable permitirá incorporarlo desde el workflow de cualquier repositorio con una configuración breve, como `snk`, conservando la animación del bailarín.

## What Changes

- Añadir una GitHub composite action invocable con `uses:` desde workflows consumidores.
- Aceptar el usuario objetivo, un token opcional y el directorio donde se generan el GIF y el PNG.
- Mantener el CLI y el workflow programado del proyecto; hacer que este último ejecute la misma Action local para reducir configuraciones divergentes.
- Reorganizar el README para presentar una demostración, una guía corta de uso como Action, configuración del token y publicación de recursos, además de conservar el uso local y la contribución al proyecto.
- Documentar que la Action escribe los recursos en el workspace del workflow consumidor y que este decide cómo publicarlos.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `contribution-dance`: permitir que la generación del GIF y su respaldo PNG se invoque como una GitHub Action reutilizable con configuración externa.

## Impact

- Añade `action.yml` en la raíz y modifica el workflow de actualización, el README y las pruebas de integración de la interfaz de Action.
- Reutiliza el paquete Python y el comando actual; no cambia la cinemática ni el diseño del moonwalker.
- Los repositorios consumidores necesitarán habilitar GitHub Actions y proporcionar un usuario objetivo; un token personalizado seguirá siendo opcional.
