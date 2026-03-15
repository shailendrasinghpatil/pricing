import { useState, useCallback } from 'react'
import { api, type SymbolSearchResult } from '../api/client'

interface SymbolSearchProps {
  token: string
  onAdd: (symbol: string) => void
  watchlistSymbols: string[]
}

export function SymbolSearch({ token, onAdd, watchlistSymbols }: SymbolSearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SymbolSearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const data = await api.searchSymbols(token, query.trim())
      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }, [token, query])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch()
  }

  return (
    <div className="symbol-search">
      <h3>Search Stocks</h3>
      <div className="search-row">
        <input
          type="text"
          placeholder="Enter symbol (e.g. AAPL, MSFT)"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button onClick={handleSearch} disabled={loading || !query.trim()}>
          {loading ? 'Searching…' : 'Search'}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      {results.length > 0 && (
        <ul className="search-results">
          {results.map(r => (
            <li key={r.symbol}>
              <span className="symbol">{r.symbol}</span>
              <span className="name">{r.company_name}</span>
              {r.exchange && <span className="exchange">{r.exchange}</span>}
              <button
                onClick={() => { onAdd(r.symbol); setResults([]); setQuery('') }}
                disabled={watchlistSymbols.includes(r.symbol)}
              >
                {watchlistSymbols.includes(r.symbol) ? 'Added' : '+ Watch'}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
