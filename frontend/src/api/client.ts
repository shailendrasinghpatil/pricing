const API_BASE = import.meta.env.VITE_API_URL || ''

export interface StockQuote {
  symbol: string
  price: number | null
  change: number | null
  change_percent: number | null
  volume: number | null
  company_name: string | null
  currency: string | null
}

export interface WatchlistItem {
  id: number
  symbol: string
}

export interface SymbolSearchResult {
  symbol: string
  company_name: string
  exchange: string | null
}

async function fetchWithAuth(token: string, path: string, options: RequestInit = {}): Promise<Response> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  })
  if (!response.ok) {
    const error = await response.text()
    throw new Error(`API error ${response.status}: ${error}`)
  }
  return response
}

export const api = {
  async getWatchlist(token: string): Promise<WatchlistItem[]> {
    const res = await fetchWithAuth(token, '/api/watchlist/')
    return res.json()
  },

  async addToWatchlist(token: string, symbol: string): Promise<WatchlistItem> {
    const res = await fetchWithAuth(token, '/api/watchlist/', {
      method: 'POST',
      body: JSON.stringify({ symbol }),
    })
    return res.json()
  },

  async removeFromWatchlist(token: string, symbol: string): Promise<void> {
    await fetchWithAuth(token, `/api/watchlist/${symbol}`, { method: 'DELETE' })
  },

  async searchSymbols(token: string, query: string): Promise<SymbolSearchResult[]> {
    const res = await fetchWithAuth(token, `/api/stocks/search?q=${encodeURIComponent(query)}`)
    return res.json()
  },

  async getQuote(token: string, symbol: string): Promise<StockQuote> {
    const res = await fetchWithAuth(token, `/api/stocks/quote/${encodeURIComponent(symbol)}`)
    return res.json()
  },

  async getQuotes(token: string, symbols: string[]): Promise<StockQuote[]> {
    if (!symbols.length) return []
    const res = await fetchWithAuth(token, `/api/stocks/quotes?symbols=${symbols.join(',')}`)
    return res.json()
  },
}
