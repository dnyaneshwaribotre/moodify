import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { PlayerProvider } from './context/PlayerContext'
import { ToastProvider } from './context/ToastContext'
import Navbar from './components/Navbar'
import MusicPlayer from './components/MusicPlayer'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import MoodInput from './pages/MoodInput'
import AIResult from './pages/AIResult'
import PlaylistPage from './pages/PlaylistPage'
import Favorites from './pages/Favorites'
import History from './pages/History'
import Trending from './pages/Trending'
import Profile from './pages/Profile'
import Playlists from './pages/Playlists'

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => { window.scrollTo(0, 0) }, [pathname])
  return null
}

function RequireAuth({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <div className="d-flex align-items-center justify-content-center min-vh-100"><div className="spinner-border text-primary" role="status"><span className="visually-hidden">Loading...</span></div></div>
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}

function AppRoutes() {
  const { user, loading } = useAuth()
  if (loading) return <div className="d-flex align-items-center justify-content-center min-vh-100"><div className="spinner-border text-primary" role="status"><span className="visually-hidden">Loading...</span></div></div>
  return (
    <Routes>
      <Route path="/" element={user ? <Navigate to="/dashboard" /> : <Landing />} />
      <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Register />} />
      <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
      <Route path="/mood" element={<RequireAuth><MoodInput /></RequireAuth>} />
      <Route path="/ai-result" element={<RequireAuth><AIResult /></RequireAuth>} />
      <Route path="/playlists" element={<RequireAuth><Playlists /></RequireAuth>} />
      <Route path="/playlist/:id" element={<RequireAuth><PlaylistPage /></RequireAuth>} />
      <Route path="/favorites" element={<RequireAuth><Favorites /></RequireAuth>} />
      <Route path="/history" element={<RequireAuth><History /></RequireAuth>} />
      <Route path="/trending" element={<RequireAuth><Trending /></RequireAuth>} />
      <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <BrowserRouter>
            <PlayerProvider>
              <ScrollToTop />
              <Navbar />
              <AppRoutes />
              <MusicPlayer />
            </PlayerProvider>
          </BrowserRouter>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  )
}

export default App
