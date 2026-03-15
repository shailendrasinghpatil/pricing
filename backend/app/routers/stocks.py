from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app import schemas, models
import yfinance as yf

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


def _build_quote(symbol: str) -> schemas.StockQuote:
    ticker = yf.Ticker(symbol)
    fast_info = ticker.fast_info
    prev_close = fast_info.previous_close
    last_price = fast_info.last_price
    change = (last_price - prev_close) if prev_close else None
    change_pct = (change / prev_close * 100) if prev_close and change is not None else None
    return schemas.StockQuote(
        symbol=symbol.upper(),
        price=last_price,
        change=change,
        change_percent=change_pct,
        volume=fast_info.three_month_average_volume,
        company_name=getattr(fast_info, "company_name", None),
        currency=getattr(fast_info, "currency", None),
    )


@router.get("/search", response_model=list[schemas.SymbolSearchResult])
async def search_symbols(
    q: str,
    current_user: models.User = Depends(get_current_user),
):
    """Search for stock symbols using Yahoo Finance."""
    if not q or len(q) < 1:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    try:
        results = []
        # yfinance search method available in newer versions
        ticker = yf.Ticker(q.upper())
        info = ticker.info
        if info and info.get("symbol"):
            results.append(
                schemas.SymbolSearchResult(
                    symbol=info["symbol"],
                    company_name=info.get("longName") or info.get("shortName") or info["symbol"],
                    exchange=info.get("exchange"),
                )
            )
        if not results:
            # Fallback: return the queried symbol directly
            results.append(
                schemas.SymbolSearchResult(
                    symbol=q.upper(),
                    company_name=q.upper(),
                )
            )
        return results
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Symbol lookup failed: {exc}")


@router.get("/quote/{symbol}", response_model=schemas.StockQuote)
async def get_quote(
    symbol: str,
    current_user: models.User = Depends(get_current_user),
):
    """Get the current price quote for a stock symbol."""
    try:
        return _build_quote(symbol)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Could not fetch quote: {exc}")


@router.get("/quotes", response_model=list[schemas.StockQuote])
async def get_quotes(
    symbols: str,
    current_user: models.User = Depends(get_current_user),
):
    """Get quotes for multiple comma-separated symbols."""
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    quotes = []
    for sym in symbol_list:
        try:
            quotes.append(_build_quote(sym))
        except Exception:
            quotes.append(schemas.StockQuote(symbol=sym))
    return quotes
