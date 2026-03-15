import asyncio
import json
import time
import httpx
import jwt
from jwt import PyJWKClient, InvalidTokenError
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.config import settings
import yfinance as yf

router = APIRouter(tags=["prices"])

_ws_jwks_client: PyJWKClient | None = None
_ws_jwks_client_time: float = 0
_JWKS_TTL = 3600


def _get_jwks_client() -> PyJWKClient:
    global _ws_jwks_client, _ws_jwks_client_time
    now = time.time()
    if _ws_jwks_client is None or (now - _ws_jwks_client_time) >= _JWKS_TTL:
        _ws_jwks_client = PyJWKClient(settings.oidc_jwks_url, cache_keys=True)
        _ws_jwks_client_time = now
    return _ws_jwks_client


def _validate_ws_token(token: str) -> bool:
    """Validate JWT token for WebSocket connections (sync — called before accept)."""
    try:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
            options={"verify_exp": True},
        )
        return payload.get("sub") is not None
    except (InvalidTokenError, Exception):
        return False


def _fetch_price(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        fast_info = ticker.fast_info
        last_price = fast_info.last_price
        prev_close = fast_info.previous_close
        change = (last_price - prev_close) if prev_close else None
        change_pct = (change / prev_close * 100) if prev_close and change is not None else None
        return {
            "symbol": symbol,
            "price": last_price,
            "change": round(change, 4) if change is not None else None,
            "changePercent": round(change_pct, 4) if change_pct is not None else None,
        }
    except Exception as exc:
        return {"symbol": symbol, "error": str(exc)}


@router.websocket("/ws/prices")
async def websocket_prices(
    websocket: WebSocket,
    token: str = Query(default=None),
):
    """
    WebSocket endpoint for live price streaming.

    Clients send a subscribe message:
        {"type": "subscribe", "symbols": ["AAPL", "MSFT"]}

    Server pushes price updates every ~5 seconds:
        {"type": "prices", "data": [{...}, ...]}
    """
    if not token or not _validate_ws_token(token):
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await websocket.accept()
    symbols: list[str] = []

    try:
        while True:
            # Check for incoming control messages (non-blocking, 5-second poll)
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
                data = json.loads(raw)
                if data.get("type") == "subscribe":
                    symbols = [s.upper() for s in data.get("symbols", []) if s]
            except asyncio.TimeoutError:
                pass
            except (json.JSONDecodeError, KeyError):
                pass

            if symbols:
                prices = [_fetch_price(sym) for sym in symbols]
                await websocket.send_json({"type": "prices", "data": prices})

    except WebSocketDisconnect:
        pass
