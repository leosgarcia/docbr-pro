"""CSV exporter module for docbr-pro."""

from pathlib import Path

import pandas as pd


def write_results(results: dict[str, pd.DataFrame], output_dir: str | Path = ".") -> None:
    """
    Writes valid and invalid dataframes to CSV files.

    Args:
        results: Dictionary with 'valid' and 'invalid' dataframes.
        output_dir: Directory to write the CSV files.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    df_valid = results.get("valid")
    if df_valid is not None and not df_valid.empty:
        df_valid.to_csv(out_path / "validos.csv", index=False)

    df_invalid = results.get("invalid")
    if df_invalid is not None and not df_invalid.empty:
        df_invalid.to_csv(out_path / "invalidos.csv", index=False)
