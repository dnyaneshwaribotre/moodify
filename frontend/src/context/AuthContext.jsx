import { createContext, useContext, useEffect, useState } from 'react'
import api from '../services/api'
const AuthContext = createContext(null)
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  async function loadProfile() {
    try { const { data } = await api.get('/auth/profile/'); setProfile(data); setUser(data.user || { id: data.id, email: data.email, username: data.username }) }
    catch { setUser(null); setProfile(null); localStorage.removeItem('moodify_access'); localStorage.removeItem('moodify_refresh') }
    finally { setLoading(false) }
  }
  useEffect(() => { if (localStorage.getItem('moodify_access')) loadProfile(); else setLoading(false) }, [])
  async function signUp(email, password, username) {
    const { data } = await api.post('/auth/register/', { email, password, username })
    localStorage.setItem('moodify_access', data.access); localStorage.setItem('moodify_refresh', data.refresh)
    setUser(data.user); setProfile(data.profile); return data
  }
  async function signIn(email, password) {
    const { data } = await api.post('/auth/login/', { email, password })
    localStorage.setItem('moodify_access', data.access); localStorage.setItem('moodify_refresh', data.refresh)
    setUser(data.user); setProfile(data.profile); return data
  }
  async function signOut() {
    const refresh = localStorage.getItem('moodify_refresh')
    try { if (refresh) await api.post('/auth/logout/', { refresh }) } catch { /* local logout still succeeds */ }
    localStorage.removeItem('moodify_access'); localStorage.removeItem('moodify_refresh'); setUser(null); setProfile(null)
  }
  async function refreshProfile() { if (!user) return; const { data } = await api.get('/auth/profile/'); setProfile(data); setUser(data.user || { id: data.id, email: data.email, username: data.username }) }
  return <AuthContext.Provider value={{ user, profile, loading, signUp, signIn, signOut, refreshProfile }}>{children}</AuthContext.Provider>
}
export function useAuth() { const ctx = useContext(AuthContext); if (!ctx) throw new Error('useAuth must be used within AuthProvider'); return ctx }
