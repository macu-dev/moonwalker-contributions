# Contribuir

Gracias por ayudar a mejorar Moonwalk Contributions. Este proyecto busca mantener una herramienta pequeña, reproducible y fácil de entender.

## Preparar el entorno

Se requiere Python 3.12 o posterior.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Calidad de código

- Sigue PEP 8 y usa nombres descriptivos en `snake_case` para funciones y variables.
- Mantén cada módulo y función enfocado en una responsabilidad; evita abstracciones que no resuelvan una necesidad concreta.
- Añade type hints y docstrings a las APIs públicas.
- Mantén la consulta a GitHub, los modelos, el render y la interfaz de línea de comandos separados.
- Las pruebas deben usar respuestas de muestra o mocks; no necesitan credenciales ni acceso a la red.
- No añadas tokens, credenciales ni otros secretos a archivos, argumentos o logs.

## Comprobaciones locales

Antes de proponer un cambio, ejecuta:

```bash
pytest
ruff check .
ruff format --check .
mypy --strict
```

La integración continua ejecuta los mismos controles. Corrige los errores de formato y lint localmente en lugar de desactivar reglas sin una razón concreta.

## Proponer cambios

1. Abre un issue para describir un error o una mejora, o revisa si ya existe uno relacionado.
2. Mantén cada pull request centrado en un cambio y explica qué problema resuelve.
3. Incluye o actualiza pruebas para el comportamiento que cambie.
4. Actualiza el README si cambia la instalación, la configuración o el uso del comando.
5. No incluyas recursos generados ni cambios de licencia sin explicar su propósito.

Usa las plantillas de issue y pull request disponibles en `.github/`.
