"""Demostración: acceso a secretos en Vault DEV. NO usar token raíz en producción."""
import os

import httpx
from fastapi import HTTPException


async def read_gateway_secrets() -> dict:
    url = os.getenv("VAULT_ADDR", "http://localhost:8200").rstrip("/")
    token = os.getenv("VAULT_TOKEN", "dev-only-token")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            result = await client.get(
                f"{url}/v1/secret/data/gateway",
                headers={"X-Vault-Token": token},
            )
        result.raise_for_status()
        return result.json()["data"]["data"]
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=503, detail="Vault no disponible") from exc
