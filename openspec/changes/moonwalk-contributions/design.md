# Design

## Context

El repositorio no contiene código, README ni especificaciones previas; OpenSpec acaba de inicializarse. El generador será un proyecto Python open source y debe poder instalarse y ejecutarse desde un checkout limpio. La salida se incrustará en un README de GitHub, que no reproduce animaciones SVG. La especificación de comportamiento está en `specs/contribution-dance/spec.md`.

## Goals / Non-Goals

**Goals:**
- Generar de forma repetible una animación GIF optimizada y una imagen estática de respaldo desde datos de contribuciones.
- Separar el recorrido por el calendario de la coreografía final para que el orden narrativo sea inequívoco.
- Mantener la generación dentro de GitHub Actions y publicar los recursos en el repositorio.
- Permitir el uso local mediante una interfaz de línea de comandos y configuración documentada, sin exigir modificar el código.
- Facilitar revisión y contribuciones comunitarias con metadatos de paquete, licencia y guía de contribución.
- Mantener límites claros entre consulta de datos, renderizado, interfaz CLI y publicación automatizada.

**Non-Goals:**
- Crear una aplicación web interactiva o un servicio de alojamiento dinámico.
- Publicar o alojar una API propia para recolectar contribuciones.
- Replicar el rostro o una representación fotorrealista de una persona específica; el bailarín será una interpretación en pixel art del personaje de referencia, con traje marfil, camisa azul y fedora.
- Animar el movimiento de cada pixel de la cuadrícula con fidelidad física; se priorizan legibilidad, tamaño y fluidez suficiente en el README.

## Decisions

1. **Implementar el generador como paquete Python instalable.** Declarar metadatos, versión mínima compatible y dependencias en `pyproject.toml`, y exponer un comando local que recibe el usuario objetivo mediante `--username`. Así las personas que lo usen y GitHub Actions ejecutan el mismo código. Se consideró mantener un script aislado, pero un paquete con interfaz explícita hace más reproducibles las instalaciones y facilita contribuir.

2. **Usar Pillow para dibujar y exportar la animación.** El generador compone cuadros de imagen y los guarda como GIF animado junto a un respaldo estático. Pillow documenta escritura de GIFs con múltiples cuadros. Se consideró producir SVG desde Python, pero GitHub no reproduce su animación en README. La documentación de Pillow: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html

3. **Generar los datos y recursos en un workflow de GitHub Actions.** El workflow se ejecutará con una frecuencia diaria configurable y también manualmente. Instalará el paquete según sus metadatos, consultará el calendario de la cuenta indicada y generará los archivos del README. Cuando se necesite autenticación, leerá el token desde la variable de entorno `GITHUB_TOKEN`; no lo aceptará en argumentos ni lo imprimirá en logs. El permiso de escritura se limitará a publicar archivos generados cuando el workflow deba hacer un commit.

4. **Mantener una fuente de datos y dos fases de animación.** El generador recibirá la cuadrícula con el nivel de contribución de cada día. La fase uno desliza al personaje por todas las baldosas con el torso inclinado hacia atrás y alterna los talones levantados con los pies que se deslizan hacia atrás, siguiendo la secuencia de referencia; resalta cada baldosa al pasar e interpola posiciones para que el movimiento no parezca una carrera. La fase dos lo mantiene en el extremo final y reproduce unos pocos pasos de coreografía y una pose. Al terminar, el GIF vuelve al primer cuadro.

5. **Diseñar primero para lectura en el ancho del README.** Se usarán fondo oscuro, luces violetas y rosas, contraste suficiente, texto mínimo y un personaje en pixel art con traje marfil, camisa azul, fedora claro y zapatos oscuros. La intensidad base seguirá comunicando los niveles diarios incluso cuando el brillo de paso desaparezca. El GIF se limitará en dimensiones, cantidad de cuadros y paleta para reducir peso y evitar que el detalle del calendario se vuelva ilegible.

6. **Actualizar artefactos de forma segura.** El README apuntará a una ruta estable dentro del repositorio. El workflow regenerará los recursos y solo creará un commit cuando haya cambios; no reescribirá el README completo. Si falla la consulta de datos, conservará los últimos recursos publicados y dejará el workflow en estado fallido para que el problema sea visible.

7. **Documentar el uso y las contribuciones de forma pública.** El README explicará la versión de Python compatible, instalación, configuración de la cuenta y generación local; una guía para colaborar describirá cómo proponer cambios. La licencia MIT elegida por el mantenedor se incluye en `LICENSE`.

8. **Automatizar estándares de estilo y tipos.** Seguir PEP 8, usar nombres descriptivos, mantener módulos y funciones enfocados, y añadir type hints y docstrings a las APIs públicas. Configurar Ruff como linter y formateador, y mypy en modo estricto para el paquete. Las reglas y la versión objetivo de Ruff se declararán en `pyproject.toml`; las comprobaciones se ejecutarán en CI junto con las pruebas. Se evita añadir herramientas separadas para formato e imports porque Ruff cubre esas tareas.

## Risks / Trade-offs

- [El calendario requiere autorización de API o el token puede perder validez] → Usar un secreto de GitHub Actions con permisos mínimos, documentar su configuración y validar la respuesta antes de reemplazar recursos.
- [El GIF puede pesar demasiado o verse borroso] → Limitar cuadros, dimensiones y colores, optimizar el archivo y revisar la lectura a tamaño real del README.
- [El workflow puede producir commits repetidos o conflictos] → Ejecutar un solo trabajo concurrente para esta salida y escribir únicamente archivos generados; omitir el commit si no hay diferencias.
- [La API puede exponer menos contribuciones que las esperadas por la cuenta o su configuración de privacidad] → Documentar el alcance del calendario y permitir indicar la cuenta objetivo sin exponer credenciales.
- [Las versiones de Python o de Pillow pueden producir diferencias en los recursos generados] → Declarar la versión mínima compatible y las dependencias, generar artefactos con versiones fijadas en CI y verificar salidas de muestra.
- [El chequeo estricto de tipos puede requerir esfuerzo adicional al integrar cambios] → Aplicarlo al código de producción, mantener las excepciones justificadas y ejecutar las mismas comprobaciones localmente y en CI.

## Migration Plan

1. Crear el paquete Python, declarar sus dependencias y producir recursos iniciales a partir de datos de contribuciones de muestra.
2. Documentar cómo instalar y ejecutar el generador, y añadir la licencia elegida y la guía de contribución.
3. Configurar el secreto de lectura requerido y añadir el workflow con disparadores programado y manual.
4. Insertar la imagen animada y su alternativa estática en el README.
5. Ejecutar manualmente el workflow, revisar el resultado en el README publicado y luego dejar activa la actualización programada.

Para revertir, quitar del README las referencias al recurso, desactivar el workflow y restaurar o eliminar los archivos generados en un commit.

## Open Questions

- ¿Qué usuario de GitHub debe alimentar el calendario? La implementación deja esta cuenta en una configuración explícita y no la infiere de datos personales.
- ¿Qué frecuencia de actualización conviene finalmente: diaria o semanal? El workflow empieza con ejecución diaria configurable.

## Corrección visual del moonwalk

La revisión del usuario evidencia que la primera corrección seguía pareciendo caminar. Los reinicios discretos de los pies y la vista frontal del torso impedían leer el gesto. Se sustituye por una marcha continua de perfil, con posiciones de las puntas triangulares y cambio gradual de talones sin reiniciar las posiciones en cada medio ciclo. El calzado pivota sobre su punta, que permanece a la altura del suelo; el pie plano desliza, el pie de apoyo dobla la rodilla. El cuerpo conserva la altura y se mueve horizontalmente con regularidad. El pie plano se mueve aproximadamente al doble de la velocidad del cuerpo y el apoyo se mantiene en un punto horizontal.

Se muestrean cuatro cuadros por intervalo entre celdas, a 50 ms por cuadro. La fase de pies sigue la distancia real de avance, con una zancada completa de 56 px. Se representa traje marfil, camisa azul, fedora y zapatos oscuros en una vista lateral más estrecha, con piernas diferenciadas por sombreado. Se exporta además una muestra ampliada corta para poder revisar el paso sin esperar el recorrido anual.

Referencia cinemática: Ferreira, Lisboa y Silva (2025), https://www.scielo.br/j/rbef/a/j8MyTX9xTw7skQRrrYPGmHd/. El ciclo es una interpretación simplificada; no se afirma reproducción exacta de la coreografía personal de Michael Jackson.

## Caminata luminosa y moonwalk en los extremos

Esta decisión sustituye las decisiones anteriores sobre moonwalk durante todo el recorrido y coreografía de cierre. La secuencia vigente es moonwalk inicial → caminata por las siete filas → moonwalk final → pose. Cada moonwalk dura un ciclo de 16 pasos más un cuadro de llegada y ocupa 56 px junto a su extremo, sin saltar de posición al cambiar de fase. El recorrido mira hacia adelante y alterna apoyo con elevación del pie libre.

La baldosa actual recibe halo y mezcla luminosa de su color con el acento; al avanzar se recupera la intensidad original. Se alinea la planta de los zapatos con el centro de la baldosa. Para mostrar el sombrero entero sobre la primera fila, se aumenta el margen superior de la cuadrícula y la altura del lienzo a 224 px. Se conservan el ancho de 960 px, los niveles de actividad y la exportación GIF/PNG.

La caminata usa una zancada de 28 px en ocho cuadros, con apoyo fijo y elevación sinusoidal del pie libre. Su paso más corto mantiene el zapato sobre la baldosa resaltada.

## Restaurar moonwalk continuo (decisión vigente)

El usuario confirmó explícitamente moonwalk durante todo el recorrido con brillo en cada cuadrado. Esto sustituye la decisión anterior de caminata con moonwalk solo en los extremos. Se conserva el recorrido, los halos y la alineación vertical del calzado, y se usa el perfil de moonwalk de espaldas al avance en todas las filas. La cinemática mantiene el pie de apoyo fijo horizontalmente mientras el pie plano desliza; ambos permanecen en el suelo. Se conservan las breves secuencias de entrada y salida y la pose final, sin añadir caminata hacia adelante.
