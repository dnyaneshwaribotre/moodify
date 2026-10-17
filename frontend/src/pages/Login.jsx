import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { AlertCircle, ArrowRight, Lock, Mail } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await signIn(email, password)
      navigate(location.state?.from?.pathname || '/dashboard', { replace: true })
    } catch (err) {
      setError(err.message || 'Could not sign in.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="auth-wrap">
      <div className="auth-card">
        <span className="eyebrow">Welcome back</span>
        <h2 style={{fontFamily:'Playfair Display, Georgia, serif', margin:'7px 0'}}>Your listening desk.</h2>
        <p className="muted" style={{fontSize:'.9rem', marginBottom:24}}>Sign in to continue your mood-based sessions.</p>
        {error && <div className="form-error"><AlertCircle size={15} style={{verticalAlign:'-3px', marginRight:6}}/>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-field">
            <label className="form-label">Email</label>
            <div style={{position:'relative'}}>
              <Mail size={16} style={{position:'absolute',left:12,top:12,color:'var(--muted)'}}/>
              <input className="form-input" style={{paddingLeft:38}} type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
            </div>
          </div>
          <div className="form-field">
            <label className="form-label">Password</label>
            <div style={{position:'relative'}}>
              <Lock size={16} style={{position:'absolute',left:12,top:12,color:'var(--muted)'}}/>
              <input className="form-input" style={{paddingLeft:38}} type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
            </div>
          </div>
          <button className="solid-button" style={{width:'100%'}} disabled={loading}>
            {loading ? 'Signing in…' : <>Sign in <ArrowRight size={16}/></>}
          </button>
        </form>
        <p className="muted" style={{fontSize:'.8rem', marginTop:18}}>
          New here? <Link to="/register" style={{color:'var(--accent)',fontWeight:700}}>Create an account</Link>
        </p>
      </div>
    </main>
  )
}
