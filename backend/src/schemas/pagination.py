from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel

# Define a generic type variable
T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    limit: int
    skip: int
    next: Optional[str] = None
    previous: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    meta: PaginationMeta
    data: List[T]  #
