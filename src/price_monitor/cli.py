import asyncio
from pathlib import Path

import pandas as pd
import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from price_monitor.config import settings
from price_monitor.http_client import HttpClient
from price_monitor.models import Price, Product
from price_monitor.scrapers.base import BaseScraper
from price_monitor.scrapers.shopify import ShopifyScraper

app = typer.Typer(help="Monitor de precos para e-commerce.")
console = Console()


def setup_logging() -> None:
    """Configura loguru para terminal colorido + arquivo rotativo."""
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(exist_ok=True)

    logger.remove()
    logger.add(
        sink=lambda msg: console.print(msg, end=""),
        level=settings.log_level,
        colorize=True,
    )
    logger.add(
        log_dir / "price_monitor.log",
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8",
    )


def carregar_produtos(arquivo: Path) -> list[Product]:
    """Le um CSV de produtos e valida com pydantic."""
    if not arquivo.exists():
        raise typer.BadParameter(f"Arquivo nao encontrado: {arquivo}")

    df = pd.read_csv(arquivo)
    logger.info(f"CSV carregado: {len(df)} produtos")

    produtos: list[Product] = []
    for i, row in df.iterrows():
        try:
            produto = Product(**row.to_dict())
            produtos.append(produto)
        except Exception as e:
            logger.warning(f"Linha {i + 2} invalida: {e}")  # +2 = header + index 0

    if not produtos:
        raise typer.BadParameter("Nenhum produto valido no CSV")

    return produtos


def _criar_scrapers(client: HttpClient) -> dict[str, BaseScraper]:
    """Instancia todos os scrapers disponiveis, indexados por site."""
    scrapers: list[BaseScraper] = [
        ShopifyScraper(client),
        # MercadoLivreScraper(client),  # descomente quando tiver credenciais
    ]
    return {s.site_name: s for s in scrapers}


async def coletar_precos(produtos: list[Product]) -> list[Price]:
    """Roda todos os scrapers em paralelo (com rate limit compartilhado)."""
    precos: list[Price] = []

    async with HttpClient() as client:
        scrapers = _criar_scrapers(client)

        for produto in produtos:
            scraper = scrapers.get(produto.site)
            if not scraper:
                logger.warning(
                    f"Site sem scraper registrado: {produto.site} " f"(produto {produto.id})"
                )
                continue

            price = await scraper.fetch_price(produto)
            if price is not None:
                precos.append(price)
                logger.success(f"[{produto.site}] {produto.id}: R$ {price.price:.2f}")

    return precos


def exibir_resultados(precos: list[Price]) -> None:
    """Mostra os precos coletados em tabela colorida."""
    if not precos:
        console.print("[yellow]Nenhum preco coletado.[/yellow]")
        return

    table = Table(title="Precos Coletados")
    table.add_column("Site", style="cyan")
    table.add_column("Produto", style="magenta")
    table.add_column("Preco", justify="right", style="green")
    table.add_column("Disponivel", justify="center")

    for price in precos:
        table.add_row(
            price.site,
            price.product_id,
            f"R$ {price.price:.2f}",
            "✅" if price.disponivel else "❌",
        )

    console.print(table)


def salvar_resultados(precos: list[Price]) -> None:
    """Salva os precos coletados em CSV."""
    if not precos:
        logger.warning("Nada para salvar.")
        return

    data_dir = Path(settings.data_dir)
    data_dir.mkdir(exist_ok=True)
    saida = data_dir / "precos.csv"

    df = pd.DataFrame([p.model_dump() for p in precos])
    df.to_csv(saida, index=False, encoding="utf-8")
    logger.success(f"{len(precos)} precos salvos em {saida}")


@app.command()  # type: ignore[misc]
def coletar(
    arquivo: Path = typer.Option(  # noqa: B008
        ...,
        "--arquivo",
        "-a",
        help="CSV com colunas: id,nome,url,site",
        exists=True,
        readable=True,
    ),
) -> None:
    """Coleta precos a partir de um CSV de produtos."""
    setup_logging()
    logger.info(f"Iniciando coleta: {arquivo}")

    produtos = carregar_produtos(arquivo)
    precos = asyncio.run(coletar_precos(produtos))

    exibir_resultados(precos)
    salvar_resultados(precos)

    logger.success("Coleta finalizada.")


if __name__ == "__main__":
    app()
