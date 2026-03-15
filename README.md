# 📈 Stock Pricing Application

Real-time stock market pricing application with OpenID Connect authentication, live WebSocket price feeds, and persistent watchlists.

## Architecture

| Component | Technology |
|-----------|-----------|
| Backend API | Python 3.12+ · FastAPI · SQLAlchemy |
| Dependency mgmt | [uv](https://docs.astral.sh/uv/) |
| Frontend | React 19 · TypeScript · Vite |
| Authentication | OpenID Connect via Keycloak |
| Database | PostgreSQL 16 |
| Live prices | yfinance (Yahoo Finance) over WebSocket |
| Containerisation | Docker · Docker Compose |

## Quick Start (Docker)

```bash
# 1. Clone the repo and start everything
docker compose up --build

# 2. Open the app
open http://localhost:3000

# 3. Sign in with the demo account
#    Username: demo
#    Password: demo
```

Services:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| Keycloak admin | http://localhost:8080 (admin / admin) |

---

## Local Development (without Docker)

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (`pip install uv`)
- Node.js 22+
- PostgreSQL 16 (or use `docker compose up postgres keycloak -d`)

### Backend

```bash
cd backend

# Install dependencies with uv
uv sync

# Copy and edit env
cp ../.env.example .env

# Run migrations / create tables (auto on startup)
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy and edit env
cp ../.env.example .env.local

# Start dev server
npm run dev
# Opens on http://localhost:3000
```

---

## API Reference

### Authentication

All API endpoints (except `/health`) require a valid JWT bearer token obtained from Keycloak.

```
Authorization: Bearer <access_token>
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/watchlist/` | List user's watchlist |
| `POST` | `/api/watchlist/` | Add symbol to watchlist |
| `DELETE` | `/api/watchlist/{symbol}` | Remove symbol from watchlist |
| `GET` | `/api/stocks/search?q={query}` | Search stock symbols |
| `GET` | `/api/stocks/quote/{symbol}` | Get current quote |
| `GET` | `/api/stocks/quotes?symbols=A,B,C` | Get quotes for multiple symbols |
| `WS` | `/ws/prices?token={jwt}` | WebSocket live price feed |

### WebSocket Protocol

Connect with a valid JWT token as a query parameter:
```
ws://localhost:8000/ws/prices?token=<access_token>
```

Subscribe to symbols:
```json
{"type": "subscribe", "symbols": ["AAPL", "MSFT", "GOOGL"]}
```

Receive price updates (every ~5 seconds):
```json
{
  "type": "prices",
  "data": [
    {"symbol": "AAPL", "price": 175.42, "change": 1.23, "changePercent": 0.71},
    {"symbol": "MSFT", "price": 415.10, "change": -0.88, "changePercent": -0.21}
  ]
}
```

---

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://pricing:pricing@localhost:5432/pricing` | PostgreSQL connection string |
| `OIDC_ISSUER` | `http://localhost:8080/realms/pricing` | Expected `iss` claim in JWT tokens |
| `OIDC_JWKS_URL` | *(derived from OIDC_ISSUER)* | URL to fetch JSON Web Key Set |
| `OIDC_AUDIENCE` | `pricing-app` | Expected `aud` claim in JWT tokens |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins (JSON array) |

### Frontend (Vite build-time)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_KEYCLOAK_URL` | `http://localhost:8080` | Keycloak base URL |
| `VITE_KEYCLOAK_REALM` | `pricing` | Keycloak realm name |
| `VITE_KEYCLOAK_CLIENT_ID` | `pricing-app` | OIDC client ID |
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## Project Structure

```
pricing/
├── backend/                  # FastAPI Python application
│   ├── app/
│   │   ├── main.py           # FastAPI app + CORS + router registration
│   │   ├── auth.py           # JWT validation via OIDC JWKS
│   │   ├── config.py         # Pydantic settings
│   │   ├── database.py       # SQLAlchemy engine & session
│   │   ├── models.py         # ORM models (User, WatchlistItem)
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── crud.py           # Database operations
│   │   └── routers/
│   │       ├── stocks.py     # Stock search & quote endpoints
│   │       ├── watchlist.py  # Watchlist CRUD endpoints
│   │       └── prices_ws.py  # WebSocket live price feed
│   ├── pyproject.toml        # uv / PEP 517 project metadata
│   ├── .python-version       # Pinned Python version for uv
│   └── Dockerfile
├── frontend/                 # React + TypeScript application
│   ├── src/
│   │   ├── main.tsx          # Entry point + OIDC AuthProvider
│   │   ├── App.tsx           # Root component (login / dashboard)
│   │   ├── api/client.ts     # Typed API client
│   │   ├── hooks/
│   │   │   └── usePriceFeed.ts  # WebSocket hook
│   │   └── components/
│   │       ├── Dashboard.tsx    # Main authenticated view
│   │       ├── SymbolSearch.tsx # Stock symbol search
│   │       └── PriceCard.tsx    # Individual price display card
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
├── keycloak/
│   └── realm-export.json     # Auto-imported Keycloak realm config
├── docker-compose.yml
├── .env.example
└── README.md
```

## Adding More Users

Log into the Keycloak admin console at http://localhost:8080 (admin / admin), navigate to the `pricing` realm → Users → Add user.

## Notes

- **Python version**: The application targets Python 3.12+. Python 3.14 support will be available upon its stable release.
- **Price data**: Stock prices are sourced from Yahoo Finance via the `yfinance` library. Data may be delayed by 15–20 minutes for some exchanges.
- **PyCharm**: Open the `backend/` directory as the project root and configure the uv virtual environment (`.venv`) as the Python interpreter.
