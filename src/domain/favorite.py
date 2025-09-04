from pydantic import BaseModel, Field


### Models
class Favorite(BaseModel):
    customer_id: int = Field(description='ID do cliente', gt=0)
    product_id: int = Field(description='ID do produto', gt=0)
