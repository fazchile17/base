// EJERCICIO: este es el ÚNICO archivo que hay que escribir en vivo.
// Copia aquí, por etapas, el contenido del archivo 04_CODIGO_PARA_TRANSCRIBIR.js.
// Antes de completar este archivo, el Frontend se ve bonito pero NO consulta la API.
// CÓDIGO QUE SE TRANSCRIBE EN CLASE: frontend/static/conexion.js
// Solo el Gateway (puerto 8000) recibe solicitudes del navegador.

// 1. Función genérica: Frontend -> Gateway usando HTTP y JSON.
async function pedir(ruta, metodo = "GET", datos = null) {
    const opciones = { method: metodo, credentials: "include" };
    if (datos !== null) {
      opciones.headers = { "Content-Type": "application/json" };
      opciones.body = JSON.stringify(datos);
    }
    try {
      const respuesta = await fetch(ruta, opciones);
      const contenido = await respuesta.json();
      ui.registrar(metodo, ruta, respuesta.status, contenido);
      return { ok: respuesta.ok, codigo: respuesta.status, datos: contenido };
    } catch (error) {
      ui.mensaje("No se pudo conectar con el Gateway: " + error.message, true);
      return { ok: false, codigo: 0, datos: null };
    }
  }
  
  // 2. Login: enviar credenciales; el Gateway coloca una cookie HttpOnly.
  document.querySelector("#login-form").addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const username = document.querySelector("#username").value;
    const password = document.querySelector("#password").value;
    const r = await pedir("/auth/login", "POST", { username, password });
    ui.mensaje(r.ok ? "Inicio de sesión correcto" : "Credenciales inválidas", !r.ok);
    if (r.ok) await verSesion();
  });
  
  // 3. Identidad y recursos protegidos: GET /auth/me, /api/products, /api/orders.
  async function verSesion() {
    const r = await pedir("/auth/me");
    ui.sesion(r.ok ? r.datos : null);
    if (!r.ok) ui.mensaje("Debes iniciar sesión (HTTP 401)", true);
  }
  
  async function verProductos() {
    const r = await pedir("/api/products");
    if (r.ok) ui.productos(r.datos.products);
    else ui.mensaje(`No se pudo consultar productos (HTTP ${r.codigo})`, true);
  }
  
  async function verOrdenes() {
    const r = await pedir("/api/orders");
    if (r.ok) ui.ordenes(r.datos.orders);
    else ui.mensaje(`No se pudo consultar órdenes (HTTP ${r.codigo})`, true);
  }
  
  // 4. Admin: el Gateway comprueba el rol y el Backend vuelve a comprobarlo.
  async function eliminarProducto(id) {
    const r = await pedir(`/api/products/${id}`, "DELETE");
    ui.mensaje(r.ok ? `Producto ${id} eliminado` : `Operación rechazada: HTTP ${r.codigo}`, !r.ok);
    if (r.ok) await verProductos();
  }
  
  // 5. Logout: revoca el token y elimina la cookie.
  async function cerrarSesion() {
    const r = await pedir("/auth/logout", "POST");
    if (r.ok) {
      ui.sesion(null);
      ui.productos([]);
      ui.ordenes([]);
      ui.mensaje("Sesión cerrada. El token fue revocado.");
    }
  }
  
  // 6. Conectar los botones existentes con las funciones anteriores.
  document.querySelector("#btn-me").addEventListener("click", verSesion);
  document.querySelector("#btn-products").addEventListener("click", verProductos);
  document.querySelector("#btn-orders").addEventListener("click", verOrdenes);
  document.querySelector("#btn-logout").addEventListener("click", cerrarSesion);
  