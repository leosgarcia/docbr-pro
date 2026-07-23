<div align="center">

# docbr-pro

**A Ãºnica ferramenta que valida, corrige, enriquece e processa CPF/CNPJ em massa â€” do terminal ou como biblioteca.**

[![CI](https://img.shields.io/github/actions/workflow/status/leosgarcia/docbr-pro/ci.yml?branch=main&label=build)](https://github.com/leosgarcia/docbr-pro/actions)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)](#testes-e-qualidade)
[![PyPI](https://img.shields.io/pypi/v/docbr-pro?color=blue)](https://pypi.org/project/docbr-pro/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/leosgarcia/docbr-pro)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/docbr-pro)](https://pypi.org/project/docbr-pro/)

</div>

---

## Por que este projeto existe

A grande maioria das bibliotecas de validaÃ§Ã£o de CPF/CNPJ no ecossistema Python e JavaScript brasileiro faz uma Ãºnica coisa: confere o dÃ­gito verificador matemÃ¡tico e devolve `True` ou `False`. Isso resolve um problema de 2015 â€” nÃ£o o de uma empresa que precisa, hoje, limpar uma planilha de 50 mil clientes com documentos mal formatados, saber quais CNPJs seguem ativos na Receita Federal, ou jÃ¡ validar o novo formato **alfanumÃ©rico** que entrou em produÃ§Ã£o em julho de 2026.

`docbr-pro` nasceu para cobrir essa distÃ¢ncia:

| | Bibliotecas tradicionais (ex. `validate-docbr`) | `docbr-pro` |
|---|---|---|
| ValidaÃ§Ã£o de dÃ­gito verificador | âœ… | âœ… |
| CNPJ alfanumÃ©rico (formato 2026) | â�Œ | âœ… |
| CorreÃ§Ã£o automÃ¡tica de input sujo (fuzzy fixing) | â�Œ | âœ… |
| DetecÃ§Ã£o de regiÃ£o fiscal do CPF | â�Œ | âœ… |
| Enriquecimento de dados via BrasilAPI (razÃ£o social, situaÃ§Ã£o cadastral, CNAE) | â�Œ | âœ… |
| Processamento em massa de CSV/XLSX com relatÃ³rio de erros | â�Œ | âœ… |
| Interface de terminal rica (tabelas, progresso, cores semÃ¢nticas) | â�Œ | âœ… |
| Uso como biblioteca **e** como CLI | parcial | âœ… |

## Funcionalidades

- âœ… **ValidaÃ§Ã£o** â€” CPF e CNPJ, incluindo o novo formato alfanumÃ©rico (mÃ³dulo 11 com conversÃ£o ASCII).
- âœ… **GeraÃ§Ã£o** â€” documentos vÃ¡lidos para testes, com CPF contextual por regiÃ£o fiscal e CNPJ no formato numÃ©rico ou alfanumÃ©rico.
- âœ… **Fuzzy fixing** â€” reconstitui zeros Ã  esquerda perdidos em exportaÃ§Ãµes de Excel e normaliza ruÃ­do comum de input humano.
- âœ… **Enriquecimento (OSINT)** â€” consulta assÃ­ncrona Ã  BrasilAPI para razÃ£o social, situaÃ§Ã£o cadastral e CNAE de CNPJs vÃ¡lidos, com cache local em SQLite.
- âœ… **Processamento em massa** â€” pipeline completo sobre CSV/XLSX: sanitiza, valida, enriquece e exporta relatÃ³rios separados de vÃ¡lidos e invÃ¡lidos.
- âœ… **CLI rica** â€” construÃ­da com `Typer` e `Rich`: tabelas, barras de progresso e saÃ­da colorida por padrÃ£o.

## InstalaÃ§Ã£o

Como biblioteca, em qualquer projeto Python 3.11+:

```bash
pip install docbr-pro
# ou, com uv:
uv add docbr-pro
```

Como ferramenta de linha de comando isolada:

```bash
pipx install docbr-pro
```

## Quickstart

### Como biblioteca

```python
from docbr_pro.core.cpf import validate_cpf, get_fiscal_region
from docbr_pro.core.cnpj import validate_cnpj

validate_cpf("529.982.247-25")        # True
get_fiscal_region("529.982.247-25")   # "SP"
validate_cnpj("06.990.590/0001-23")   # True â€” suporta formato numÃ©rico e alfanumÃ©rico
```

### Como CLI

```bash
docbr validate "06.990.590/0001-23" --enrich
```

![ValidaÃ§Ã£o e Enriquecimento](docs/assets/demo.png)

```bash
docbr generate cpf --region 8
docbr generate cnpj --alphanumeric
```

![Gerador de Documentos](docs/assets/gerador.png)

```bash
docbr process base_clientes.csv --enrich
```

![Processamento em Lote](docs/assets/batch.png)

## ReferÃªncia de CLI

| Comando | DescriÃ§Ã£o | Flags principais |
|---|---|---|
| `docbr validate <documento>` | Valida um CPF ou CNPJ pontual | `--enrich` (consulta BrasilAPI para CNPJ) |
| `docbr generate cpf` | Gera um CPF vÃ¡lido | `--region <cÃ³digo>` (regiÃ£o fiscal de emissÃ£o) |
| `docbr generate cnpj` | Gera um CNPJ vÃ¡lido | `--alphanumeric` (formato 2026) |
| `docbr process <arquivo.csv\|.xlsx>` | Executa o pipeline completo em massa | `--enrich`, `--column <nome>` |

Execute `docbr --help` ou `docbr <comando> --help` para a lista completa de opÃ§Ãµes.

## Arquitetura

O projeto Ã© organizado em camadas com regra de dependÃªncia estrita: `core` Ã© domÃ­nio puro (sem I/O, sem rede) e nÃ£o depende de nenhuma outra camada â€” isso Ã© o que permite reaproveitar toda a regra de negÃ³cio numa futura API HTTP sem reescrever nada.

```mermaid
graph TD
    CLI["cli â€” Typer + Rich"] --> CORE["core â€” validaÃ§Ã£o, geraÃ§Ã£o, sanitizaÃ§Ã£o"]
    CLI --> BATCH["batch â€” pipeline CSV/XLSX"]
    BATCH --> CORE
    BATCH --> ENRICH["enrichment â€” BrasilAPI + cache SQLite"]
    ENRICH --> CORE
    API["api (planejado) â€” FastAPI"] -.-> CORE
    API -.-> ENRICH
```

## Testes e qualidade

- **Tipagem estÃ¡tica:** `mypy --strict` sem ressalvas em toda a base.
- **Lint e formataÃ§Ã£o:** `ruff`.
- **Cobertura:** ~90% nos pipelines assÃ­ncronos e 100% nos validadores do `core`, incluindo testes baseados em propriedades com `hypothesis` (round-trip: todo documento gerado pela ferramenta Ã© validado como vÃ¡lido pela prÃ³pria ferramenta).
- **Gerenciamento de dependÃªncias:** `uv`.

```bash
uv run pytest --cov
uv run mypy .
uv run ruff check .
```

## Roadmap

- [x] Validação e geração de CPF/CNPJ, incluindo formato alfanumérico
- [x] Fuzzy fixing e sanitização de input
- [x] Enriquecimento via BrasilAPI com cache SQLite
- [x] Processamento em massa (CSV/XLSX) via CLI
- [ ] **API REST paga (em breve)** — mesma camada `core` exposta via FastAPI, com autenticação, rate limiting e planos de uso
- [ ] SDKs oficiais em outras linguagens consumindo a futura API
- [ ] Suporte a XLSX com múltiplas planilhas no mesmo arquivo

## ⚡ Como API REST (Novo!)

A partir da versão 0.1.0, o `docbr-pro` acompanha um servidor nativo escrito em **FastAPI**.
Você pode iniciar o servidor utilizando o comando CLI:

```bash
docbr serve --port 8000
```

Isso disponibilizará os seguintes endpoints de alta performance:
- `GET /validate/{document}`: Valida qualquer CPF ou CNPJ.
- `GET /generate/cpf`: Gera um CPF válido.
- `GET /generate/cnpj`: Gera um CNPJ válido.

A documentação interativa (Swagger UI) ficará disponível automaticamente em `http://127.0.0.1:8000/docs`.

## Como contribuir

Contribuições são bem-vindas. Veja [`CONTRIBUTING.md`](CONTRIBUTING.md) para o fluxo de desenvolvimento, padrão de commits ([Conventional Commits](https://www.conventionalcommits.org/)) e como rodar a suíte de testes localmente.

## Aviso legal

`docbr-pro` valida **formato e dígitos verificadores** de CPF e CNPJ segundo os algoritmos públicos definidos pela Receita Federal do Brasil (incluindo a Instrução Normativa RFB nº 2.229/2024 para o formato alfanumérico). O enriquecimento de CNPJ consulta exclusivamente a [BrasilAPI](https://brasilapi.com.br/), fonte pública que agrega dados oficiais e abertos da Receita Federal — nenhum dado pessoal sensível é armazenado, revendido ou exposto pela ferramenta. Não existe, nem é objetivo deste projeto, qualquer forma de consulta a dados pessoais de CPF além do cálculo público da região fiscal de emissão.

## Licença

Distribuído sob a licença MIT. Veja [`LICENSE`](LICENSE) para o texto completo.

---

<p align="center">
  <a href="https://buymeacoffee.com/leosgarcia" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >
  </a>
</p>
