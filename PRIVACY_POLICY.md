# Política de privacidad de YomCeph

**Última actualización: 11 de septiembre de 2026**

YomCeph es una herramienta educativa y de apoyo a investigación para trazados cefalométricos. Este repositorio contiene versiones para distintas plataformas; las funciones de red pueden diferir entre YomCeph Desktop y la aplicación Android.

## Responsable y contacto

YomCeph es un proyecto mantenido en el repositorio público de GitHub `yomismtz/-ngulos-cefalometricos`.

Para consultas sobre privacidad o incidencias puede utilizarse:

https://github.com/yomismtz/-ngulos-cefalometricos/issues

## Datos que puede manejar YomCeph

Según la función utilizada, YomCeph puede trabajar con información introducida o seleccionada directamente por el usuario, como:

- radiografías e imágenes;
- identificadores de caso o paciente introducidos por el usuario;
- nombre y protocolo de una investigación;
- edad y fechas;
- sexo registrado e identidad de género opcional;
- país, institución y variables de agrupación del estudio;
- landmarks cefalométricos;
- calibración;
- mediciones, control de calidad y resultados.

Por su naturaleza, una radiografía y los datos asociados pueden constituir información personal y relacionada con la salud.

## Finalidad

Los datos se utilizan para las funciones solicitadas por el usuario: visualizar una radiografía, seleccionar análisis, colocar landmarks, calibrar, calcular mediciones, guardar y revisar casos, organizar una investigación y exportar resultados.

## Almacenamiento de estudios

Los datos clínicos y de investigación de YomCeph Desktop se procesan y almacenan **localmente en el equipo**. La base de datos, las copias de radiografías, los protocolos y los historiales se mantienen fuera de la carpeta de instalación para que una actualización del programa no los sustituya.

YomCeph Desktop:

- no requiere una cuenta;
- no contiene anuncios;
- no utiliza analítica de uso;
- no incluye telemetría del desarrollador;
- no sube automáticamente radiografías, identificadores de pacientes, landmarks ni resultados a servidores del desarrollador.

La versión Android descrita por la documentación actual del proyecto mantiene sus estudios localmente y no utiliza permiso `INTERNET`. Si esa situación cambia, esta política y las declaraciones de la tienda deberán actualizarse antes de publicar la versión correspondiente.

## Actualizaciones de YomCeph Desktop

YomCeph Desktop v0.12 puede consultar automáticamente la API pública de **GitHub Releases** al iniciar para saber si existe una versión nueva. Esta consulta está separada de la base clínica y no transmite radiografías, información de pacientes, landmarks, resultados ni contenido de investigaciones.

Como en cualquier conexión HTTPS, GitHub puede procesar datos técnicos necesarios para prestar el servicio, como dirección IP, fecha/hora, agente de usuario y la versión instalada que se incluye en el agente de usuario de YomCeph.

Cuando existe una actualización:

1. YomCeph informa al usuario y solicita confirmación antes de instalarla.
2. El instalador y su checksum se descargan mediante HTTPS desde la publicación oficial del repositorio.
3. YomCeph calcula y verifica SHA-256 antes de ejecutar el instalador.
4. Si existe un caso con cambios sin guardar, la instalación no se inicia.
5. Si no hay conexión a Internet, YomCeph continúa funcionando localmente.

La comprobación de actualizaciones no se utiliza para analítica, perfiles de uso ni seguimiento de pacientes.

## Exportación y compartición

El usuario puede exportar archivos como Excel, CSV, sintaxis para IBM SPSS, imágenes o informes. La compartición con otras aplicaciones o servicios se produce únicamente por decisión del usuario. Una vez entregado un archivo a un tercero, el tratamiento posterior depende de las políticas de ese tercero.

## Investigación

YomCeph permite definir protocolos con muestra, rango de edad, criterios de inclusión/exclusión, grupos y variables cefalométricas. La aplicación puede ayudar a marcar casos como incluidos, no elegibles o pendientes y a producir estadística descriptiva, pero la aprobación ética, consentimiento/autorizaciones y base legal del tratamiento corresponden al investigador y a su institución.

Para docencia e investigación se recomienda utilizar identificadores codificados y radiografías anonimizadas siempre que sea posible.

## Conservación y eliminación

Los estudios permanecen en el dispositivo o equipo hasta que el usuario los elimina o borra los archivos locales correspondientes. YomCeph no mantiene una copia clínica en un servidor del desarrollador.

## Seguridad y uso responsable

El usuario o la institución deben proteger el equipo y las exportaciones conforme a su contexto: control de acceso, cifrado del dispositivo cuando proceda, copias de seguridad autorizadas y manejo adecuado de información identificable.

## Público previsto

YomCeph está orientada principalmente a estudiantes universitarios, docentes, investigadores y profesionales de odontología/ortodoncia. No está diseñada específicamente para niños como usuarios de la aplicación.

## Aviso médico

YomCeph es una herramienta educativa y de apoyo a investigación/trazado. No sustituye la evaluación clínica de un profesional sanitario y no debe utilizarse como único fundamento para diagnóstico o tratamiento. Una medición aislada no constituye un diagnóstico independiente.

## Cambios futuros

Esta política se actualizará antes de incorporar cuentas, almacenamiento clínico en la nube, sincronización, telemetría, anuncios u otras funciones que transmitan información adicional fuera del dispositivo. La política publicada debe corresponder siempre al comportamiento real de la versión distribuida.
