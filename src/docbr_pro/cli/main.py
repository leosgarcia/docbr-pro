# ruff: noqa: B008, E501
"""CLI entrypoint for docbr-pro."""
import asyncio
from pathlib import Path
from typing import Any

import pandas as pd
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from docbr_pro.batch.processor import process_batch
from docbr_pro.batch.reader import read_file
from docbr_pro.batch.writer import write_results
from docbr_pro.core.cnpj import CNPJ
from docbr_pro.core.cpf import CPF
from docbr_pro.core.exceptions import DocbrError
from docbr_pro.core.generator import generate_cnpj, generate_cpf
from docbr_pro.core.sanitizer import sanitize_cnpj, sanitize_cpf
from docbr_pro.enrichment.brasilapi import fetch_cnpj

app = typer.Typer(
    name="docbr-pro",
    help="Validação, geração e enriquecimento de CPF/CNPJ brasileiros.",
    add_completion=False,
)
console = Console()

@app.command()
def validate(
    document: str = typer.Argument(..., help="O CPF ou CNPJ a ser validado"),
    enrich: bool = typer.Option(False, "--enrich", "-e", help="Consultar BrasilAPI para CNPJs"),
) -> None:
    """Valida e formata um único documento."""
    clean = "".join(c for c in document if c.isalnum())

    try:
        if len(clean) > 11:
            sanitized = sanitize_cnpj(document)
            cnpj_obj = CNPJ(sanitized)
            console.print(f"[green]CNPJ Válido![/green] Formato: [bold]{cnpj_obj.formatted}[/bold]")

            if enrich:
                console.print("[yellow]Buscando dados na BrasilAPI...[/yellow]")

                async def do_fetch() -> dict[str, Any]:
                    return await fetch_cnpj(cnpj_obj.clean)

                try:
                    data = asyncio.run(do_fetch())
                    table = Table(title="Dados da Empresa")
                    table.add_column("Chave", style="cyan")
                    table.add_column("Valor", style="magenta")
                    for k, v in data.items():
                        if k not in ["qsa", "cnaes_secundarios"]:
                            table.add_row(str(k), str(v))
                    console.print(table)
                except Exception as e:
                    console.print(f"[red]Erro na integração:[/red] {e}")

        else:
            sanitized = sanitize_cpf(document)
            cpf_obj = CPF(sanitized)
            console.print(f"[green]CPF Válido![/green] Formato: [bold]{cpf_obj.formatted}[/bold]")
            console.print(f"Região Fiscal Emissora: [cyan]{cpf_obj.fiscal_region}[/cyan]")

    except DocbrError as e:
        console.print(f"[bold red]Documento Inválido:[/bold red] {e}")
        raise typer.Exit(1) from e

@app.command()
def generate(
    tipo: str = typer.Argument(..., help="'cpf' ou 'cnpj'"),
    formatted: bool = typer.Option(True, "--formatted/--raw", help="Formatar saída"),
    region: str | None = typer.Option(None, "--region", "-r", help="Região fiscal (para CPF)"),
    alphanumeric: bool = typer.Option(True, "--alphanumeric/--numeric", help="Padrão alfanumérico"),
) -> None:
    """Gera um CPF ou CNPJ válido."""
    tipo = tipo.lower()
    if tipo == "cpf":
        doc = generate_cpf(region=region, formatted=formatted)
        console.print(f"CPF Gerado: [bold green]{doc}[/bold green]")
    elif tipo == "cnpj":
        doc = generate_cnpj(alphanumeric=alphanumeric, formatted=formatted)
        console.print(f"CNPJ Gerado: [bold green]{doc}[/bold green]")
    else:
        console.print("[red]Erro:[/red] Tipo deve ser 'cpf' ou 'cnpj'.")
        raise typer.Exit(1)

@app.command()
def process(
    filepath: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False, help="Arquivo CSV de entrada"
    ),
    enrich: bool = typer.Option(False, "--enrich", "-e", help="Consultar BrasilAPI"),
    output: Path = typer.Option(".", "--output", "-o", help="Pasta para salvar os resultados"),
) -> None:
    """Processa documentos em massa a partir de um CSV."""
    console.print(f"Lendo [bold]{filepath}[/bold]...")
    try:
        df = read_file(filepath)
    except Exception as e:
        console.print(f"[red]Erro ao ler arquivo:[/red] {e}")
        raise typer.Exit(1) from e

    console.print(f"Processando {len(df)} registros...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Processando e enriquecendo dados...", total=None)

        async def run_batch() -> dict[str, pd.DataFrame]:
            return await process_batch(df, enrich=enrich)

        try:
            results = asyncio.run(run_batch())
        except Exception as e:
            console.print(f"[red]Erro no processamento:[/red] {e}")
            raise typer.Exit(1) from e

    write_results(results, output_dir=output)

    n_valid = len(results.get("valid", []))
    n_invalid = len(results.get("invalid", []))

    console.print("[green]✔ Processamento concluído![/green]")
    console.print(f"- Válidos: [bold green]{n_valid}[/bold green]")
    console.print(f"- Inválidos: [bold red]{n_invalid}[/bold red]")
    console.print(f"Arquivos salvos em: [bold]{output.absolute()}[/bold]")

@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Host para a API"),
    port: int = typer.Option(8000, help="Porta para a API"),
) -> None:
    """Inicia o servidor da API REST do docbr-pro."""
    try:
        import uvicorn
        console.print(f"[green]Iniciando servidor em http://{host}:{port}...[/green]")
        uvicorn.run("docbr_pro.api.main:app", host=host, port=port, reload=False)
    except ImportError:
        console.print("[red]Erro:[/red] uvicorn ou fastapi não instalados.")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
