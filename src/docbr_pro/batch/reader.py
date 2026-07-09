"""CSV/XLSX reader module for docbr-pro."""

from pathlib import Path

import pandas as pd


def read_file(filepath: str | Path, document_col: str | None = None) -> pd.DataFrame:
    """
    Reads a CSV file and ensures the document column exists.
    If document_col is not provided, it tries to guess based on common names.

    Args:
        filepath: Path to the CSV file.
        document_col: Optional name of the column containing the documents.

    Returns:
        A pandas DataFrame with the target column renamed to '_raw_document'.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path, dtype=str)
    else:
        raise ValueError("Formato não suportado nativamente. Por favor, forneça um arquivo .csv")

    # Guess column if not provided
    if not document_col:
        common_names = ["cpf", "cnpj", "documento", "doc", "cpf_cnpj", "documentos"]
        for col in df.columns:
            if str(col).lower().strip() in common_names:
                document_col = str(col)
                break

    if not document_col or document_col not in df.columns:
        raise ValueError(
            "Não foi possível encontrar a coluna de documentos automaticamente. "
            "Especifique-a manualmente."
        )

    # Fill NaN with empty string
    df[document_col] = df[document_col].fillna("")

    # Rename to a standard internal name
    df = df.rename(columns={document_col: "_raw_document"})

    return df
