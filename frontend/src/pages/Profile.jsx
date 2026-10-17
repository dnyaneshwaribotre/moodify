import { useEffect, useState } from 'react'
import { Heart, Save, Sparkles, UserRound } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { getFavorites, getListeningHistory, getMoodHistory, updateProfile } from '../services/userService'
import { GENRES, LANGUAGES, MOOD_CONFIG } from '../utils/constants'

export default function Profile() {
  const { user, profile, refreshProfile } = useAuth()
  const { showToast } = useToast()
  const [username,setUsername]=useState('')
  const [genres,setGenres]=useState([])
  const [languages,setLanguages]=useState([])
  const [artists,setArtists]=useState('')
  const [mood,setMood]=useState('chill')
  const [saving,setSaving]=useState(false)
  const [stats,setStats]=useState({favorites:0,plays:0,moods:0})

  useEffect(()=>{
    if(!profile)return
    setUsername(profile.username||'');setGenres(profile.preferred_genres||[]);setLanguages(profile.preferred_languages||[])
    setArtists((profile.favorite_artists||[]).join(', '));setMood(profile.preferred_mood||'chill')
  },[profile])

  useEffect(()=>{
    Promise.all([getFavorites(),getListeningHistory(100),getMoodHistory(100)]).then(([f,h,m])=>setStats({favorites:f.length,plays:h.length,moods:m.length})).catch(()=>{})
  },[])

  function toggle(list,setter,value){setter(prev=>prev.includes(value)?prev.filter(x=>x!==value):[...prev,value])}
  async function save(){
    setSaving(true)
    try{await updateProfile({username,preferred_genres:genres,preferred_languages:languages,favorite_artists:artists.split(',').map(x=>x.trim()).filter(Boolean),preferred_mood:mood});await refreshProfile();showToast('Profile updated','success')}
    catch{showToast('Could not update profile','error')}
    finally{setSaving(false)}
  }

  if(!profile)return <main className="page"><div className="shell"><div className="skeleton" style={{height:180}}/></div></main>
  return <main className="page"><div className="shell">
    <div className="page-head"><div><span className="eyebrow"><UserRound size={13}/> Account</span><h1 style={{marginTop:7}}>Your profile.</h1><p>Shape the recommendations around how you listen.</p></div></div>
    <div className="profile-grid">
      <div>
        <div className="surface-card" style={{marginBottom:12}}><div style={{display:'flex',alignItems:'center',gap:12}}><div className="header-user"><span style={{width:48,height:48,fontSize:'1rem'}}>{(user?.username||'U').slice(0,1).toUpperCase()}</span></div><div><strong>{profile.username}</strong><div className="muted" style={{fontSize:'.78rem'}}>{profile.email}</div></div></div></div>
        <div className="stat-grid"><div className="stat"><Heart size={15}/><strong>{stats.favorites}</strong><span>Saved</span></div><div className="stat"><strong>{stats.plays}</strong><span>Recent plays</span></div><div className="stat"><Sparkles size={15}/><strong>{stats.moods}</strong><span>Mood sessions</span></div></div>
      </div>
      <div className="surface-card">
        <h3>Preferences</h3>
        <div className="form-field"><label className="form-label">Username</label><input className="form-input" value={username} onChange={e=>setUsername(e.target.value)}/></div>
        <div className="form-field"><label className="form-label">Genres</label><div className="preference-list">{GENRES.map(g=><button key={g} className="chip" style={genres.includes(g)?{borderColor:'var(--accent)',color:'var(--accent)'}:{}} onClick={()=>toggle(genres,setGenres,g)}>{g}</button>)}</div></div>
        <div className="form-field"><label className="form-label">Languages</label><div className="preference-list">{LANGUAGES.map(l=><button key={l} className="chip" style={languages.includes(l)?{borderColor:'var(--accent)',color:'var(--accent)'}:{}} onClick={()=>toggle(languages,setLanguages,l)}>{l}</button>)}</div></div>
        <div className="form-field"><label className="form-label">Favorite artists</label><input className="form-input" value={artists} onChange={e=>setArtists(e.target.value)} placeholder="Separate names with commas"/></div>
        <div className="form-field"><label className="form-label">Preferred mood</label><div className="preference-list">{Object.entries(MOOD_CONFIG).map(([key,cfg])=><button key={key} className="chip" style={mood===key?{borderColor:'var(--accent)',color:'var(--accent)'}:{}} onClick={()=>setMood(key)}>{cfg.icon} {cfg.label}</button>)}</div></div>
        <button className="solid-button" onClick={save} disabled={saving}><Save size={15}/>{saving?'Saving…':'Save changes'}</button>
      </div>
    </div>
  </div></main>
}
