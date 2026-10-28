from abc import ABC, abstractmethod

from price_monitor.http_client import HttpClient
from price_monitor.models import Price, Product


class BaseScraper(ABC):
    """Contrato que todo scraper de site deve seguir."""

    site_name: str = "desconhecido"

    def __init__(self, client: HttpClient) -> None:
        self.client = client

    @abstractmethod
    async def fetch_price(self, product: Product) -> Price | None:
        """Busca preco de um produto. Retorna None se indisponivel ou invalido."""
        ...

    def supports(self, product: Product) -> bool:
        """Verifica se este scraper suporta o produto."""
        return product.site == self.site_name
