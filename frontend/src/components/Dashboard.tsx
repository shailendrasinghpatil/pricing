import { useState, useEffect, useCallback } from 'react'
import { useAuth } from 'react-oidc-context'
import { api, type WatchlistItem } from '../api/client'
import { type PriceUpdate, usePriceFeed } from '../hooks/usePriceFeed'
import { SymbolSearch } from './SymbolSearch'
import { PriceCard } from './PriceCard'

export function Dashboard() {
  const auth = useAuth()
  const token = auth.user?.access_token ?? ''

  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([])
  const [prices, setPrices] = useState<Record<string, PriceUpdate>>({})
  const [loadingWatchlist, setLoadingWatchlist] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load watchlist on mount
  useEffect(() => {
    if (!token) return
    api.getWatchlist(token)
      .then(setWatchlist)
      .catch(err => setError(err.message))
      .finally(() => setLoadingWatchlist(false))
  }, [token])

  const symbols = watchlist.map(w => w.symbol)

  // Handle incoming price updates
  const handlePrices = useCallback((updates: PriceUpdate[]) => {
    setPrices(prev => {
      const next = { ...prev }
      updates.forEach(u => { next[u.symbol] = u })
      return next
    })
  }, [])

  usePriceFeed(token || undefined, symbols, handlePrices)

  const handleAdd = useCallback(async (symbol: string) => {
    try {
      const item = await api.addToWatchlist(token, symbol)
      setWatchlist(prev => [...prev, item])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add symbol')
    }
  }, [token])

  const handleRemove = useCallback(async (symbol: string) => {
    try {
      await api.removeFromWatchlist(token, symbol)
      setWatchlist(prev => prev.filter(w => w.symbol !== symbol))
      setPrices(prev => {
        const next = { ...prev }
        delete next[symbol]
        return next
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove symbol')
    }
  }, [token])

  const handleLogout = () => auth.signoutRedirect()

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>📈 Stock Pricing</h1>
        <div className="user-info">
          <span>{auth.user?.profile?.preferred_username || auth.user?.profile?.email}</span>
          <button onClick={handleLogout} className="logout-btn">Sign Out</button>
        </div>
      </header>

      <main>
        {error && (
          <div className="error-banner">
            {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        <SymbolSearch
          token={token}
          onAdd={handleAdd}
          watchlistSymbols={symbols}
        />

        <section className="watchlist-section">
          <h2>My Watchlist</h2>
          {loadingWatchlist ? (
            <p>Loading watchlist…</p>
          ) : watchlist.length === 0 ? (
            <p className="empty-state">No stocks in your watchlist yet. Search above to add some!</p>
          ) : (
            <div className="price-grid">
              {watchlist.map(item => (
                <PriceCard
                  key={item.symbol}
                  symbol={item.symbol}
                  price={prices[item.symbol] ?? null}
                  onRemove={handleRemove}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
