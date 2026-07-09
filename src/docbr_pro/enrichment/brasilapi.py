"""Async client for BrasilAPI."""

from typing import Any

import httpx

from docbr_pro.core.exceptions import DocbrError

from .cache import CNPJCache


class APIError(DocbrError):
    """Raised when the external API fails or times out."""


async def fetch_cnpj(
    cnpj: str, cache: CNPJCache | None = None, timeout: float = 10.0
) -> dict[str, Any]:
    """
    Fetches CNPJ data from BrasilAPI.

    Args:
        cnpj: The numeric or alphanumeric CNPJ (clean format).
        cache: Optional SQLite cache instance.
        timeout: Request timeout in seconds.

    Returns:
        A dictionary with the CNPJ data.
    """
    if cache:
        cached_data = cache.get(cnpj)
        if cached_data:
            return cached_data

    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)

            if response.status_code == 404:
                # API returns 404 for invalid/unregistered CNPJs
                data = {"error": "CNPJ não encontrado."}
            else:
                response.raise_for_status()
                data = dict(response.json())

            # Only cache successful 200 OK responses to avoid poisoning
            if cache and response.status_code == 200:
                cache.set(cnpj, data)

            return data

    except httpx.TimeoutException as e:
        raise APIError("Tempo de resposta excedido ao consultar a BrasilAPI.") from e
    except httpx.RequestError as e:
        raise APIError(f"Erro de conexão com a BrasilAPI: {e}") from e
    except httpx.HTTPStatusError as e:
        raise APIError(f"Erro HTTP da BrasilAPI: {e.response.status_code}") from e
