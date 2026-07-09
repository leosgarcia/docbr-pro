"""Tests for batch processing module."""

import asyncio
import os
import tempfile

import pandas as pd

from docbr_pro.batch.processor import process_batch
from docbr_pro.batch.reader import read_file
from docbr_pro.batch.writer import write_results
from docbr_pro.core.generator import generate_cnpj, generate_cpf


def test_read_file() -> None:
    """Test reading a CSV and guessing the document column."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)

    with open(path, "w", encoding="utf-8") as f:
        f.write("nome,documento,idade\nLeo,12345678909,30\n")

    try:
        df = read_file(path)
        assert "_raw_document" in df.columns
        assert df.iloc[0]["_raw_document"] == "12345678909"
    finally:
        os.unlink(path)


def test_process_batch() -> None:
    """Test processing a batch of valid and invalid documents."""

    async def run_test() -> None:
        valid_cpf = generate_cpf()
        valid_cnpj = generate_cnpj()

        df = pd.DataFrame(
            [
                {"_raw_document": valid_cpf, "nome": "Pessoa"},
                {"_raw_document": valid_cnpj, "nome": "Empresa"},
                {"_raw_document": "123", "nome": "Invalido"},
            ]
        )

        res = await process_batch(df, enrich=False)
        assert len(res["valid"]) == 2
        assert len(res["invalid"]) == 1
        assert "documento_formatado" in res["valid"].columns
        assert "erro" in res["invalid"].columns

    asyncio.run(run_test())


def test_write_results() -> None:
    """Test writing the results back to CSV."""
    import tempfile

    with tempfile.TemporaryDirectory() as tempdir:
        df_valid = pd.DataFrame([{"doc": "111"}])
        df_invalid = pd.DataFrame([{"doc": "222"}])

        write_results({"valid": df_valid, "invalid": df_invalid}, output_dir=tempdir)

        assert os.path.exists(os.path.join(tempdir, "validos.csv"))
        assert os.path.exists(os.path.join(tempdir, "invalidos.csv"))
