from pydantic import BaseModel, ConfigDict, Field


### Models
class FavoriteInDb(BaseModel):
    """Modelo para um favorito no banco de dados"""

    customer_id: int = Field(description='ID do cliente', gt=0)
    product_id: int = Field(description='ID do produto', gt=0)

    model_config = ConfigDict(from_attributes=True)


class ProductPublic(BaseModel):
    """Modelo para um produto"""

    id: int = Field(description='ID do produto', gt=0)
    title: str = Field(description='Título do produto')
    image: str = Field(description='URL da imagem do produto')
    price: float = Field(description='Preço do produto')
    review: float = Field(description='Review do produto', alias='rating.rate')


class FavoriteUpsert(BaseModel):
    product_id: int = Field(description='ID do produto', gt=0)
