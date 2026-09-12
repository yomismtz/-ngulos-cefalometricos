# Política de privacidad de YomCeph

**Última actualización: 11 de septiembre de 2026**

YomCeph es una herramienta educativa y de apoyo a investigación para trazados cefalométricos. Este repositorio contiene versiones para distintas plataformas; las funciones de red pueden diferir entre YomCeph Desktop y la aplicación Android.

## Responsable y contacto

YomCeph es un proyecto mantenido en el repositorio público de GitHub `yomismtz/Cefalometria-`.

Para consultas sobre privacidad o incidencias puede utilizarse:

https://github.com/yomismtz/Cefalometria-/issues

## Datos que puede manejar YomCeph

Según la función utilizada, YomCeph puede trabajar con información introducida o seleccionada directamente por el usuario, como radiografías e imágenes, archivos PDF que contienen radiografías, identificadores de caso, nombre y protocolo de investigación, edad y fechas, sexo registrado, identidad de género opcional, país o institución si el usuario decide registrarlos, variables de agrupación, landmarks, calibración, mediciones, control de calidad, estado de elegibilidad, motivos de exclusión y resultados.

Por su naturaleza, una radiografía y los datos asociados pueden constituir información personal y relacionada con la salud. Para docencia e investigación se recomienda utilizar identificadores codificados y radiografías anonimizadas siempre que sea posible.

## Finalidad

Los datos se utilizan para las funciones solicitadas por el usuario: visualizar una radiografía, seleccionar análisis, colocar landmarks, calibrar, calcular mediciones, guardar y revisar casos, documentar inclusión o exclusión, organizar investigaciones y exportar resultados.

## Almacenamiento de YomCeph Desktop

Los datos clínicos y de investigación de YomCeph Desktop se procesan y almacenan **localmente en el equipo**. En Windows la ruta principal actual es:

`%LOCALAPPDATA%\YomCeph\ResearchData`

En esa carpeta pueden existir la base SQLite, copias de radiografías asociadas a casos, imágenes importadas desde PDF, respaldos, preferencias visuales y archivos temporales de actualización. Se almacenan fuera de la carpeta del programa para que una actualización o reinstalación no los sustituya automáticamente.

YomCeph Desktop:

- no requiere una cuenta;
- no contiene anuncios;
- no utiliza analítica de uso del desarrollador;
- no incluye telemetría clínica;
- no sube automáticamente radiografías, identificadores de pacientes, landmarks, protocolos ni resultados a servidores del desarrollador.

La versión Android descrita por la documentación actual del proyecto mantiene sus estudios localmente y no utiliza permiso `INTERNET`. Si esa situación cambia, esta política y las declaraciones de la tienda deberán actualizarse antes de publicar la versión correspondiente.

## Sitio web público

El sitio público de YomCeph es estático y no incorpora cookies publicitarias, píxeles de seguimiento ni analítica propia de YomCeph. Las descargas se sirven desde GitHub Releases.

Al visitar el sitio, abrir GitHub o descargar un instalador, GitHub puede procesar los datos técnicos normales necesarios para prestar el servicio, como dirección IP, fecha/hora, agente de usuario y URL solicitada, de acuerdo con sus propias políticas. El sitio no tiene acceso a la base local de YomCeph ni a las radiografías almacenadas en el equipo.

## Actualizaciones de YomCeph Desktop

YomCeph Desktop v0.12.5 consulta automáticamente la API pública de **GitHub Releases** poco después de iniciar para saber si existe una versión nueva. Esta consulta está separada de la base clínica y no transmite radiografías, información de pacientes, landmarks, protocolos, resultados ni contenido de investigaciones.

Como en cualquier conexión HTTPS, GitHub puede procesar datos técnicos necesarios para prestar el servicio, como dirección IP, fecha/hora, agente de usuario y versión instalada.

Cuando existe una actualización:

1. YomCeph informa al usuario y solicita confirmación antes de instalarla.
2. El instalador y su checksum se descargan mediante HTTPS desde la publicación oficial del repositorio.
3. YomCeph calcula y verifica SHA-256 antes de ejecutar el instalador.
4. Si existe un caso con cambios sin guardar, la instalación no se inicia.
5. Si no hay conexión a Internet, YomCeph continúa funcionando localmente.

La comprobación de actualizaciones no se utiliza para analítica, perfiles de uso ni seguimiento de pacientes.

## Personalización visual

YomCeph Desktop permite elegir tipografía, tamaño de letra y una de cinco paletas de color. Las preferencias se guardan localmente en el perfil de YomCeph y no contienen radiografías, resultados ni identificadores clínicos.

La personalización sólo modifica la presentación de la interfaz. No cambia la radiografía, coordenadas de landmarks, calibración, fórmulas, referencias seleccionadas ni resultados guardados.

## Exportación y compartición

El usuario puede exportar archivos como Excel, CSV, sintaxis para IBM SPSS, imágenes o informes. La compartición con otras aplicaciones o servicios se produce únicamente por decisión del usuario. Una vez entregado un archivo a un tercero, el tratamiento posterior depende de las políticas de ese tercero.

## Investigación y elegibilidad

YomCeph permite definir protocolos con muestra, rango de edad, país/procedencia, criterios de inclusión/exclusión, grupos y variables cefalométricas. En Desktop v0.12.5 la radiografía puede abrirse y trazarse antes de completar la ficha final del sujeto.

Al finalizar un caso de investigación, YomCeph puede evaluar reglas objetivas derivadas del protocolo, como rango de edad, país/procedencia, disponibilidad de los landmarks requeridos y calibración cuando se seleccionaron mediciones lineales. El investigador también puede registrar motivos radiográficos de exclusión, por ejemplo calidad insuficiente, anatomía recortada, artefactos, proyección inadecuada, imposibilidad de identificar puntos o un motivo adicional.

Los motivos de elegibilidad se guardan localmente con el caso para trazabilidad. Un caso excluido puede conservarse en la base pero permanece separado de la muestra incluida. La aprobación ética, consentimiento/autorizaciones y base legal del tratamiento corresponden al investigador y a su institución.

## Conservación y eliminación

Los estudios permanecen en el equipo hasta que el usuario elimina los registros o borra los archivos locales correspondientes. **Desinstalar YomCeph Desktop no elimina por defecto `%LOCALAPPDATA%\YomCeph\ResearchData`**, precisamente para evitar pérdida accidental durante una reinstalación o actualización.

Si el usuario desea retirar completamente los datos después de desinstalar, debe revisar y, si corresponde, eliminar manualmente esa carpeta después de conservar los respaldos necesarios. YomCeph no mantiene una copia clínica paralela en un servidor del desarrollador.

## Seguridad y uso responsable

El usuario o la institución deben proteger el equipo y las exportaciones conforme a su contexto: control de acceso, cifrado del dispositivo cuando proceda, copias de seguridad autorizadas y manejo adecuado de información identificable.

YomCeph Desktop incorpora comprobaciones para advertir sobre cambios locales sin guardar antes de cerrar, cargar otro caso, cambiar de flujo o iniciar una actualización. Estas protecciones reducen el riesgo de pérdida accidental, pero no sustituyen las copias de seguridad ni las políticas institucionales de conservación.

## Público previsto

YomCeph está orientada principalmente a estudiantes universitarios, docentes, investigadores y profesionales de odontología/ortodoncia. No está diseñada específicamente para niños como usuarios de la aplicación.

## Aviso médico

YomCeph es una herramienta educativa y de apoyo a investigación/trazado. No sustituye la evaluación clínica de un profesional sanitario y no debe utilizarse como único fundamento para diagnóstico o tratamiento. Una medición aislada no constituye un diagnóstico independiente.

## Cambios futuros

Esta política se actualizará antes de incorporar cuentas, almacenamiento clínico en la nube, sincronización, telemetría, anuncios u otras funciones que transmitan información adicional fuera del dispositivo. La política publicada debe corresponder siempre al comportamiento real de la versión distribuida.
