"""Auth Service: login, sesiones opacas, introspección y revocación."""
import hmac
import secrets
import time

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from vault_client import read_gateway_secrets

app = FastAPI(title="Auth Service - laboratorio")
TTL_SECONDS = 15 * 60
ph = PasswordHasher()

# Credenciales EXCLUSIVAMENTE de ejemplo: simulan usuarios en memoria.
# Se generan y comparan hashes Argon2, no passwords en la estructura USERS.
USERS = {
    "ana": {"user_id": "USR-001", "password_hash": ph.hash("1234"), "roles": ["user"]},
    "ernesto": {"user_id": "USR-003", "password_hash": ph.hash("admin123"), "roles": ["user", "admin"]},
}
SESSIONS: dict[str, dict] = {}


class Credentials(BaseModel):
    username: str
    password: str


class TokenInput(BaseModel):
    token: str


async def verify_gateway_secret(candidate: str | None):
    vault = await read_gateway_secrets()
    expected = vault["auth_introspection_secret"]
    if not candidate or not hmac.compare_digest(candidate, expected):
        raise HTTPException(status_code=403, detail="Servicio no autorizado")


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}


@app.post("/login")
def login(data: Credentials):
    user = USERS.get(data.username)
    try:
        valid = user is not None and ph.verify(user["password_hash"], data.password)
    except (VerifyMismatchError, VerificationError):
        valid = False
    if not valid:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = secrets.token_urlsafe(32)  # Token opaco, NO JWT
    SESSIONS[token] = {
        "user_id": user["user_id"],
        "username": data.username,
        "roles": user["roles"],
        "expires_at": time.monotonic() + TTL_SECONDS,
    }
    return {"access_token": token, "token_type": "bearer", "expires_in": TTL_SECONDS}


@app.post("/introspect")
async def introspect(data: TokenInput, x_introspection_secret: str | None = Header(default=None)):
    await verify_gateway_secret(x_introspection_secret)
    session = SESSIONS.get(data.token)
    if session is None:
        return {"active": False}
    if time.monotonic() >= session["expires_at"]:
        SESSIONS.pop(data.token, None)
        return {"active": False}
    return {
        "active": True,
        "user_id": session["user_id"],
        "username": session["username"],
        "roles": session["roles"],
    }


@app.post("/logout")
async def logout(data: TokenInput, x_introspection_secret: str | None = Header(default=None)):
    await verify_gateway_secret(x_introspection_secret)
    SESSIONS.pop(data.token, None)
    return {"message": "Sesión revocada"}
