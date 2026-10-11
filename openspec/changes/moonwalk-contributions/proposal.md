# Proposal

## Why

El README de DiarioDevops puede convertir el calendario de contribuciones en una pieza visual que conecte la actividad de desarrollo con su estética citypop. El generador será un proyecto open source en Python para que otras personas puedan configurarlo, ejecutarlo y adaptarlo; la animación contará una secuencia clara de moonwalk continuo por las baldosas iluminadas.

## What Changes

- Añadir una visualización animada del calendario de contribuciones de GitHub, con una baldosa por día y brillo proporcional a la actividad.
- Mostrar un personaje en pixel art con traje claro, camisa azul y sombrero inspirado en la referencia adjunta que hace moonwalk por toda la cuadrícula y activa un brillo temporal en cada baldosa al pasar.
- Generar y publicar el recurso para insertarlo en el README, con actualización automatizada y una alternativa estática accesible.
- Aplicar fondo oscuro y luces violetas y rosas en línea con la identidad citypop de DiarioDevops.
- Crear un generador Python reutilizable, con configuración externa, dependencias declaradas y documentación de instalación, uso y contribución.
- Aplicar estándares de clean code en Python: módulos cohesionados, nombres descriptivos, APIs públicas tipadas y documentadas, y formato y análisis estático automatizados.
- Preparar los archivos básicos de publicación open source, incluida una licencia elegida por el mantenedor.

## Capabilities

### New Capabilities
- `contribution-dance`: Visualización de las contribuciones como una pista animada recorrida con moonwalk continuo y brillo por baldosa.

### Modified Capabilities
- Ninguna.

## Impact

- Proyecto Python open source, con metadatos y dependencias declarados en `pyproject.toml`, documentación y licencia MIT.
- README del proyecto DiarioDevops y recursos visuales generados para el calendario de contribuciones.
- Flujo de GitHub Actions y acceso de solo lectura a los datos de contribuciones mediante credenciales configuradas fuera del código.
- El formato final debe ser compatible con la reproducción en README de GitHub; se usa GIF animado y PNG estático de respaldo, porque GitHub no reproduce animaciones SVG en README.
