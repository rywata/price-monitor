import pytest
import respx
from httpx import Response
from decimal import Decimal
from price_monitor.scrapers.shopify import ShopifyScraper
from price_monitor.http_client import HttpClient
from price_monitor.models import Product

@pytest.mark.asyncio
@respx.mock
async def test_shopify_produto_individual():
    respx.get("https://loja-teste.com/products/fone.json").mock(
        return_value=Response(200, json={
            "product": {"variants": [{"price": "199.90", "available": True}]}
        })
    )
    async with HttpClient() as client:
        scraper = ShopifyScraper(client)
        produto = Product(id="fone", nome="Fone", url="https://loja-teste.com/products/fone", site="shopify")
        price = await scraper.fetch_price(produto)
    assert price is not None
    assert price.price == Decimal("199.90")