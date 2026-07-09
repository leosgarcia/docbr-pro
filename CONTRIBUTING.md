# Guia de Contribuição - docbr-pro

Obrigado por considerar contribuir para o `docbr-pro`! Este projeto segue rígidos padrões de qualidade, tipagem e testes. Abaixo você encontra o passo a passo de como configurar o ambiente e submeter suas alterações.

## Requisitos Prévios

Utilizamos o [**uv**](https://github.com/astral-sh/uv) como nosso gerenciador de pacotes e ambientes virtuais, pois ele é extremamente rápido e moderno.

Certifique-se de ter instalado:
- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Configurando o ambiente de desenvolvimento

1. Faça o fork deste repositório e clone na sua máquina:
   ```bash
   git clone https://github.com/SEU_USUARIO/docbr-pro.git
   cd docbr-pro
   ```

2. Instale as dependências (o `uv` criará automaticamente o ambiente virtual `.venv` para você):
   ```bash
   uv sync
   ```

3. Ative o ambiente virtual:
   - **Windows:** `.venv\Scripts\activate`
   - **Linux/macOS:** `source .venv/bin/activate`

## Rodando Testes e Linters

Para garantir que tudo continua funcionando, o seu código deve passar em todas as nossas verificações rigorosas:

1. **Testes Unitários e Cobertura (Pytest + Hypothesis):**
   Garantimos 100% de cobertura nos validadores do core.
   ```bash
   uv run pytest --cov
   ```

2. **Verificação de Tipagem Estática (Mypy):**
   Trabalhamos com o modo `--strict`.
   ```bash
   uv run mypy .
   ```

3. **Linter e Formatação (Ruff):**
   ```bash
   uv run ruff check .
   ```
   *Dica: Você pode rodar `uv run ruff check --fix .` para corrigir problemas simples automaticamente.*

## Padrão de Commits

Seguimos a especificação do [Conventional Commits](https://www.conventionalcommits.org/). Por favor, estruture as mensagens dos seus commits da seguinte maneira:

- `feat:` Novas funcionalidades (ex: `feat: suporte a cnh`)
- `fix:` Correção de bugs (ex: `fix: corrige timeout na brasilapi`)
- `docs:` Alterações em documentação (ex: `docs: atualiza readme com nova flag`)
- `test:` Adição ou refatoração de testes
- `refactor:` Alterações de código que não mudam a lógica do negócio nem corrigem bugs

## Arquitetura do Projeto

Ao propor mudanças, mantenha a estrita separação de camadas:
- **`core/`**: Regras de negócio puras (sem I/O, sem requisições HTTP, sem banco de dados).
- **`enrichment/`**: Comunicação com APIs externas e cache.
- **`batch/`**: Processamento em massa e DataFrames.
- **`cli/`**: Interface de linha de comando (Typer).

## Submetendo seu Pull Request

1. Crie uma branch com um nome descritivo: `git checkout -b feat/minha-nova-funcionalidade`
2. Realize as alterações mantendo o código formatado e testado.
3. Faça o push para o seu fork: `git push origin feat/minha-nova-funcionalidade`
4. Abra um **Pull Request** no repositório original.

Qualquer dúvida, sinta-se à vontade para abrir uma *Issue* antes de começar o código. Vamos adorar receber o seu PR!
