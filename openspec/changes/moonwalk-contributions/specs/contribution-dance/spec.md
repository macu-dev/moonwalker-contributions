# Spec Delta

## Purpose

Esta capacidad transforma el calendario de contribuciones de GitHub en una pista animada que comunica la actividad y se recorre con moonwalk continuo y brillo temporal por baldosa.

## ADDED Requirements

### Requirement: Representación de actividad en la cuadrícula
La visualización SHALL representar cada día del calendario de contribuciones como una baldosa y SHALL variar su intensidad visual según la cantidad de contribuciones de ese día.

#### Scenario: Día con contribuciones
- **WHEN** un día contiene una o más contribuciones
- **THEN** su baldosa se ilumina con una intensidad correspondiente a su nivel de actividad

#### Scenario: Día sin contribuciones
- **WHEN** un día no contiene contribuciones
- **THEN** su baldosa permanece visible con el nivel base de iluminación

### Requirement: Recorrido con moonwalk y brillo por baldosa
El personaje SHALL recorrer toda la cuadrícula haciendo moonwalk de espaldas al desplazamiento y SHALL activar un brillo temporal en cada baldosa visitada, preservando la distinción entre niveles de actividad.

#### Scenario: Recorrido de una baldosa
- **WHEN** el personaje pisa una baldosa durante el moonwalk
- **THEN** la baldosa muestra un halo y mayor luminosidad, y vuelve a su color base cuando el personaje pasa a la siguiente

#### Scenario: Día sin actividad
- **WHEN** el personaje pisa una baldosa sin contribuciones
- **THEN** también brilla temporalmente y después recupera su nivel base

#### Scenario: Moonwalk por las filas
- **WHEN** el personaje recorre las baldosas interiores
- **THEN** mantiene un pie plano que desliza y otro de apoyo en punta, sin elevar el pie plano ni caminar hacia adelante

### Requirement: Entrada y salida del moonwalk
La animación SHALL ejecutar un moonwalk corto junto al inicio de la cuadrícula antes del recorrido, y otro junto al final después de visitar todas las baldosas, seguido de una pose final antes de reiniciar.

#### Scenario: Inicio del recorrido
- **WHEN** comienza el ciclo
- **THEN** el personaje ejecuta el moonwalk cerca de la primera baldosa y continúa el moonwalk desde ella

#### Scenario: Cierre del recorrido
- **WHEN** termina de recorrer todas las baldosas
- **THEN** ejecuta el moonwalk junto al extremo final y mantiene una pose antes de reiniciar

#### Scenario: Transferencia de peso en los extremos
- **WHEN** el personaje ejecuta moonwalk al inicio o al final
- **THEN** muestra el cuerpo de perfil de espaldas al desplazamiento y cambia los talones sin saltos de posición de las puntas

#### Scenario: Reinicio del ciclo
- **WHEN** termina la pose final
- **THEN** vuelve a la secuencia inicial de moonwalk

### Requirement: Presentación visual y alternativa estática
La presentación SHALL usar una paleta de fondo oscuro con luces violetas y rosas y SHALL ofrecer una imagen estática descriptiva para contextos que no reproduzcan animación.

#### Scenario: Visualización animada en el README
- **WHEN** GitHub muestra el recurso animado en el README
- **THEN** se reproduce el moonwalk inicial, el moonwalk continuo con brillo y el moonwalk final con la paleta definida

#### Scenario: Contexto sin animación
- **WHEN** el recurso animado no puede reproducirse o el usuario prefiere contenido estático
- **THEN** hay una alternativa estática que conserva la cuadrícula y una descripción accesible

### Requirement: Configuración de la cuenta objetivo
El generador SHALL aceptar el nombre de usuario de GitHub objetivo mediante una opción documentada, sin requerir cambios en el código fuente.

#### Scenario: Configurar otra cuenta
- **WHEN** una persona proporciona un nombre de usuario válido de GitHub al ejecutar el generador
- **THEN** la generación consulta y representa las contribuciones de esa cuenta

#### Scenario: Credencial ausente o inválida
- **WHEN** la fuente de datos necesita una credencial y esta falta o no es válida
- **THEN** la generación informa el error sin imprimir el valor de la credencial ni reemplazar recursos válidos existentes

### Requirement: Uso reproducible del generador
El proyecto SHALL documentar cómo instalar sus dependencias y ejecutar la generación localmente con la configuración requerida.

#### Scenario: Preparar y ejecutar el generador
- **WHEN** una persona sigue la documentación con una versión de Python compatible y la configuración necesaria
- **THEN** puede generar el GIF y su alternativa estática, o recibe un error que identifica la configuración faltante

### Requirement: Personaje de referencia
El bailarín SHALL conservar el estilo pixel art, traje claro, camisa azul y sombrero claro del personaje adjunto, con zapatos oscuros y perfil legible durante el moonwalk.

#### Scenario: Cambio de sentido en la cuadrícula
- **WHEN** cambia el sentido horizontal del recorrido
- **THEN** el personaje invierte su orientación para mirar de espaldas al avance en cada fila

## REMOVED Requirements

### Requirement: Recorrido de moonwalk
**Reason**: Se reemplaza el requisito inicial por el contrato de moonwalk continuo con brillo temporal.
**Migration**: Usar Recorrido con moonwalk y brillo por baldosa.

### Requirement: Coreografía de cierre
**Reason**: El cierre usa moonwalk y pose en lugar de la coreografía inicial.
**Migration**: Usar Entrada y salida del moonwalk.

### Requirement: Recorrido a pie y brillo por pisada
**Reason**: El usuario confirmó que quiere moonwalk durante todo el recorrido.
**Migration**: Usar Recorrido con moonwalk y brillo por baldosa.

### Requirement: Moonwalk en los extremos
**Reason**: El moonwalk ya no queda limitado a los extremos.
**Migration**: Usar Entrada y salida del moonwalk y Recorrido con moonwalk y brillo por baldosa.
