"""Tests for the BrasilAPI client."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from docbr_pro.enrichment.brasilapi import APIError, fetch_cnpj
from docbr_pro.enrichment.cache import CNPJCache


def test_fetch_cnpj_success() -> None:
    """Test successful CNPJ fetch."""

    async def run_test() -> None:
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value={"razao_social": "TESTE LTDA"})
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = await fetch_cnpj("123")
            assert result["razao_social"] == "TESTE LTDA"

    asyncio.run(run_test())


def test_fetch_cnpj_not_found() -> None:
    """Test when CNPJ is not found (404)."""

    async def run_test() -> None:
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = await fetch_cnpj("000")
            assert "error" in result

    asyncio.run(run_test())


def test_fetch_cnpj_timeout() -> None:
    """Test timeout error handling."""

    async def run_test() -> None:
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Timeout")

            with pytest.raises(APIError, match="Tempo de resposta excedido"):
                await fetch_cnpj("123")

    asyncio.run(run_test())


def test_fetch_cnpj_with_cache() -> None:
    """Test that cache prevents network requests."""

    async def run_test() -> None:
        import os
        import tempfile

        fd, path = tempfile.mkstemp()
        os.close(fd)

        try:
            cache = CNPJCache(db_path=path)
            cache.set("123", {"razao_social": "CACHED LTDA"})

            with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
                result = await fetch_cnpj("123", cache=cache)
                assert result["razao_social"] == "CACHED LTDA"
                mock_get.assert_not_called()
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    asyncio.run(run_test())
