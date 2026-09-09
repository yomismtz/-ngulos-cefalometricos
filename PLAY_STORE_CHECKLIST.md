# Checklist de publicación en Google Play — YomCeph

Actualizado: 9 de septiembre de 2026.

## Preparación técnica
- [x] Nombre: YomCeph.
- [x] App Bundle preparado como formato de publicación.
- [x] compileSdk 36.
- [x] targetSdk 36.
- [x] minSdk 24.
- [x] Actividades internas no exportadas.
- [x] Sin permisos de cámara, ubicación, contactos ni almacenamiento amplio.
- [x] Sin permiso INTERNET.
- [x] Copias de seguridad de datos locales desactivadas.
- [x] Política de privacidad incluida.
- [x] Aviso educativo/médico visible dentro de la app.
- [ ] Crear una clave de subida segura y guardarla fuera del repositorio.
- [ ] Configurar secretos de GitHub para generar el AAB firmado.
- [ ] Probar el AAB mediante Internal App Sharing o prueba interna.

## Secretos requeridos por el workflow de Play
- YOMCEPH_UPLOAD_KEYSTORE_BASE64
- YOMCEPH_KEYSTORE_PASSWORD
- YOMCEPH_KEY_ALIAS
- YOMCEPH_KEY_PASSWORD

Nunca suba el archivo .jks ni sus contraseñas al repositorio.

## Play Console
- [ ] Crear la aplicación YomCeph.
- [ ] Añadir la política de privacidad pública.
- [ ] Completar Seguridad de los datos.
- [ ] Completar Declaración de aplicaciones de salud.
- [ ] Añadir el aviso legal de que no es un dispositivo médico en la descripción.
- [ ] Recordar al usuario consultar a un profesional sanitario.
- [ ] Subir icono de 512×512, gráfico de funciones y capturas.
- [ ] Completar clasificación de contenido y público objetivo.
- [ ] Completar datos de contacto del desarrollador.

## Seguridad de los datos
La versión actual de YomCeph procesa radiografías, nombre/identificador, edad, sexo y resultados únicamente en el dispositivo y no los transmite fuera del dispositivo. De acuerdo con la definición de Google Play, el tratamiento exclusivamente local no se declara como “recogida” de datos. Revise esta respuesta si en el futuro se añaden nube, analítica, anuncios o cuentas.

## Aplicaciones de salud
No marque “mi aplicación no ofrece funciones de salud”. YomCeph trabaja con salud bucal/radiografías y cálculos cefalométricos. Declare honestamente la funcionalidad educativa/cefálica que corresponda en Play Console. Si Google la clasifica dentro de funciones médicas, mantenga el aviso de que no es un dispositivo médico y no diagnostica, trata, cura ni previene afecciones.

## Cuentas personales nuevas
Si la cuenta personal de desarrollador se creó después del 13 de noviembre de 2023, Google puede exigir una prueba cerrada con al menos 12 testers durante 14 días continuos antes de conceder acceso a producción.
