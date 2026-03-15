import { type PriceUpdate } from '../hooks/usePriceFeed'

interface PriceCardProps {
  symbol: string
  price: PriceUpdate | null
  onRemove: (symbol: string) => void
}

function fmt(value: number | null | undefined, decimals = 2): string {
  if (value == null) return '—'
  return value.toFixed(decimals)
}

export function PriceCard({ symbol, price, onRemove }: PriceCardProps) {
  const isPositive = price?.change != null && price.change >= 0
  const changeClass = price?.change == null ? '' : isPositive ? 'positive' : 'negative'

  return (
    <div className={`price-card ${changeClass}`}>
      <div className="card-header">
        <span className="card-symbol">{symbol}</span>
        <button className="remove-btn" onClick={() => onRemove(symbol)} title="Remove from watchlist">
          ×
        </button>
      </div>

      {price?.error ? (
        <p className="card-error">{price.error}</p>
      ) : (
        <>
          <div className="card-price">${fmt(price?.price)}</div>
          <div className={`card-change ${changeClass}`}>
            {price?.change != null ? (isPositive ? '+' : '') + fmt(price.change) : '—'}
            {' '}
            ({price?.changePercent != null
              ? (isPositive ? '+' : '') + fmt(price.changePercent) + '%'
              : '—'})
          </div>
          {price == null && <div className="card-loading">Loading…</div>}
        </>
      )}
    </div>
  )
}
