import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const AuthContext = createContext(null)

function readUser() {
  try {
    return JSON.parse(localStorage.getItem('user')) || null
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readUser)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const onLogout = () => setUser(null)
    window.addEventListener('auth:logout', onLogout)
    setLoading(false)
    return () => window.removeEventListener('auth:logout', onLogout)
  }, [])

  const login = (userData) => {
    localStorage.setItem('token', userData.token)
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  const value = useMemo(
    () => ({ user, login, logout, isAuthenticated: Boolean(user) }),
    [user],
  )

  return <AuthContext.Provider value={value}>{!loading && children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
