```markdown
# Decisões de arquitetura

Registro das decisões técnicas relevantes do projeto.

---

## CLI com comando único

**Data:** 2026-10-18

**Contexto:** o projeto tem apenas 1 comando (`coletar`).

**Decisão:** usar o modo "single command" do Typer (sem subcomando).

**Uso atual:** `price-monitor --arquivo data/produtos.csv`

**Consequência:** quando o projeto ganhar um segundo comando (ex: `status`,
`configurar`), o Typer muda automaticamente para modo grupo. Nesse momento,
o uso passará a ser `price-monitor coletar --arquivo data/produtos.csv`.

**Alternativa descartada:** forçar modo grupo agora adicionando um comando
dummy. Descartada por YAGNI — complexidade desnecessária para resolver
problema hipotético.