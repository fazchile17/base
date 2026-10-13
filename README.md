# NODO / LAB — Conectar Frontend + Backend con Auth Service

## Abrir y ejecutar

Esta carpeta está **completa salvo la conexión de JavaScript**. El diseño, los botones, el Backend, Auth Service, API Gateway y Vault ya están programados.

1. Instala y abre **Docker Desktop** (necesita Docker Compose y conexión para obtener las imágenes la primera vez).
2. Abre una terminal **dentro de esta carpeta**.
3. Ejecuta `docker compose up --build -d`.
4. Abre <http://localhost:8000>. El Frontend aparecerá, pero aún no consultará la API..
6. Refresca el navegador con `Ctrl+F5` cada vez que escribas un bloque nuevo. Usa **F12 → Network → Fetch/XHR**.

### Credenciales de demostración

- `ana / 1234` → rol `user`
- `ernesto / admin123` → roles `user`, `admin`

### Rutas ya programadas

- Login: `POST /auth/login` (Gateway); Auth Service internamente procesa `POST /login`.
- Identidad: `GET /auth/me`.
- Productos: `GET /api/products`.
- Órdenes: `GET /api/orders`.
- Borrar producto: `DELETE /api/products/{id}` (solo admin).
- Logout: `POST /auth/logout`.

### Comprobaciones

- Ana puede iniciar sesión y consultar productos (`200`), pero no eliminar (`403`).
- Ernesto puede eliminar un producto existente (`200`).
- Sin sesión, los recursos devuelven `401`.
- Acceso directo a `http://localhost:9000/products` sin secreto devuelve `403`.

Detener: `docker compose down`. Para restaurar productos, `docker compose restart backend`.

**Uso didáctico solamente:** Vault en modo DEV; datos y sesiones en memoria; secretos de demostración; HTTP local sin TLS. No usar en producción.
