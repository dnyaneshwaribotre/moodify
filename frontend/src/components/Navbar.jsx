import { Compass, Heart, Home, LogOut, Menu, Music2, Sun, Moon, TrendingUp, UserRound, X } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

const navItems = [
  { path: '/dashboard', label: 'Home', icon: Home },
  { path: '/mood', label: 'Mood studio', icon: Compass },
  { path: '/trending', label: 'Trending', icon: TrendingUp },
  { path: '/favorites', label: 'Saved', icon: Heart },
  { path: '/history', label: 'History', icon: Music2 },
]

export default function Navbar() {
  const { user, signOut } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  async function handleSignOut() {
    await signOut()
    setOpen(false)
    navigate('/')
  }

  return (
    <header className="site-header">
      <div className="shell header-inner">
        <Link to={user ? '/dashboard' : '/'} className="wordmark" onClick={() => setOpen(false)}>
          <span className="wordmark-mark"><Music2 size={17} /></span>
          <span>Moodify</span>
        </Link>

        {user && (
          <nav className={`primary-nav ${open ? 'is-open' : ''}`}>
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={location.pathname === path ? 'active' : ''}
                onClick={() => setOpen(false)}
              >
                <Icon size={16} />
                {label}
              </Link>
            ))}
            <Link
              to="/profile"
              className={location.pathname === '/profile' ? 'active' : ''}
              onClick={() => setOpen(false)}
            >
              <UserRound size={16} />
              Profile
            </Link>
          </nav>
        )}

        <div className="header-actions">
          <button className="icon-button" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
          </button>
          {user ? (
            <button className="header-user" onClick={() => navigate('/profile')}>
              <span>{(user.username || user.email || 'U').slice(0, 1).toUpperCase()}</span>
              <strong>{user.username || 'Profile'}</strong>
            </button>
          ) : (
            <>
              <Link to="/login" className="text-button">Sign in</Link>
              <Link to="/register" className="solid-button compact">Create account</Link>
            </>
          )}
          {user && (
            <button className="icon-button desktop-only" onClick={handleSignOut} aria-label="Sign out">
              <LogOut size={17} />
            </button>
          )}
          {user && (
            <button className="icon-button mobile-only" onClick={() => setOpen(v => !v)} aria-label="Menu">
              {open ? <X size={19} /> : <Menu size={19} />}
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
