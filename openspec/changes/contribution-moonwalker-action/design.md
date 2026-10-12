# Design

## Context

El paquete ya expone `moonwalk-contributions --username ... --output-dir ...` y genera los nombres estables `moonwalk-contributions.gif` y `moonwalk-contributions.png`. El workflow propio instala Python y el paquete, ejecuta el CLI y publica solo esos archivos. La capacidad `contribution-dance` define el contenido visual y seguirá siendo la fuente de verdad para la animación.

## Goals / Non-Goals

**Goals:**
- Permitir invocar la generación desde un workflow externo mediante `uses:`.
- Reutilizar el paquete existente para evitar mantener una segunda implementación.
- Dejar que el workflow consumidor decida cómo almacenar o publicar los recursos.
- Mantener el flujo local y el workflow programado del repositorio.

**Non-Goals:**
- Añadir SVG, nuevos estilos o cambios a la coreografía y paleta.
- Crear commits o publicar ramas desde la Action reutilizable.
- Publicar un release o tag de GitHub durante esta implementación.

## Decisions

1. **Usar una composite action declarada en `action.yml` en la raíz.** GitHub permite consumirla desde otros repositorios mediante `uses: owner/repository@ref`. Una Action compuesta conserva el desarrollo y dependencias Python actuales. Se descarta duplicar el render en JavaScript o mantener una imagen Docker específica.

2. **Instalar el paquete desde `github.action_path` y ejecutar el CLI existente.** La Action preparará Python 3.12, instalará el proyecto desde la ruta de la Action y llamará al comando con el usuario y directorio configurados. Esto mantiene iguales el comportamiento local, el programado y el externo.

3. **Definir entradas pequeñas y compatibles con el CLI.** `github_user_name` será obligatoria, `github_token` opcional y `output_dir` tendrá `assets` como valor predeterminado. Si no se pasa un token, el paso usará `github.token`. El directorio será relativo al workspace del workflow consumidor.

4. **No publicar desde la Action.** La Action solo escribe los dos archivos en el checkout del workflow anfitrión. Cada consumidor podrá confirmarlos con sus permisos, cargarlos como artefactos o procesarlos en pasos posteriores. Así la Action no necesita permisos de escritura implícitos ni altera ramas remotas.

5. **Usar la Action localmente en el workflow de este proyecto.** El job de actualización invocará `uses: ./` después del checkout, conservará el chequeo de calidad y el paso que confirma solo las imágenes cuando cambien. Para repositorios externos, el README mostrará la referencia del repositorio y explicará que `@main` sirve para probar; se recomienda un tag una vez que el mantenedor publique una versión.

## Risks / Trade-offs

- [El token automático puede no dar acceso a contribuciones privadas] → Documentar el token opcional `read:user` y el secreto que debe proporcionar el consumidor.
- [Una referencia mutable puede cambiar entre ejecuciones] → Recomendar referencias a tags publicados y mantener `@main` solo como ejemplo de prueba inicial.
- [La preparación de Python e instalación añade tiempo al job] → Reutilizar metadatos y dependencias ya declarados; no añadir un runtime duplicado.
- [Un fallo del generador podría dejar imágenes anteriores] → Mantener la validación y escritura segura que ya ofrece el paquete, y propagar errores como fallo del paso de Action.

## Migration Plan

1. Añadir `action.yml` con las entradas acordadas y una ejecución compuesta del CLI.
2. Cambiar el workflow propio para invocar `./` y conservar su publicación condicional.
3. Reescribir la sección de Actions del README con un ejemplo consumidor, permisos, token, directorio y publicación; mantener las instrucciones del CLI local.
4. Validar el manifiesto y el ejemplo; probar el workflow interno en GitHub una vez que los cambios estén en la rama predeterminada.

Para revertir, eliminar `action.yml` y restaurar el workflow y la documentación anteriores; el CLI y los recursos generados siguen siendo utilizables localmente.
