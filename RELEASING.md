# Política de releases

El paquete Python y la GitHub Action comparten una versión. Release Please mantiene
una PR acumulativa; fusionarla decide publicar, siempre que el commit objetivo
supere los controles. El flujo prepara un borrador, valida su SHA completo y
publica ese mismo commit. No se publica en PyPI.

## Versiones y contrato público

| Cambio | En `0.x` | Desde `1.0.0` |
| --- | --- | --- |
| `fix:` corrección compatible | PATCH | PATCH |
| `feat:` funcionalidad compatible | MINOR | MINOR |
| `!` o `BREAKING CHANGE:` incompatibilidad | MINOR | MAJOR |

El contrato público incluye las entradas `github_user_name`, `github_token` y
`output_dir` de la Action, sus valores predeterminados, los flags del CLI,
los nombres `moonwalk-contributions.gif` y `moonwalk-contributions.png`, sus
rutas documentadas y los requisitos de Python. Elevar el mínimo de Python,
eliminar un flag o renombrar una entrada son cambios incompatibles.

`chore`, `docs`, `style`, `test` y `ci` sin impacto funcional no inician releases.
Esto incluye `chore: update contribution animation`, generado a diario. Una
incompatibilidad marcada explícitamente sigue siendo publicable aunque use uno
de esos tipos. Los cambios visuales compatibles se clasifican como `feat` o `fix`
según su intención. El salto a `1.0.0` requiere una decisión explícita del
mantenedor, incorporada mediante el mecanismo `Release-As` de Release Please.

Las versiones de `pyproject.toml` y `src/moonwalk_contributions/__init__.py` se
actualizan con la estrategia Python de Release Please. CI comprueba su igualdad
con `moonwalk-contributions --version` y, al publicar, con el tag objetivo.

## Changelog y Release Notes

`CHANGELOG.md` conserva el historial acumulado. Las Release Notes de GitHub son
la sección correspondiente a la versión. Se verifican antes de publicar para
evitar divergencias. No hay otro archivo manual de notas.

Cada cambio debe explicar qué cambia, a quién afecta y cómo actualizar, o indicar
que la migración no aplica. Los títulos Conventional Commits se validan, pero
el mantenedor revisa el contenido antes de fusionar la PR de release. Las
descripciones provienen de los commits; no se traducen automáticamente.

Ejemplo de cambio incompatible:

```text
feat!: renombrar la entrada de cuenta

BREAKING CHANGE: la entrada github_user_name se reemplaza por account.
Impacto: los workflows que usen la entrada anterior deben actualizarse.
Migración: sustituir github_user_name por account en el bloque with.
```

Es un ejemplo de redacción, no un cambio real de la interfaz actual. Para
enriquecer notas generadas, usar el bloque `BEGIN_COMMIT_OVERRIDE` /
`END_COMMIT_OVERRIDE` de Release Please en la PR de origen y regenerar la PR de
release. Revisar la sección final y las instrucciones de migración antes de
fusionar; editar solo el cuerpo de la PR de release no actualiza el changelog.

## Configuración inicial en GitHub

La automatización exige configuración explícita. La preparación de PR puede
habilitarse antes de permitir publicaciones públicas.

1. Crear una GitHub App dedicada e instalarla solo en este repositorio. Otorgar
   **Contents**, **Pull requests** e **Issues** con escritura; Metadata se concede
   automáticamente. No conceder bypass de protecciones ni acceso a otros repositorios.
2. En **Settings → Environments → prod**, configurar la variable
   `RELEASE_APP_ID` y el secreto `RELEASE_APP_PRIVATE_KEY`. Los jobs `prepare` y
   `publish` declaran `environment: prod` para acceder a ellos y respetar sus
   protecciones; los jobs de calidad no necesitan ese environment. La clave se
   carga directamente en GitHub; nunca se incorpora al repositorio, argumentos o logs.
3. Habilitar squash merge y usar el título de la PR como título del commit.
   Cuando el plan lo permita, proteger `main` con revisión de PR y controles
   requeridos **Quality checks** (workflow Quality) y **Conventional title**
   (workflow PR title), seleccionando sus nombres efectivos. Exigir la revisión
   vigente y rama actualizada, sin excepciones para la App.
   Si la protección no está disponible por el plan, el mantenedor verifica
   manualmente que ambos controles aprueben sobre la última revisión, que la rama
   esté actualizada y que las notas y migraciones estén revisadas antes de fusionar.
   El bot no aprueba ni fusiona su propia PR. La generación diaria conserva sus
   permisos existentes; comprobar su convivencia con las reglas disponibles.
4. Con una sesión administrativa autenticada, verificar configuración de Actions,
   acceso de la App, protecciones, tags, releases y borradores. Registrar fecha,
   nombres de controles, resultados y enlaces en un issue o PR de este repositorio.
   Si el plan no permite proteger `main`, registrar explícitamente:
   «Protección de main no disponible por el plan; revisión manual antes del merge».
   Esta modalidad acordada permite continuar; no equivale a una protección activa.
   Un `401`, `403` o `404` inesperado bloquea esta comprobación: no prueba ausencia.
5. Configurar `RELEASE_PREFLIGHT_URL` con el enlace HTTPS a esa evidencia,
   como variable del repositorio o del environment `prod`.
   Mantener `RELEASE_AUTOMATION_ENABLED` sin definir o en `false`.
   Ejecutar **Release Please** manualmente: puede preparar la PR, pero no publicar.
6. Comprobar que la App abre/actualiza la PR y que CI arranca automáticamente sobre
   su revisión vigente. Completar la evidencia con enlaces a esas ejecuciones.
   No usar credenciales personales como sustituto silencioso de la App.
7. Recién entonces configurar `RELEASE_AUTOMATION_ENABLED=true`. Al fusionar la PR
   de release, el flujo valida y publica. No fusionarla antes de completar la
   revisión del historial, de la versión y de las notas.

La evidencia de configuración administrativa se revisa con acceso del mantenedor;
la App no necesita permisos administrativos adicionales. El workflow exige el
enlace y la activación, comprueba lectura autenticada de tags/releases y squash
merge, y falla antes de mutaciones si la autenticación no funciona. El enlace es
una constancia administrativa, no una inspección automática de todas las reglas.

Sin protección de rama, GitHub permite fusionar con controles fallidos o hacer
push directo. El mantenedor debe respetar la revisión manual. El workflow conserva
la validación obligatoria del SHA objetivo antes de publicar: una validación
fallida deja el borrador sin publicar y no actualiza tags ni alias. Esa garantía
corresponde al flujo automatizado y no impide cambios directos hechos por cuentas
con permisos de escritura. La falta de protección por el plan no exige eliminar
`RELEASE_PREFLIGHT_URL` ni activar anticipadamente la publicación.

### Estado inicial y bootstrap

Al preparar esta automatización, los metadatos locales indican `0.1.0` y no hay
tags en el checkout. La consulta pública del remoto no permitió verificar su
estado; **la comprobación autenticada sigue pendiente**. El manifiesto refleja
la versión local y no declara que ya exista una release publicada.

Antes de activar, comparar el manifiesto con tags y releases reales y reconciliar
cualquier diferencia. Sin releases anteriores, Release Please genera la primera
entrada desde el historial pertinente. No fijar `bootstrap-sha` al commit que añade
la automatización: se perdería el historial previo. No fabricar un tag `v0.1.0`
para aparentar una publicación anterior.

### Credenciales y rotación

Cada job que modifica PR o releases obtiene su propio token temporal de instalación
con `actions/create-github-app-token`; no se conserva entre jobs. La clave de la App
requiere custodia. Para rotarla, crear una nueva, sustituir el secreto de GitHub,
comprobar una ejecución y revocar la clave anterior. Si se revoca la instalación
o la clave, el flujo falla y necesita intervención del mantenedor.

## Publicación, recuperación y referencias

El flujo normal y la recuperación comparten el grupo de concurrencia
`release-publication`, sin cancelar publicaciones en curso. Primero se busca un
borrador pendiente. Si existe, se recupera antes de volver a invocar Release Please;
varios borradores, un objetivo que no es SHA completo o un tag en conflicto detienen
el flujo. No eliminar borradores para forzar otra versión sin reconciliar el estado.

La calidad del borrador se ejecuta sobre su SHA guardado, aunque `main` avance.
Antes de publicar se releen release, notas, changelog y tag; cualquier discrepancia
detiene el flujo. Una validación fallida deja el borrador sin publicar. La publicación
usa el SHA validado y comprueba el tag resultante.

Si la ejecución falla, en **Actions → Release Please → Run workflow**, ejecutar
desde `main` y completar `recover_tag` con el tag completo existente, por ejemplo
`v1.2.3`. La recuperación revalida esa versión y completa la publicación o repara
su alias. No crea otra release ni cambia tags completos. Si el tag publicado
es defectuoso, publicar una corrección con otra versión.

En `0.x`, consumir el tag completo publicado o su SHA; no se crea `v0`. Desde
`1.0.0`, se mantiene el alias `vN` de cada mayor. Los tags completos no se
reescriben. El alias solo avanza entre releases validadas del mismo mayor;
recuperar una versión anterior no lo retrocede. Si apunta a un commit desconocido,
se requiere reconciliación manual. Puede haber una ventana con el alias anterior
si GitHub falla después de publicar; reejecutar la recuperación.

Tras la primera publicación, sustituir `@main` del ejemplo del README por su tag
real. Probar la Action desde otro repositorio y registrar release, SHA, CI y
recursos generados. No anunciar una referencia todavía inexistente.

Para desactivar: poner `RELEASE_AUTOMATION_ENABLED=false` y deshabilitar el workflow;
revocar la instalación/clave cuando corresponda. Conservar changelog, releases y
tags ya publicados.

## Verificación local

Además de pytest, Ruff y mypy:

```bash
node scripts/check-version.cjs
npm install --prefix /tmp/moonwalk-release-validation --no-audit --no-fund \
  release-please@17.11.2 ajv@8.17.1 ajv-formats@3.0.1 yaml@2.8.1
NODE_PATH=/tmp/moonwalk-release-validation/node_modules node --test tests/release.test.cjs
```

Se requiere Node.js 24 para las herramientas de release; el uso de la Action y
del CLI sigue requiriendo solo Python. Las pruebas usan el motor real de Release
Please para incrementos y actualización de versiones, y una API simulada para
publicación, errores y recuperación. No sustituyen la prueba remota con la App.

Fuentes: [Release Please](https://github.com/googleapis/release-please-action),
[configuración](https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md),
[overrides](https://github.com/googleapis/release-please#how-can-i-fix-release-notes),
[tokens de GitHub App](https://github.com/actions/create-github-app-token).
