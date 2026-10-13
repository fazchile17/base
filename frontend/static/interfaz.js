// INTERFAZ YA CONSTRUIDA. Los estudiantes NO transcriben este archivo.
// Su objetivo en clase es conectar la interfaz con fetch() en conexion.js.

const ui = {
  mensaje(texto, error = false) {
    const el = document.querySelector("#mensaje");
    el.textContent = texto;
    el.className = "message " + (error ? "error" : "ok");
  },

  registrar(metodo, ruta, codigo, datos) {
    document.querySelector("#resultado").textContent =
      `${metodo} ${ruta}\nHTTP ${codigo}\n\n${JSON.stringify(datos, null, 2)}`;
  },

  sesion(perfil) {
    const activo = Boolean(perfil);
    const badge = document.querySelector("#sesion-badge");
    badge.className = "badge" + (activo ? " active" : "");
    badge.innerHTML = '<span class="dot"></span>' + (activo ? " AUTENTICADO" : " SIN SESIÓN");
    document.querySelector("#perfil-nombre").textContent = activo ? perfil.username : "Visitante";
    document.querySelector("#perfil-detalle").textContent = activo
      ? `ID: ${perfil.user_id} · Roles: ${perfil.roles.join(", ")}` : "Aún no autenticado";
    document.querySelector("#perfil-estado").textContent = activo ? "Activa" : "Desconectada";
    document.querySelector("#avatar").textContent = activo ? perfil.username[0].toUpperCase() : "?";
  },

  productos(productos) {
    const contenedor = document.querySelector("#productos");
    contenedor.replaceChildren();
    document.querySelector("#contador-productos").textContent = `${productos.length} productos`;
    if (productos.length === 0) {
      const aviso = document.createElement("p");
      aviso.textContent = "No quedan productos en el inventario.";
      contenedor.append(aviso);
      return;
    }
    productos.forEach((producto) => {
      const fila = document.createElement("div");
      fila.className = "product-row";
      const icono = document.createElement("span");
      icono.className = "product-icon";
      icono.textContent = "▣";
      const detalle = document.createElement("div");
      detalle.className = "product-desc";
      const nombre = document.createElement("strong");
      nombre.textContent = producto.name;
      const id = document.createElement("small");
      id.textContent = `Producto #${producto.id}`;
      detalle.append(nombre, id);
      const precio = document.createElement("span");
      precio.className = "product-price";
      precio.textContent = new Intl.NumberFormat("es-CL", {
        style: "currency", currency: "CLP", maximumFractionDigits: 0
      }).format(producto.price);
      const borrar = document.createElement("button");
      borrar.className = "btn-delete";
      borrar.type = "button";
      borrar.textContent = "Eliminar";
      borrar.addEventListener("click", () => window.eliminarProducto(producto.id));
      fila.append(icono, detalle, precio, borrar);
      contenedor.append(fila);
    });
  },

  ordenes(ordenes) {
    const contenedor = document.querySelector("#ordenes");
    contenedor.replaceChildren();
    if (!ordenes.length) {
      contenedor.textContent = "No hay órdenes disponibles.";
      return;
    }
    ordenes.forEach((orden) => {
      const fila = document.createElement("div");
      fila.className = "order-row";
      const nombre = document.createElement("strong");
      nombre.textContent = `Orden #${orden.id}`;
      const detalle = document.createElement("span");
      detalle.textContent = `Producto ${orden.product_id} · Cantidad ${orden.quantity}`;
      fila.append(nombre, detalle);
      contenedor.append(fila);
    });
  }
};

// Rellenar credenciales de prueba NO hace login; solo modifica los inputs.
document.querySelectorAll(".demo-user").forEach((boton) => {
  boton.addEventListener("click", () => {
    document.querySelector("#username").value = boton.dataset.username;
    document.querySelector("#password").value = boton.dataset.password;
  });
});
