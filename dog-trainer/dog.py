from pydantic.fields import Field
from pydantic.main import BaseModel


class Dog(BaseModel):
    """Class which stores information about one of your dogs."""

    name: str = Field(description="Name of the dog.")
    breed: str = Field(default="mutt", description="Breed of the dog.")
    description: str = Field(
        default="description", description="Description of the dog's personality."
    )
