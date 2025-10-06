from pydantic import BaseModel
from typing import Optional, List

class Location(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None

class LocationSearch(BaseModel):
    query: str
    limit: Optional[int] = 10

class LocationResponse(BaseModel):
    locations: List[Location]
    total: int