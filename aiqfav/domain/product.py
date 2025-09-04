from pydantic import BaseModel, Field


### Models
class ProductPublic(BaseModel):
    """Modelo para um produto"""

    id: int = Field(description='ID do produto', gt=0)
    title: str = Field(description='Título do produto')
    image: str = Field(description='URL da imagem do produto')
    price: float = Field(description='Preço do produto')
    rating: float | None = Field(description='Avaliação do produto')
