# Moonwalk Contributions

Una animación del calendario de contribuciones de GitHub, recorrido por un moonwalker en pixel art. El gráfico incluye los días y meses, el total anual y una escala de intensidad; el bailarín recorre cada casilla y enciende brevemente cada día que pisa.

![Moonwalk sobre una cuadrícula de contribuciones de GitHub](assets/moonwalk-contributions.gif)

[Imagen PNG estática](assets/moonwalk-contributions.png) · [Vista corta del movimiento](assets/moonwalk-continuous-preview.gif)

Puedes usarlo como una GitHub Action reutilizable en el README de tu perfil o ejecutar el generador de Python localmente.

## Uso como GitHub Action

Añade un workflow al repositorio donde quieras guardar la animación. Este ejemplo actualiza las imágenes todos los días y también permite iniciar la ejecución desde **Actions → Generar moonwalk → Run workflow**:

```yaml
name: Generar moonwalk

on:
  workflow_dispatch:
  schedule:
    - cron: "17 4 * * *"

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - name: Descargar el repositorio del perfil
        uses: actions/checkout@v6

      - name: Generar el moonwalk
        uses: macu-dev/moonwalker-contributions@main
        with:
          github_user_name: ${{ github.repository_owner }}
          # Opcional para contribuciones públicas. Usa un secreto con acceso
          # read:user si necesitas incluir contribuciones privadas.
          github_token: ${{ secrets.CONTRIBUTIONS_TOKEN }}
          output_dir: assets

      - name: Publicar las imágenes modificadas
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add -- assets/moonwalk-contributions.gif assets/moonwalk-contributions.png
          if git diff --cached --quiet; then
            echo "Las imágenes del moonwalk ya están actualizadas."
            exit 0
          fi
          git commit -m "chore: actualizar animación de contribuciones"
          git push
```

La Action escribe `moonwalk-contributions.gif` y `moonwalk-contributions.png` en `output_dir`. No crea commits ni publica ramas: el workflow que la invoca decide si confirma los archivos, los carga como artefactos o los usa en pasos posteriores. Configura `contents: write` solo si el workflow necesita confirmar las imágenes.

El ejemplo usa `@main` para que funcione antes de publicar la primera versión etiquetada. Después de publicar una versión, fija la Action a su etiqueta, por ejemplo `@v1`. El repositorio que contiene la Action debe ser público o tener acceso habilitado para el repositorio que la utiliza.

Para mostrar la animación generada en el README de tu perfil, confirma las imágenes en ese repositorio y añade:

```markdown
![Mi moonwalk de contribuciones de GitHub](assets/moonwalk-contributions.gif)

[Versión estática](assets/moonwalk-contributions.png)
```

El token predeterminado es `github.token`. Para mostrar contribuciones públicas, deja vacío `github_token`. Para incluir contribuciones privadas, crea un token con acceso `read:user`, guárdalo como secreto de repositorio `CONTRIBUTIONS_TOKEN` y pásalo como en el ejemplo. El token se entrega mediante una variable de entorno y nunca se escribe en los archivos generados.

### Parámetros de la Action

| Parámetro | Obligatorio | Valor predeterminado | Descripción |
| --- | --- | --- | --- |
| `github_user_name` | Sí | — | Cuenta de GitHub cuyo calendario de contribuciones se representará. |
| `github_token` | No | `github.token` del workflow | Token para la consulta GraphQL de GitHub. |
| `output_dir` | No | `assets` | Directorio relativo dentro del workspace para guardar el GIF y el PNG. |

## Generar imágenes localmente

Requisitos: Python 3.12 o posterior. La API GraphQL de GitHub requiere un token en `GITHUB_TOKEN`.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install .
export GITHUB_TOKEN="tu-token"
moonwalk-contributions --username TU_USUARIO_DE_GITHUB --output-dir assets
```

El comando genera el mismo GIF y PNG que la Action. Si falla la consulta del calendario o la generación, conserva las imágenes existentes. El calendario representa el último año de contribuciones que devuelve GitHub. La inclusión de contribuciones privadas depende del acceso `read:user` del token y de la configuración de visibilidad de la cuenta. Consulta la [guía de autenticación GraphQL de GitHub](https://docs.github.com/en/graphql/guides/forming-calls-with-graphql) y la [referencia de contribuciones](https://docs.github.com/en/graphql/reference/users#contributionscollection).

## Desarrollo

Instala las herramientas de desarrollo y ejecuta los controles que usa CI:

```bash
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
mypy --strict
pytest
```

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para ver las convenciones de código y el proceso para colaborar.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta [LICENSE](LICENSE).
