import { useAuth } from 'react-oidc-context'
import { Dashboard } from './components/Dashboard'
import './App.css'

function App() {
  const auth = useAuth()

  if (auth.isLoading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <p>Loading…</p>
      </div>
    )
  }

  if (auth.error) {
    return (
      <div className="error-screen">
        <h2>Authentication Error</h2>
        <p>{auth.error.message}</p>
        <button onClick={() => auth.signinRedirect()}>Retry Login</button>
      </div>
    )
  }

  if (!auth.isAuthenticated) {
    return (
      <div className="login-screen">
        <div className="login-card">
          <h1>📈 Stock Pricing</h1>
          <p>Real-time stock market prices at your fingertips.</p>
          <button className="login-btn" onClick={() => auth.signinRedirect()}>
            Sign In
          </button>
        </div>
      </div>
    )
  }

  return <Dashboard />
}

export default App
