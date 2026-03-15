import { useEffect, useRef, useCallback } from 'react'

export interface PriceUpdate {
  symbol: string
  price: number | null
  change: number | null
  changePercent: number | null
  error?: string
}

type MessageHandler = (prices: PriceUpdate[]) => void

const WS_BASE = import.meta.env.VITE_WS_URL || ''

export function usePriceFeed(
  token: string | undefined,
  symbols: string[],
  onPrices: MessageHandler,
) {
  const wsRef = useRef<WebSocket | null>(null)
  const symbolsRef = useRef<string[]>(symbols)
  const onPricesRef = useRef<MessageHandler>(onPrices)

  // Keep refs up to date
  useEffect(() => { symbolsRef.current = symbols }, [symbols])
  useEffect(() => { onPricesRef.current = onPrices }, [onPrices])

  const send = useCallback((ws: WebSocket, syms: string[]) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'subscribe', symbols: syms }))
    }
  }, [])

  useEffect(() => {
    if (!token || symbolsRef.current.length === 0) {
      wsRef.current?.close()
      wsRef.current = null
      return
    }

    const wsUrl = WS_BASE
      ? `${WS_BASE.replace(/^http/, 'ws')}/ws/prices?token=${encodeURIComponent(token)}`
      : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/prices?token=${encodeURIComponent(token)}`

    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      send(ws, symbolsRef.current)
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'prices') {
          onPricesRef.current(msg.data)
        }
      } catch {
        // ignore parse errors
      }
    }

    ws.onerror = (err) => {
      console.warn('WebSocket error', err)
    }

    return () => {
      ws.close()
    }
  }, [token, send])  // Only reconnect when token changes

  // Re-subscribe when symbols change (without reconnecting)
  useEffect(() => {
    const ws = wsRef.current
    if (ws) {
      send(ws, symbols)
    }
  }, [symbols, send])
}
