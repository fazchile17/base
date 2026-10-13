"""Gateway: único punto de entrada del navegador; sesión, roles y routing."""
import os

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from vault_client import read_gateway_secrets

app = FastAPI(title="API Gateway - laboratorio")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
AUTH_URL = os.getenv("AUTH_URL", "http://localhost:8100").rstrip("/")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:9000").rstrip("/")
COOKIE_NAME = "session_token"


class Credentials(BaseModel):
    username: str
    password: str


async def call_auth(endpoint: str, body: dict, headers: dict | None = None) -> httpx.Response:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            return await client.post(f"{AUTH_URL}{endpoint}", json=body, headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Auth Service no disponible") from exc


async def get_identity(request: Request) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Falta la sesión")
    secrets = await read_gateway_secrets()
    result = await call_auth(
        "/introspect",
        {"token": token},
        {"X-Introspection-Secret": secrets["auth_introspection_secret"]},
    )
    if result.status_code != 200:
        raise HTTPException(status_code=503, detail="No se pudo validar la sesión")
    identity = result.json()
    if not identity.get("active"):
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    return identity


async def route_backend(request: Request, path: str, method: str = "GET", admin: bool = False):
    identity = await get_identity(request)
    if admin and "admin" not in identity["roles"]:
        raise HTTPException(status_code=403, detail="El rol admin es obligatorio")
    secrets = await read_gateway_secrets()
    # Los encabezados de identidad se generan AQUÍ. No se aceptan desde el cliente.
    headers = {
        "X-Gateway-Secret": secrets["backend_shared_secret"],
        "X-Authenticated-User": identity["user_id"],
        "X-Authenticated-Username": identity["username"],
        "X-Authenticated-Roles": ",".join(identity["roles"]),
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            result = await client.request(method, f"{BACKEND_URL}{path}", headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Backend no disponible") from exc
    return JSONResponse(content=result.json(), status_code=result.status_code)


@app.get("/")
def frontend():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


@app.post("/auth/login")
async def login(data: Credentials):
    result = await call_auth("/login", data.model_dump())
    if result.status_code != 200:
        raise HTTPException(status_code=result.status_code, detail="Credenciales inválidas")
    payload = result.json()
    response = JSONResponse(content={"message": "Sesión iniciada"})
    response.set_cookie(
        key=COOKIE_NAME,
        value=payload["access_token"],
        httponly=True,
        secure=False,  # SOLO laboratorio HTTP; en producción HTTPS + secure=True.
        samesite="lax",
        max_age=payload["expires_in"],
        path="/",
    )
    return response


@app.get("/auth/me")
async def me(request: Request):
    identity = await get_identity(request)
    return {k: identity[k] for k in ("user_id", "username", "roles")}


@app.post("/auth/logout")
async def logout(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        secrets = await read_gateway_secrets()
        result = await call_auth(
            "/logout",
            {"token": token},
            {"X-Introspection-Secret": secrets["auth_introspection_secret"]},
        )
        if result.status_code != 200:
            raise HTTPException(status_code=503, detail="No se pudo revocar la sesión")
    response = JSONResponse(content={"message": "Sesión cerrada"})
    response.delete_cookie(COOKIE_NAME, path="/", samesite="lax")
    return response


@app.get("/api/products")
async def products(request: Request):
    return await route_backend(request, "/products")


@app.get("/api/orders")
async def orders(request: Request):
    return await route_backend(request, "/orders")


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int, request: Request):
    return await route_backend(request, f"/products/{product_id}", "DELETE", admin=True)
