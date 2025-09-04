from pydantic import BaseModel, ConfigDict, Field


### Models
class Favorite(BaseModel):
    customer_id: int = Field(description='ID do cliente', gt=0)
    product_id: int = Field(description='ID do produto', gt=0)

    model_config = ConfigDict(from_attributes=True)
