# Guía de declaraciones de Google Play — YomCeph

Actualizado: 9 de septiembre de 2026.

Este archivo resume cómo contestar Play Console **solo mientras el comportamiento técnico de la app siga siendo el actual**. Debe revisarse antes de cada publicación.

## Seguridad de los datos

Estado técnico actual:
- no existe permiso INTERNET;
- no hay anuncios;
- no hay analítica;
- no hay cuentas;
- no hay SDK de crash reporting que transmita telemetría;
- radiografías, datos del estudio y resultados se guardan localmente;
- el usuario puede exportar o compartir archivos mediante una acción iniciada por él.

### Borrador de respuesta
Para la pregunta sobre si la aplicación recopila o comparte datos fuera del dispositivo, la respuesta prevista es **No**, porque la versión actual procesa los datos localmente y no los transmite automáticamente fuera del dispositivo.

La acción de exportar o compartir un archivo debe seguir describiéndose claramente en la política de privacidad.

No reutilice esta respuesta si se incorpora cualquier SDK o función que envíe datos fuera del dispositivo.

## Datos personales y de salud que la app puede procesar localmente
- imágenes/radiografías;
- nombre o identificador de paciente introducido por el usuario;
- edad;
- sexo;
- puntos anatómicos;
- mediciones cefalométricas;
- calibración;
- nombre del estudio.

Aunque el tratamiento sea local, la política de privacidad debe explicarlo porque se trata de información potencialmente personal o sensible.

## Declaración de aplicaciones de salud

YomCeph ofrece funciones relacionadas con salud bucal y análisis cefalométrico. No debe declararse como una app sin funciones de salud.

La ficha y la aplicación deben mantener este aviso:

> YomCeph no es un dispositivo médico y no diagnostica, trata, cura ni previene ninguna afección médica. Para asesoramiento, diagnóstico o tratamiento médico u odontológico, consulte a un profesional sanitario cualificado.

Si en el futuro la app se comercializa para diagnóstico, decisión clínica, tratamiento o como dispositivo médico, detener la publicación hasta revisar los requisitos regulatorios y de Google Play aplicables.

## Revisión obligatoria antes de cada versión

Volver a evaluar esta guía si se añade cualquiera de los siguientes elementos:
- Firebase Analytics, Crashlytics u otra telemetría;
- publicidad;
- inicio de sesión;
- sincronización en la nube;
- copias de seguridad externas;
- APIs remotas;
- Health Connect;
- almacenamiento o procesamiento en servidores;
- envío automático de informes;
- IA que procese radiografías en un servicio externo.
