import httpx
import time
import jwt
from jwt import PyJWKClient, ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app import crud, models

security = HTTPBearer()

# PyJWKClient with a simple TTL cache
_jwks_client: PyJWKClient | None = None
_jwks_client_time: float = 0
_JWKS_TTL = 3600


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client, _jwks_client_time
    now = time.time()
    if _jwks_client is None or (now - _jwks_client_time) >= _JWKS_TTL:
        _jwks_client = PyJWKClient(settings.oidc_jwks_url, cache_keys=True)
        _jwks_client_time = now
    return _jwks_client


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(credentials.credentials)
        payload = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
            options={"verify_exp": True},
        )
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exception
        email: str = payload.get("email", "")
        username: str = payload.get("preferred_username", email)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise credentials_exception
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )

    return crud.get_or_create_user(db, oidc_sub=sub, email=email, username=username)
