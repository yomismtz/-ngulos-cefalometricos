# YomCeph Desktop v0.12.0

YomCeph v0.12 reorganiza la aplicación alrededor de dos flujos separados: **Caso individual** e **Investigación**.

## Caso individual

- No entra en estadísticas de investigación.
- Permite seleccionar uno o varios análisis disponibles.
- Permite seleccionar sólo las mediciones necesarias.
- La lista de landmarks se reduce automáticamente a la unión de puntos requeridos.

## Investigación

Cada estudio guarda su propio protocolo:

- nombre;
- muestra planeada de 1 a 1000 casos;
- permiso opcional para aumentar la muestra posteriormente;
- rango de edad;
- criterios de inclusión y exclusión;
- país e institución;
- variables configurables de procedencia/grupo/momento;
- análisis seleccionados;
- mediciones seleccionadas;
- conjunto de referencia Steiner, si se desea clasificación.

La edad se valida al capturar cada caso. Los casos fuera del intervalo se marcan como `not_eligible`. Los demás criterios son confirmados explícitamente por el investigador. Después del primer caso incluido, el protocolo queda bloqueado contra cambios silenciosos; sólo puede incrementarse la muestra si esa opción fue permitida.

## Análisis disponibles en esta versión

- Steiner, conservando por separado el protocolo UAM 2026 y una referencia clásica publicada.
- Postura craneofacial/cervical ya existente.
- Powell ya existente y corregido con Dn separado de Prn.
- Wits AO–BO.
- Björk–Jarabak.
- YEN.
- W.

El catálogo también muestra análisis en validación (Rocabado completo, McNamara, vías aéreas, Downs, Tweed, Ricketts, COGS, Sassouni, Bimler, G-triangle) sin inventar resultados. Alexander queda como referencia metodológica y Ritucci–Burstone se marca como otra proyección porque el método de asimetría publicado utiliza SMV.

## Exportación científica

Una investigación puede exportarse como:

- Excel `.xlsx` con hojas `Datos`, `Descriptivos`, `Frecuencias`, `Prevalencias`, `Diccionario` y `Protocolo`;
- CSV UTF-8 para interoperabilidad;
- sintaxis `.sps` para importar reproduciblemente en IBM SPSS.

Las prevalencias sólo se calculan para variables con regla categórica explícita. Las variables continuas se conservan como valores crudos y reciben estadística descriptiva.

## Base de datos

La migración es no destructiva. Los casos del estudio UAM 2026 se conservan con su identificador, puntos, mediciones y calibración actuales. Las nuevas investigaciones y los casos individuales se separan mediante identificadores internos sin alterar el ID visible del caso.

## Pruebas

El flujo CI compila el código y ejecuta pruebas para:

- consistencia del catálogo científico;
- landmarks requeridos;
- YEN;
- W;
- signo anatómico de Wits, incluida orientación invertida de perfil;
- variables Björk–Jarabak;
- reglas de elegibilidad por edad;
- bloqueo del protocolo;
- aumento de muestra autorizado.

La compilación automática no sustituye una prueba interactiva de la GUI en Windows.