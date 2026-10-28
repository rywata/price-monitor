# Price Monitor

![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Commits](https://img.shields.io/github/commit-activity/m/rywata/price-monitor)

Monitor de preços resiliente para e-commerce, com coleta via APIs
oficiais e endpoints públicos, retry inteligente, rate limiting e
exportação estruturada.

> Projeto em desenvolvimento ativo — construído do zero para aprender
> e aplicar boas práticas de engenharia de software em Python.

## ✨ Objetivo

Automatizar a coleta de preços de concorrentes para pequenos e-commerces,
transformando dados brutos em inteligência acionável.

## 🏗️ Arquitetura (evolutiva)

- **Fase 1 (atual):** scraper resiliente com export CSV
- **Fase 2:** pipeline ETL + banco de dados + histórico
- **Fase 3:** API + automação de alertas (e-mail/Telegram)
- **Fase 4:** dashboard + deploy

## 🧰 Stack

- **Linguagem:** Python 3.11+
- **HTTP:** `httpx` (async, HTTP/2)
- **Validação:** `pydantic` v2
- **Retry:** `tenacity`
- **Logs:** `loguru`
- **CLI:** `typer` + `rich`
- **Dados:** `pandas`
- **Testes:** `pytest` + `respx`
- **Qualidade:** `ruff` + `mypy` + `pre-commit`

## 📋 Status

- [x] Estrutura inicial do projeto
- [x] Ambiente e dependências
- [x] Configuração centralizada (`pydantic-settings`)
- [x] Modelos de dados (`pydantic`)
- [x] Cliente HTTP resiliente (retry + rate limit)
- [x] CLI com comando `coletar`
- [x] Qualidade de código (ruff, mypy, pre-commit)
- [x] Scraper Shopify (com fallback de catálogo)   ← novo
- [ ] Scraper Mercado Livre (API)
- [ ] Testes automatizados
- [ ] CI/CD (GitHub Actions)


## 📊 Exemplo de saída

```bash
$ price-monitor --arquivo data/produtos.csv

         Precos Coletados
┏━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Site    ┃ Produto     ┃    Preco ┃ Disponivel ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ shopify │ qualquer-id │ R$ 39.00 │     ❌     │
└─────────┴─────────────┴──────────┴────────────┘

## 🚀 Como rodar

```bash
# 1. Clone
git clone https://github.com/rywata/price-monitor.git
cd price-monitor

# 2. Ambiente virtual
python -m venv .venv
source .venv/bin/activate          # Linux/Mac
# .venv\Scripts\Activate.ps1       # Windows PowerShell

# 3. Instale em modo editável
pip install -e ".[dev]"

# 4. Rode a CLI
price-monitor --help
price-monitor --arquivo data/produtos.csv
