# Preparación y publicación

El repositorio se prepara en main sin commit ni remoto automático. Publicar requiere
la URL del repositorio elegido y acceso del usuario. No se ha subido contenido.

```powershell
git status --short
git add .
git diff --cached --stat
git diff --cached
git commit -m "chore: bootstrap Cosmic Hunter AI architecture"
git remote add origin https://github.com/ORGANIZACION/cosmic-hunter-ai.git
git push -u origin main
```

Sustituir ORGANIZACION y confirmar nombre de repo antes de ejecutar. Los ejemplos
de credenciales en .env.example son solo desarrollo local. Revisar staged diff antes
de commit; .gitignore no elimina secretos previamente versionados. Rotar cualquier
clave expuesta, aunque luego se borre del historial. No versionar FITS/modelos; guardar
manifiestos con referencias/checksums y condiciones de acceso.

CI verifica estilo, pruebas, deriva OpenAPI, Compose y construcción API. Protección
de main y revisión por PR se configuran en GitHub al crear el remoto. El esquema SQL
requiere validación con PostgreSQL real; no basta con generar el archivo.
