# Tasks

## 1. Crear la base del proyecto Python

- [x] 1.1 Crear el paquete Python, su interfaz de línea de comandos y metadatos en `pyproject.toml`, declarando la versión mínima compatible, Pillow y dependencias de desarrollo; configurar Ruff para lint y formato, y mypy en modo estricto; verificar instalación limpia y que `ruff check`, `ruff format --check` y `mypy --strict` pasan sobre el paquete inicial.
- [x] 1.2 Añadir configuración explícita de `--username` y lectura opcional de credenciales desde `GITHUB_TOKEN`; dar nombres descriptivos, type hints y docstrings a las APIs públicas; verificar con pruebas que la cuenta se cambia sin editar código, el secreto nunca aparece en argumentos ni logs, y los chequeos de estilo y tipos pasan.

## 2. Obtener y validar contribuciones

- [x] 2.1 Implementar la consulta y conversión del calendario a datos por fecha e intensidad en módulos cohesionados; verificar con fixtures que preserva semanas, fechas y días sin actividad y que pasan las pruebas, Ruff y mypy.
- [x] 2.2 Añadir pruebas para respuestas inválidas, errores de API y credenciales ausentes; verificar que los errores son claros, los recursos existentes quedan intactos y los chequeos de calidad siguen pasando.

## 3. Crear y exportar la animación

- [x] 3.1 Implementar el render de cuadrícula y bailarín con la paleta citypop, separando composición de datos; verificar mediante pruebas de salida que la actividad cambia el nivel base de cada baldosa y pasan Ruff y mypy.
- [x] 3.2 Implementar el recorrido moonwalk con inclinación hacia atrás, alternancia de talones y deslizamiento según la secuencia de referencia, más coreografía final y pose; verificar cuadros clave y orden recorrido → coreografía → pose → reinicio con pruebas automatizadas.
- [x] 3.3 Exportar GIF optimizado y respaldo estático usando Pillow; verificar dimensiones, peso, número de cuadros, apertura de ambos recursos y legibilidad al ancho del README.

## 4. Documentar el proyecto open source

- [x] 4.1 Crear README con instalación Python, uso local, configuración de cuenta, token opcional, GIF y alternativa estática; verificar que cada comando documentado funciona desde un checkout limpio.
- [x] 4.2 Añadir guía de contribución con convenciones de nombres, docstrings, type hints y comandos locales de Ruff, mypy y pruebas, además de plantillas para reportes o cambios; verificar que una persona colaboradora puede seguir el flujo desde un checkout limpio.
- [x] 4.3 Elegir con el mantenedor e incluir una licencia open source; verificar que el archivo de licencia coincide con la elección documentada.

## 5. Automatizar actualización en GitHub Actions

- [x] 5.1 Crear workflow programado configurable y ejecutable manualmente que instale el paquete Python y use los secretos como variables de entorno; ejecutar Ruff, mypy y pruebas en CI y verificar que pasan con permisos mínimos.
- [x] 5.2 Publicar únicamente los recursos generados cuando cambien; verificar que una segunda ejecución sin diferencias no crea un commit y que los errores conservan los recursos previos.
- [x] 5.3 Añadir instrucciones para configurar el workflow y los secretos; verificar que no se almacena ningún token en archivos versionados ni aparece en logs.

## 6. Revisar la integración publicada

- [ ] 6.1 Ejecutar el workflow manualmente y revisar el README en GitHub; verificar reproducción del GIF, coreografía posterior al recorrido, lectura de la cuadrícula y acceso al respaldo estático.

## 7. Corregir personaje y moonwalk según la referencia

- [x] 7.1 Sustituir la silueta por un personaje pixel art de traje claro, camisa azul, sombrero claro y zapatos oscuros; revisar cuadros clave.
- [x] 7.2 Corregir la orientación y el apoyo de los pies, mantener el torso estable y ralentizar el ciclo; probar apoyo horizontal y cambios de sentido.
- [x] 7.3 Regenerar el GIF y PNG de demostración; verificar lectura visual, peso, reproducción, Ruff, mypy y pruebas.

## 8. Corregir continuidad y vista lateral del paso

- [x] 8.1 Rehacer el paso con posiciones continuas, talones que pivotan sobre la punta y piernas diferenciadas; probar continuidad en los cambios de apoyo y en el cierre del ciclo.
- [x] 8.2 Dibujar un perfil auténtico del personaje con el vestuario de referencia, rodilla de apoyo flexionada y pierna deslizante extendida; revisar una muestra ampliada en movimiento.
- [x] 8.3 Aumentar el muestreo espacial, regenerar GIF y PNG y una muestra corta del paso; verificar peso, tiempos, pruebas, Ruff y mypy.

## 9. Caminata con brillo y moonwalk en extremos

- [x] 9.1 Cambiar la secuencia a moonwalk inicial, caminata hacia adelante por todas las baldosas, moonwalk final y pose; verificar fases y continuidad de posiciones.
- [x] 9.2 Añadir caminata con elevación alterna de pies, halo por pisada y alineación con las baldosas; probar preservación de niveles y recuperación del brillo.
- [x] 9.3 Regenerar GIF y PNG, revisar cuadros de fases y ejecutar pruebas, Ruff, mypy y validación OpenSpec.

## 10. Restaurar moonwalk continuo con brillo

- [x] 10.1 Sustituir la caminata por moonwalk en todas las filas, mantener el brillo temporal y comprobar orientación, apoyo y cobertura de todos los días.
- [x] 10.2 Regenerar GIF anual, muestra corta y PNG; comprobar continuidad entre fases, pruebas, Ruff, mypy y sincronizar especificaciones.

## Workflow follow-up

- Archivar el cambio después de implementar y verificar los criterios de aceptación.

## Verificación de la corrección visual

- 28 pruebas aprobadas, incluidos apoyo horizontal fijo, orientación opuesta al avance y torso estable.
- Ruff (lint y formato) y mypy estricto aprobados.
- GIF de 960 × 180, 745 cuadros, bucle continuo y 790595 bytes; PNG de respaldo regenerado.
- Revisión local de las ocho poses y de un cuadro sobre el calendario.
- La tarea 6.1 de revisión del workflow y README en GitHub sigue pendiente; el cambio permanece activo.

## Verificación de continuidad y perfil

- 31 pruebas aprobadas, incluidas continuidad de ambas puntas y talones en cambio de apoyo y reinicio, velocidad del pie plano y contacto de apoyo estable con el redondeo real del calendario.
- Ruff y mypy estricto aprobados.
- GIF anual: 960 × 180, 1485 cuadros, 1371679 bytes; PNG regenerado.
- Muestra ampliada del paso: 720 × 240, 64 cuadros, 50 ms por cuadro, 119365 bytes.
- Revisión visual de las 16 poses laterales y de un cuadro sobre el calendario. La semejanza con el estilo personal de Michael Jackson queda sujeta a la evaluación visual del usuario.

## Verificación de caminata luminosa

- 32 pruebas aprobadas; Ruff y mypy estricto aprobados.
- Fases verificadas: moonwalk inicial → caminata → moonwalk final → pose, sin saltos de posición entre fases.
- Todos los días se resaltan durante la caminata, incluido el nivel sin actividad; los niveles siguen diferenciados y se recupera el color base después de la pisada.
- GIF anual: 960 × 224, 1516 cuadros, 1347637 bytes. Muestra corta: 600 × 448, 200 cuadros, 392136 bytes.
- PNG regenerado y revisión visual local del zapato alineado con la baldosa iluminada. OpenSpec validado en modo estricto.
- La revisión del workflow en GitHub (6.1) continúa pendiente; el cambio permanece activo.

## Verificación de moonwalk continuo restaurado

- 33 pruebas aprobadas; Ruff y mypy estricto aprobados.
- Todas las fases móviles usan el paso moonwalk, mirando de espaldas al desplazamiento. El pie plano no se eleva y el apoyo permanece fijo horizontalmente durante el deslizamiento.
- Se mantienen el halo por baldosa y la recuperación de su color base al pasar a la siguiente.
- GIF anual: 1516 cuadros y 1428280 bytes; muestra corta: 200 cuadros y 410487 bytes; PNG regenerado.
- Cambio todavía activo por la revisión de GitHub pendiente (6.1).
