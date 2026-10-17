import { useEffect, useState } from 'react'
import { ArrowLeft, Music2, Play, Trash2 } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { getPlaylistById, deletePlaylist } from '../services/playlistService'
import { getFavorites } from '../services/userService'
import { usePlayer } from '../context/PlayerContext'
import { useToast } from '../context/ToastContext'
import { MOOD_CONFIG, formatTotalDuration } from '../utils/constants'
import SongCard from '../components/SongCard'
import EmptyState from '../components/EmptyState'

export default function PlaylistPage() {
  const {id}=useParams()
  const navigate=useNavigate()
  const {playQueue}=usePlayer()
  const {showToast}=useToast()
  const [playlist,setPlaylist]=useState(null)
  const [favIds,setFavIds]=useState(new Set())
  const [loading,setLoading]=useState(true)

  useEffect(()=>{
    Promise.all([getPlaylistById(id),getFavorites()]).then(([p,f])=>{setPlaylist(p);setFavIds(new Set(f.map(x=>x.song?.id).filter(Boolean)))}).catch(()=>setPlaylist(null)).finally(()=>setLoading(false))
  },[id])

  async function remove() {
    try { await deletePlaylist(id); showToast('Playlist deleted','info'); navigate('/playlists') }
    catch { showToast('Could not delete playlist','error') }
  }

  if(loading) return <main className="page"><div className="shell"><div className="skeleton" style={{height:220}}/></div></main>
  if(!playlist) return <main className="page"><div className="shell"><EmptyState title="Playlist not found" message="It may have been deleted or is no longer available."/></div></main>

  const mood=MOOD_CONFIG[playlist.mood]||MOOD_CONFIG.chill
  return <main className="page"><div className="shell">
    <Link to="/playlists" className="text-button" style={{display:'inline-flex',gap:6,alignItems:'center',padding:0,marginBottom:18}}><ArrowLeft size={15}/> Playlists</Link>
    <div className="surface-card" style={{marginBottom:20}}>
      <div style={{display:'flex',gap:18,alignItems:'center',flexWrap:'wrap'}}>
        <div className="playlist-cover" style={{width:150,height:150,borderRadius:12,flex:'0 0 auto',background:playlist.cover_gradient||'#26312c'}}><Music2 size={48}/></div>
        <div style={{flex:1,minWidth:220}}><span className="eyebrow">Playlist</span><h1 style={{fontSize:'clamp(2rem,5vw,3.7rem)',margin:'7px 0'}}>{playlist.name}</h1><p className="muted" style={{marginBottom:6}}>{playlist.description}</p><span className="muted" style={{fontSize:'.75rem'}}>{mood.icon} {mood.label} · {playlist.song_count} tracks · {formatTotalDuration(playlist.total_duration)}</span></div>
      </div>
      <div style={{display:'flex',gap:8,marginTop:18}}><button className="solid-button" onClick={()=>playQueue(playlist.songs||[],0)} disabled={!playlist.songs?.length}><Play size={16}/> Play all</button><button className="icon-button" style={{width:'auto',padding:'0 13px',display:'inline-flex',gap:7}} onClick={remove}><Trash2 size={15}/> Delete</button></div>
    </div>
    {playlist.songs?.length?<div className="song-list">{playlist.songs.map((song,i)=><div key={song.id} style={{display:'grid',gridTemplateColumns:'28px 1fr',gap:6,alignItems:'center'}}><span className="muted" style={{textAlign:'center',font:'500 .68rem "DM Mono",monospace'}}>{String(i+1).padStart(2,'0')}</span><SongCard song={song} isFavorite={favIds.has(song.id)} onFavoriteToggle={id=>setFavIds(prev=>{const n=new Set(prev);n.has(id)?n.delete(id):n.add(id);return n})}/></div>)}</div>:<EmptyState title="Empty playlist" message="There are no tracks in this playlist yet."/>}
  </div></main>
}
