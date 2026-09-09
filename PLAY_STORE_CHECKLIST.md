# Checklist de publicación en Google Play — YomCeph

Actualizado: 9 de septiembre de 2026.

## Identidad de la app
- [x] Nombre visible: YomCeph.
- [x] Application ID previsto para Google Play: `com.yomceph.app`.
- [ ] Confirmar este Application ID antes de la primera carga en Play Console.
- [ ] Después de la primera carga, no cambiar el Application ID de la app.
- [x] versionCode y versionName definidos en `app/build.gradle`.
- [ ] Incrementar siempre `versionCode` para cada nueva versión que se suba a Google Play.

## Preparación técnica
- [x] compileSdk 36.
- [x] targetSdk 36.
- [x] minSdk 24.
- [x] App Bundle (AAB) preparado como formato de publicación.
- [x] Java 17.
- [x] Lint de release configurado para fallar si encuentra errores.
- [x] Actividades internas no exportadas.
- [x] Sin permisos de cámara, ubicación, contactos ni almacenamiento amplio.
- [x] Sin permiso INTERNET.
- [x] Tráfico HTTP sin cifrar desactivado.
- [x] Copias de seguridad de datos locales desactivadas.
- [x] Aviso educativo/médico visible dentro de la app.
- [x] Política de privacidad accesible desde la app.
- [x] Archivos de claves, APK/AAB y secretos excluidos mediante `.gitignore`.

## Firma y AAB
- [ ] Crear una clave de carga (upload key) y un almacén de claves seguro.
- [ ] Guardar el archivo .jks fuera del repositorio y conservar una copia de seguridad segura.
- [ ] Configurar los secretos de GitHub:
  - `YOMCEPH_UPLOAD_KEYSTORE_BASE64`
  - `YOMCEPH_KEYSTORE_PASSWORD`
  - `YOMCEPH_KEY_ALIAS`
  - `YOMCEPH_KEY_PASSWORD`
- [ ] Ejecutar el workflow **Build Signed Google Play Bundle**.
- [ ] Verificar el checksum SHA-256 generado junto al AAB.
- [ ] Activar Play App Signing al crear la primera versión en Play Console.
- [ ] Probar primero el AAB en prueba interna o uso compartido interno.

## Política de privacidad
Google Play exige una política de privacidad incluso cuando la app no envía datos fuera del dispositivo.

Antes de publicar:
- [ ] Usar una URL activa, pública, sin geobloqueo, no editable por el visitante y que no sea un PDF.
- [x] La política explica radiografías/imágenes, identificador del estudio/paciente, edad, sexo, puntos, calibración y mediciones.
- [x] La política explica que el procesamiento actual es local.
- [x] La política incluye retención y eliminación local.
- [x] La política incluye un mecanismo de contacto.
- [ ] Sustituir la URL de desarrollo de GitHub por una página web estable de privacidad antes del envío final, si Play Console no acepta la URL actual.

## Seguridad de los datos
La versión actual no tiene permiso INTERNET ni SDKs de publicidad/analítica. Los datos de radiografías y estudios se procesan localmente. En el formulario de Seguridad de los datos, Google define “recoger” como transmitir datos fuera del dispositivo; el tratamiento exclusivamente local no se declara como recogida.

La exportación o compartición iniciada expresamente por el usuario debe describirse en la política de privacidad, pero no debe confundirse con una transmisión automática al desarrollador.

Revisar estas respuestas si en el futuro se añaden:
- nube o sincronización;
- cuentas;
- analítica;
- anuncios;
- telemetría/crash reporting que envíe datos;
- APIs externas;
- Health Connect.

## Aplicaciones de salud
YomCeph trabaja con radiografías y mediciones cefalométricas, por lo que debe tratarse como una app con funciones relacionadas con salud.

- [ ] Completar el Formulario de declaración de aplicaciones de salud en Play Console.
- [x] Mantener el aviso claro: YomCeph no es un dispositivo médico y no diagnostica, trata, cura ni previene afecciones.
- [x] Recomendar consultar a un profesional sanitario cualificado.
- [ ] Si en el futuro se presenta como dispositivo médico o se añaden funciones reguladas, revisar los requisitos regulatorios antes de publicar.

## Ficha de Play Console
- [ ] Crear la aplicación YomCeph.
- [ ] Añadir la política de privacidad pública.
- [ ] Completar Seguridad de los datos.
- [ ] Completar Declaración de aplicaciones de salud.
- [ ] Completar clasificación de contenido.
- [ ] Definir el público objetivo; la propuesta actual es estudiantes universitarios/adultos.
- [ ] Completar datos de contacto del desarrollador.
- [ ] Subir icono de Play de 512×512.
- [ ] Preparar gráfico de funciones y capturas reales de la app.
- [ ] Revisar que la descripción no haga afirmaciones diagnósticas ni terapéuticas.

## Pruebas para cuentas personales nuevas
Si la cuenta personal de desarrollador se creó después del 13 de noviembre de 2023, antes de solicitar acceso a producción se requiere una prueba cerrada con al menos 12 testers que hayan participado de forma continua durante al menos 14 días.

## Antes de producción
- [ ] Instalar la versión de prueba en varios tamaños de pantalla.
- [ ] Probar Android 7 (API 24), una versión intermedia y Android 16 (API 36).
- [ ] Probar abrir, rotar, guardar, eliminar, exportar y volver a abrir estudios.
- [ ] Confirmar que una radiografía o estudio eliminado no reaparece.
- [ ] Confirmar que la app funciona sin conexión.
- [ ] Revisar accesibilidad básica, textos cortados y botones fuera de pantalla.
- [ ] Subir primero a prueba interna/cerrada y revisar los informes de Play Console.
