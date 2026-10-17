import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, Music2 } from 'lucide-react'
import { getUserPlaylists } from '../services/playlistService'
import PlaylistCard from '../components/PlaylistCard'

export default function Playlists() {
  const [playlists,setPlaylists]=useState([])
  useEffect(()=>{getUserPlaylists().then(setPlaylists).catch(()=>setPlaylists([]))},[])
  return <main className="page"><div className="shell">
    <Link to="/dashboard" className="text-button" style={{display:'inline-flex',gap:6,alignItems:'center',padding:0,marginBottom:20}}><ArrowLeft size={15}/> Dashboard</Link>
    <div className="page-head"><div><span className="eyebrow"><Music2 size={13}/> Library</span><h1 style={{marginTop:7}}>Your playlists.</h1><p>Saved mood sessions, ready when you are.</p></div></div>
    {playlists.length ? <div className="playlist-grid">{playlists.map(p=><Link key={p.id} to={`/playlist/${p.id}`}><PlaylistCard playlist={p}/></Link>)}</div> :
      <div className="empty-state"><Music2 size={22}/><strong>No playlists yet</strong><span><Link to="/mood" style={{color:'var(--accent)',fontWeight:700}}>Create a mood session</Link> to get started.</span></div>}
  </div></main>
}
