"""Backend de negocio: confía solo en solicitudes verificadas desde Gateway."""
import hmac

from fastapi import FastAPI, Header, HTTPException

from vault_client import read_gateway_secrets

app = FastAPI(title="Backend - laboratorio")
PRODUCTS = [
    {"id": 1, "name": "Teclado", "price": 15000},
    {"id": 2, "name": "Mouse", "price": 9000},
    {"id": 3, "name": "Monitor", "price": 89000},
]
ORDERS = [
    {"id": 101, "product_id": 1, "quantity": 1},
    {"id": 102, "product_id": 3, "quantity": 2},
]


async def verify_gateway(
    gateway_secret: str | None,
    user_id: str | None,
):
    expected = (await read_gateway_secrets())["backend_shared_secret"]
    if not gateway_secret or not hmac.compare_digest(gateway_secret, expected) or not user_id:
        raise HTTPException(status_code=403, detail="Acceso directo prohibido")


@app.get("/health")
def health():
    return {"status": "ok", "service": "backend"}


@app.get("/products")
async def products(
    x_gateway_secret: str | None = Header(default=None),
    x_authenticated_user: str | None = Header(default=None),
):
    await verify_gateway(x_gateway_secret, x_authenticated_user)
    return {"products": PRODUCTS}


@app.get("/orders")
async def orders(
    x_gateway_secret: str | None = Header(default=None),
    x_authenticated_user: str | None = Header(default=None),
):
    await verify_gateway(x_gateway_secret, x_authenticated_user)
    return {"orders": ORDERS}


@app.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    x_gateway_secret: str | None = Header(default=None),
    x_authenticated_user: str | None = Header(default=None),
    x_authenticated_roles: str | None = Header(default=None),
):
    await verify_gateway(x_gateway_secret, x_authenticated_user)
    roles = (x_authenticated_roles or "").split(",")
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Se necesita el rol admin")
    for index, product in enumerate(PRODUCTS):
        if product["id"] == product_id:
            deleted = PRODUCTS.pop(index)
            return {"deleted": deleted, "by": x_authenticated_user}
    raise HTTPException(status_code=404, detail="Producto inexistente")
