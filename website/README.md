# Sitio web de YomCeph

Contenido estático de la web pública de YomCeph.

- `index.html`: sitio principal en español.
- `en.html`: versión inglesa.
- `science.html`: estado de validación y referencias científicas.
- `privacy.html`: política de privacidad.
- `styles.css` y `v120.css`: estilos responsive.

El workflow `.github/workflows/deploy-pages.yml` está preparado para GitHub Pages con GitHub Actions. El repositorio necesita tener **GitHub Pages habilitado una vez en la configuración del repositorio**. El token de Actions no puede habilitar Pages por sí mismo si el repositorio todavía no tiene el servicio activado.
