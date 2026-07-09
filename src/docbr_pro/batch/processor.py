"""Batch processor module for docbr-pro."""

import asyncio
from typing import Any

import pandas as pd

from docbr_pro.core.cnpj import CNPJ
from docbr_pro.core.cpf import CPF
from docbr_pro.core.exceptions import DocbrError
from docbr_pro.core.sanitizer import sanitize_cnpj, sanitize_cpf
from docbr_pro.enrichment.brasilapi import fetch_cnpj
from docbr_pro.enrichment.cache import CNPJCache


async def process_batch(
    df: pd.DataFrame,
    enrich: bool = False,
    cache_path: str = "docbr_cache.sqlite",
    concurrency_limit: int = 10,
) -> dict[str, pd.DataFrame]:
    """
    Processes a dataframe containing a '_raw_document' column.

    Returns a dictionary with 'valid' and 'invalid' dataframes.
    """
    valids = []
    invalids = []

    cache = CNPJCache(cache_path) if enrich else None
    semaphore = asyncio.Semaphore(concurrency_limit)

    async def process_row(row_series: pd.Series) -> tuple[bool, dict[str, Any]]:
        row = dict(row_series)
        raw_doc = str(row.get("_raw_document", "")).strip()

        if not raw_doc:
            row["erro"] = "Documento em branco"
            return False, row

        # Clean punctuation to estimate size
        stripped = "".join(c for c in raw_doc if c.isalnum())

        # If it looks like a CNPJ (> 11 chars or explicitly requested?)
        # We try CNPJ first if it's long enough
        if len(stripped) > 11:
            try:
                sanitized_cnpj = sanitize_cnpj(raw_doc)
                cnpj_obj = CNPJ(sanitized_cnpj)
                row["documento_limpo"] = cnpj_obj.clean
                row["documento_formatado"] = cnpj_obj.formatted
                row["tipo"] = "CNPJ"

                if enrich:
                    async with semaphore:
                        data = await fetch_cnpj(cnpj_obj.clean, cache=cache)
                        row.update(data)

                return True, row
            except DocbrError as e:
                # Maybe it was a very broken CPF? Fallthrough.
                cnpj_err = str(e)
        else:
            cnpj_err = None

        # Try CPF
        try:
            sanitized_cpf = sanitize_cpf(raw_doc)
            cpf_obj = CPF(sanitized_cpf)
            row["documento_limpo"] = cpf_obj.clean
            row["documento_formatado"] = cpf_obj.formatted
            row["tipo"] = "CPF"
            row["regiao_fiscal"] = cpf_obj.fiscal_region
            return True, row
        except DocbrError as e:
            # If it failed both, report the most likely error based on length
            if cnpj_err and len(stripped) > 11:
                row["erro"] = cnpj_err
            else:
                row["erro"] = str(e)
            return False, row

    # Process concurrently
    # iterrows() returns (index, Series), so we just pass the Series
    tasks = [process_row(row) for _, row in df.iterrows()]
    results = await asyncio.gather(*tasks)

    for is_valid, row_data in results:
        # Remove internal column before returning
        if "_raw_document" in row_data:
            del row_data["_raw_document"]

        if is_valid:
            valids.append(row_data)
        else:
            invalids.append(row_data)

    return {
        "valid": pd.DataFrame(valids) if valids else pd.DataFrame(),
        "invalid": pd.DataFrame(invalids) if invalids else pd.DataFrame(),
    }
