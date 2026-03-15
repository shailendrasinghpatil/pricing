from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import crud, schemas, models
from typing import List

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("/", response_model=List[schemas.WatchlistItem])
async def get_watchlist(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's watchlist."""
    return crud.get_watchlist(db, current_user.id)


@router.post("/", response_model=schemas.WatchlistItem, status_code=201)
async def add_symbol(
    item: schemas.WatchlistItemCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a stock symbol to the user's watchlist."""
    result = crud.add_to_watchlist(db, current_user.id, item.symbol)
    if result is None:
        raise HTTPException(status_code=409, detail="Symbol already in watchlist")
    return result


@router.delete("/{symbol}", status_code=204)
async def remove_symbol(
    symbol: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a stock symbol from the user's watchlist."""
    crud.remove_from_watchlist(db, current_user.id, symbol)
