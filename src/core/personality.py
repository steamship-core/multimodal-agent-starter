from typing import Optional, List

from pydantic import BaseModel


class Personality(BaseModel):
    name: str
    byline: str
    identity: Optional[List[str]] = []
    behavior: Optional[List[str]] = []