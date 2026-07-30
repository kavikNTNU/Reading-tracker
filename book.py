from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    status: str
    pages: int

