import { useState } from 'react'
import {
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import './App.css'

import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Contracts from './pages/Contracts'
import NewContract from './pages/NewContract'
import Customers from './pages/Customers'
import Commissions from './pages/Commissions'
import Payments from './pages/Payments'
import Documents from './pages/Documents'
import Reports from './pages/Reports'
import Messages from './pages/Messages'
import Settings from './pages/Settings'

const API_URL = 'http://127.0.0.1:8000'

function App() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState(null)

  const handleLogin = async (event) => {
    event.preventDefault()

    setError('')
    setLoading(true)

    try {
      const formData = new URLSearchParams()
      formData.append('username', email.trim())
      formData.append('password', password)

      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Login failed')
      }

      const data = await response.json()

      if (!data.access_token) {
        throw new Error('No access token')
      }

      localStorage.setItem('access_token', data.access_token)

      const userResponse = await fetch(`${API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      })

      if (!userResponse.ok) {
        throw new Error('Could not load user')
      }

      const userData = await userResponse.json()

      setUser(userData)
      setPassword('')
    } catch (err) {
      console.error(err)
      localStorage.removeItem('access_token')
      setError('E-Mail oder Passwort ist nicht korrekt.')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
    setEmail('')
    setPassword('')
    setError('')
  }

  if (!user) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="brand">
            <div className="brand-icon">⚡</div>
            <h1>Gigawatt</h1>
            <span>Portal</span>
          </div>

          <h2>Willkommen zurück</h2>

          <p className="subtitle">
            Melden Sie sich an, um fortzufahren.
          </p>

          <form onSubmit={handleLogin}>
            <label htmlFor="email">
              E-Mail-Adresse
            </label>

            <input
              id="email"
              type="email"
              placeholder="name@unternehmen.at"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
            />

            <label htmlFor="password">
              Passwort
            </label>

            <input
              id="password"
              type="password"
              placeholder="Passwort"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />

            {error && (
              <div className="error">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? 'Anmeldung läuft...'
                : 'Anmelden'}
            </button>
          </form>

          <div className="login-footer">
            Energievertrieb einfach verwalten
          </div>
        </div>
      </div>
    )
  }

  return (
    <Routes>
      <Route
        element={
          <Layout
            user={user}
            onLogout={handleLogout}
          />
        }
      >
        <Route
          index
          element={<Dashboard user={user} />}
        />

        <Route
          path="contracts"
          element={<Contracts />}
        />

        <Route
          path="contracts/new"
          element={<NewContract />}
        />

        <Route
          path="customers"
          element={<Customers />}
        />

        <Route
          path="commissions"
          element={<Commissions />}
        />

        <Route
          path="payments"
          element={<Payments />}
        />

        <Route
          path="documents"
          element={<Documents />}
        />

        <Route
          path="reports"
          element={<Reports />}
        />

        <Route
          path="messages"
          element={<Messages />}
        />

        <Route
          path="settings"
          element={<Settings />}
        />

        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Route>
    </Routes>
  )
}

export default App