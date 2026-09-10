# YomCeph Desktop · Investigación

Versión de escritorio para Windows orientada a medición manual de radiografías laterales de cráneo.

## Funciones incluidas

- Apertura de PNG, JPG, JPEG, TIFF y BMP.
- Zoom con rueda del ratón y desplazamiento con botón derecho.
- Colocación y ajuste manual de landmarks.
- Guía breve para localizar cada punto.
- Cálculo de SNA, SNB, ANB, SN–PoOr, SN–GoGn, SN–OPT, SN–CVT y OPT–CVT.
- Análisis del plano vertebral mediante tangente C2–C7 y punto de profundidad cervical.
- Calibración opcional para convertir la profundidad cervical a milímetros.
- Esquema visual de lordosis, rectificación, cifosis e hiperlordosis.
- Interpretación de resultados respecto a los rangos configurados en el protocolo.
- Guardado y reapertura de proyectos.
- Exportación de resultados a CSV.
- Exportación de radiografía con puntos y líneas.

## Plano vertebral

Para la valoración cuantitativa se marcan:

- `C2ps`: punto posterior superior de C2.
- `C7pi`: punto posterior inferior de C7.
- `PC`: punto de máxima profundidad de la curvatura respecto a la tangente C2–C7.

Si la radiografía está calibrada, el programa calcula la distancia en milímetros. El intervalo 7–15 mm se presenta expresamente como referencia del protocolo aportado por el investigador y no como diagnóstico clínico universal.

Para postura craneocervical también se marcan `cv2tg`, `cv2ip` y `cv4ip`, con los que se calculan SN–OPT, SN–CVT y OPT–CVT.

## Crear el EXE

El workflow `Build Windows EXE` usa GitHub Actions en `windows-latest` y PyInstaller. El artefacto final se llama `YomCeph_Desktop.exe`.

Uso educativo y de investigación. No sustituye valoración profesional.
