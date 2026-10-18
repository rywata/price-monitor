from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Product(BaseModel):
    """Produto a ser monitorado em um site de e-commerce."""

    id: str = Field(
        ...,
        description="Identificador unico (SKU, EAN, MLB ID ou slug da URL)",
    )
    nome: str = Field(..., description="Nome do produto")
    description: str | None = Field(
        default=None,
        description="Descricao do produto (opcional)",
    )
    url: HttpUrl = Field(..., description="URL do produto")
    site: str = Field(..., description="Nome do site")


class Price(BaseModel):
    """Preco coletado de um produto em um momento especifico."""

    model_config = ConfigDict(
        json_encoders={Decimal: str},
    )

    product_id: str = Field(..., description="ID do Product monitorado")
    site: str = Field(..., description="Nome do site")
    price: Decimal = Field(..., description="Preco no momento da coleta")
    moeda: str = Field(default="BRL", description="Moeda ISO 4217")
    disponivel: bool = Field(default=True, description="Produto a venda?")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp UTC da coleta",
    )
    url_origem: str = Field(..., description="URL ou origem do preco")
