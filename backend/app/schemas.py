from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    oidc_sub: str


class User(UserBase):
    id: int
    oidc_sub: str

    class Config:
        from_attributes = True


class WatchlistItemCreate(BaseModel):
    symbol: str


class WatchlistItem(BaseModel):
    id: int
    symbol: str

    class Config:
        from_attributes = True


class StockQuote(BaseModel):
    symbol: str
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    company_name: Optional[str] = None
    currency: Optional[str] = None


class SymbolSearchResult(BaseModel):
    symbol: str
    company_name: str
    exchange: Optional[str] = None
