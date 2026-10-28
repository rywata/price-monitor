"""Scraper para lojas Shopify via endpoint publico .json.

Suporta dois formatos:
- /products/{handle}.json  -> {"product": {...}}
- /products.json           -> {"products": [{...}, ...]}
"""

from decimal import Decimal, InvalidOperation
from typing import cast

from loguru import logger

from price_monitor.models import Price, Product
from price_monitor.scrapers.base import BaseScraper


class ShopifyScraper(BaseScraper):
    """Coleta precos de lojas Shopify via endpoint .json publico."""

    site_name = "shopify"

    async def fetch_price(self, product: Product) -> Price | None:
        """Busca o preco de um produto Shopify."""
        if product.id and not (product.url.path or "").endswith(".json"):
            url_individual = f"{product.url}.json"
        else:
            url_individual = str(product.url)

        logger.info(f"[Shopify] Buscando {url_individual}")

        data = await self._fetch_json(url_individual)

        if data is None or "product" not in data:
            logger.info("[Shopify] Tentando catalogo /products.json")
            url_catalogo = f"{product.url.scheme}://{product.url.host}/products.json?limit=1"
            data = await self._fetch_json(url_catalogo)

        if data is None:
            return None

        product_data = self._extrair_produto(data)
        if product_data is None:
            return None

        try:
            variants = product_data["variants"]
            if not isinstance(variants, list) or not variants:
                logger.warning(f"[Shopify] Sem variantes para {product.id}")
                return None

            variant = variants[0]
            if not isinstance(variant, dict):
                return None

            preco = Decimal(str(variant["price"]))
            disponivel = bool(variant.get("available", True))

            return Price(
                product_id=product.id,
                site=self.site_name,
                price=preco,
                moeda="BRL",
                disponivel=disponivel,
                url_origem=str(product.url),
            )

        except (KeyError, IndexError, TypeError, InvalidOperation) as e:
            logger.error(f"[Shopify] Estrutura inesperada: {e}")
            return None

    async def _fetch_json(self, url: str) -> dict[str, object] | None:
        """Faz a request e devolve o JSON, ou None em caso de falha."""
        try:
            data = await self.client.get_json(url)
            if isinstance(data, dict):
                return data
            return None
        except Exception as e:
            logger.debug(f"[Shopify] Falha em {url}: {e}")
            return None

    def _extrair_produto(self, data: dict[str, object]) -> dict[str, object] | None:
        """Extrai o dicionario do produto de qualquer formato."""
        if "product" in data:
            return cast(dict[str, object], data["product"])
        products = data.get("products")
        if isinstance(products, list) and products:
            first = products[0]
            if isinstance(first, dict):
                return cast(dict[str, object], first)
        logger.error("[Shopify] Nenhum produto encontrado no JSON")
        return None
