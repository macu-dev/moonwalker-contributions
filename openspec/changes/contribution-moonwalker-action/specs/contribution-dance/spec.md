# Spec Delta

## ADDED Requirements

### Requirement: Generación mediante GitHub Action reutilizable
El proyecto SHALL proporcionar una GitHub Action reutilizable que obtenga las contribuciones de la cuenta configurada y genere el GIF moonwalker y el PNG de respaldo en el directorio del workspace indicado.

#### Scenario: Generar recursos en un workflow consumidor
- **WHEN** un workflow invoca la Action con un nombre de usuario y un directorio de salida
- **THEN** la Action escribe allí `moonwalk-contributions.gif` y `moonwalk-contributions.png` usando la animación existente

#### Scenario: Directorio de salida omitido
- **WHEN** un workflow omite el directorio de salida
- **THEN** la Action escribe ambos recursos en el directorio `assets` del workspace

#### Scenario: Autenticación opcional
- **WHEN** el workflow consumidor no proporciona un token personalizado
- **THEN** la Action usa el token de GitHub Actions disponible en el contexto del workflow sin imprimir su valor

#### Scenario: Error durante la generación
- **WHEN** la consulta de contribuciones o la generación falla
- **THEN** la Action termina con error y conserva los recursos válidos que ya existían

### Requirement: Publicación controlada por el workflow consumidor
La Action SHALL escribir recursos en el workspace y SHALL dejar la decisión de confirmarlos, publicarlos o cargarlos como artefactos al workflow que la invoca.

#### Scenario: Workflow que publica recursos en el repositorio
- **WHEN** un workflow consumidor desea actualizar sus imágenes versionadas
- **THEN** puede añadir un paso posterior que confirme y publique los archivos generados con los permisos de repositorio que haya configurado

#### Scenario: Workflow que no publica recursos
- **WHEN** un workflow consumidor solo necesita los recursos para esa ejecución
- **THEN** puede cargarlos como artefactos o usarlos en otros pasos sin que la Action cree commits ni modifique referencias remotas

### Requirement: Documentación de integración de la Action
El README SHALL documentar la invocación de la Action desde un workflow consumidor, las entradas requeridas y opcionales, el token, el directorio de salida y la publicación de los recursos en un README de perfil.

#### Scenario: Configuración desde la documentación
- **WHEN** una persona configura un workflow siguiendo el README
- **THEN** puede generar los dos recursos del moonwalker en su repositorio y referenciarlos desde su README

#### Scenario: Uso local existente
- **WHEN** una persona prefiere generar recursos fuera de GitHub Actions
- **THEN** el README conserva instrucciones para instalar y ejecutar el CLI local
