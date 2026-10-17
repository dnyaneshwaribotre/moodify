import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertCircle, ArrowRight, Lock, Mail, UserRound } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { signUp } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await signUp(email, password, username)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.message || 'Could not create account.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="auth-wrap">
      <div className="auth-card">
        <span className="eyebrow">New account</span>
        <h2 style={{fontFamily:'Playfair Display, Georgia, serif', margin:'7px 0'}}>Make the first playlist.</h2>
        <p className="muted" style={{fontSize:'.9rem', marginBottom:24}}>A small profile helps recommendations feel less generic.</p>
        {error && <div className="form-error"><AlertCircle size={15} style={{verticalAlign:'-3px', marginRight:6}}/>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-field"><label className="form-label">Username</label><div style={{position:'relative'}}><UserRound size={16} style={{position:'absolute',left:12,top:12,color:'var(--muted)'}}/><input className="form-input" style={{paddingLeft:38}} value={username} onChange={e=>setUsername(e.target.value)} placeholder="your_name" required /></div></div>
          <div className="form-field"><label className="form-label">Email</label><div style={{position:'relative'}}><Mail size={16} style={{position:'absolute',left:12,top:12,color:'var(--muted)'}}/><input className="form-input" style={{paddingLeft:38}} type="email" value={email} onChange={e=>setEmail(e.target.value)} required /></div></div>
          <div className="form-field"><label className="form-label">Password</label><div style={{position:'relative'}}><Lock size={16} style={{position:'absolute',left:12,top:12,color:'var(--muted)'}}/><input className="form-input" style={{paddingLeft:38}} type="password" value={password} onChange={e=>setPassword(e.target.value)} minLength={6} required /></div></div>
          <button className="solid-button" style={{width:'100%'}} disabled={loading}>{loading ? 'Creating account…' : <>Create account <ArrowRight size={16}/></>}</button>
        </form>
        <p className="muted" style={{fontSize:'.8rem', marginTop:18}}>Already registered? <Link to="/login" style={{color:'var(--accent)',fontWeight:700}}>Sign in</Link></p>
      </div>
    </main>
  )
}
