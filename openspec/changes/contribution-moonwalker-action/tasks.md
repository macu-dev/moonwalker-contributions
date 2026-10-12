# Tasks

## 1. Crear la GitHub Action reutilizable

- [x] 1.1 Añadir `action.yml` como composite action con entradas `github_user_name`, `github_token` opcional y `output_dir` con valor predeterminado `assets`; instalar el paquete desde `github.action_path` y ejecutar el CLI existente, comprobando que genera ambos archivos en el workspace y propaga errores sin revelar el token.
- [x] 1.2 Actualizar el workflow propio para invocar `uses: ./` y conservar las comprobaciones de calidad y la publicación condicional de solo los dos recursos, verificando que una ejecución sin diferencias no crea commits.

## 2. Documentar el uso como `snk`

- [x] 2.1 Reorganizar el README con la demostración al inicio, un ejemplo de workflow consumidor con `uses:`, configuración de username/token/output, pasos para publicar los recursos en el README de perfil y notas de permisos/versionado; verificar coherencia de los nombres de entrada y archivos con `action.yml`.
- [x] 2.2 Conservar las instrucciones de instalación y generación con el CLI local, verificar que los enlaces a GIF y PNG sigan siendo válidos y describir que publicar artefactos es responsabilidad del workflow anfitrión.

## 3. Verificar integración y contrato

- [x] 3.1 Validar OpenSpec en modo estricto y revisar el workflow consumidor documentado junto con el workflow interno para confirmar que ambas invocaciones usan las entradas y rutas compatibles con la Action.
- [ ] 3.2 Ejecutar manualmente el workflow del repositorio tras publicar los cambios y revisar en GitHub la ejecución, los recursos generados y su lectura desde el README.

## Workflow follow-up

- Archivar el cambio tras completar las verificaciones y revisar la integración publicada.
