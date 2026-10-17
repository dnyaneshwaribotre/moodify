import { useEffect, useState } from 'react'
import { ArrowRight, Compass, Heart, History, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getUserPlaylists, getPlaylistById } from '../services/playlistService'
import { getFavorites, getListeningHistory, getMoodHistory } from '../services/userService'
import { getTrendingSongs } from '../services/songService'
import { analyzeMood, getInsights } from '../services/backendApi'
import { useNavigate } from 'react-router-dom'
import { usePlayer } from '../context/PlayerContext'
import SongCard from '../components/SongCard'
import PlaylistCard from '../components/PlaylistCard'
import { MOOD_CONFIG, formatRelativeTime } from '../utils/constants'

export default function Dashboard() {
  const { user, profile } = useAuth()
  const { playQueue } = usePlayer()
  const [data,setData] = useState({playlists:[],favorites:[],history:[],moods:[],trending:[]})
  const [loading,setLoading] = useState(true)
  const [favIds,setFavIds] = useState(new Set())
  const [insight,setInsight] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    let active=true
    Promise.all([getUserPlaylists(),getFavorites(),getListeningHistory(6),getMoodHistory(5),getTrendingSongs(null,6)])
      .then(([playlists,favorites,history,moods,trending]) => {
        if (!active) return
        setData({playlists,favorites,history,moods,trending})
        setFavIds(new Set(favorites.map(item=>item.song?.id).filter(Boolean)))
      })
      .catch(()=>{})
      .finally(()=>active && setLoading(false))
    return ()=>{active=false}
  },[])

  useEffect(() => { getInsights().then(setInsight).catch(()=>{}) }, [])

  async function startSuggested() {
    const text = `I want ${insight.suggested_mood} music right now.`
    const result = await analyzeMood(text)
    navigate('/ai-result', { state: { text, ...result } })
  }

  async function playPlaylist(pl) {
    const full=await getPlaylistById(pl.id)
    if(full?.songs?.length) playQueue(full.songs,0)
  }

  if(loading) return <main className="page"><div className="shell"><div className="skeleton" style={{height:150}}/></div></main>

  const name=profile?.username || user?.email?.split('@')[0] || 'there'
  return (
    <main className="page">
      <div className="shell">
        <div className="page-head">
          <div><span className="eyebrow">Your listening desk</span><h1 style={{marginTop:7}}>Good to see you, {name}.</h1><p>Pick a direction or let your current mood set the tone.</p></div>
          <Link to="/mood" className="solid-button">Open mood studio <ArrowRight size={16}/></Link>
        </div>

        {insight && <div className="surface-card insight-card">
          <div><span className="badge"><Sparkles size={12}/> AI insight</span><p>{insight.message} {insight.suggestion_reason}</p></div>
          <button className="solid-button compact" onClick={startSuggested}>Play a {MOOD_CONFIG[insight.suggested_mood]?.label.toLowerCase()} session</button>
        </div>}

        <div className="stat-grid">
          <div className="stat"><Heart size={16}/><strong>{data.favorites.length}</strong><span>Saved tracks</span></div>
          <div className="stat"><History size={16}/><strong>{data.history.length}</strong><span>Recent plays</span></div>
          <div className="stat"><Sparkles size={16}/><strong>{data.moods.length}</strong><span>Mood sessions</span></div>
        </div>

        <div className="section">
          <div className="section-title"><h3>Your playlists</h3><Link to="/playlists">View all</Link></div>
          {data.playlists.length ? <div className="playlist-grid">{data.playlists.slice(0,4).map(pl=><PlaylistCard key={pl.id} playlist={pl} onClick={playPlaylist}/>)}</div> :
            <div className="empty-state"><Sparkles size={22}/><strong>No playlists yet</strong><span>Describe your mood to create your first one.</span></div>}
        </div>

        <div className="section" style={{display:'grid',gridTemplateColumns:'1.4fr .8fr',gap:22}}>
          <div>
            <div className="section-title"><h3>Trending now</h3><Link to="/trending">See all</Link></div>
            <div className="song-list">{data.trending.slice(0,5).map(song=><SongCard key={song.id} song={song} isFavorite={favIds.has(song.id)} onFavoriteToggle={id=>setFavIds(prev=>{const n=new Set(prev);n.has(id)?n.delete(id):n.add(id);return n})}/>)}</div>
          </div>
          <div>
            <div className="section-title"><h3>Recent moods</h3></div>
            <div className="history-list">
              {data.moods.length ? data.moods.map(m=>{const cfg=MOOD_CONFIG[m.detected_mood]||MOOD_CONFIG.chill; return <div className="history-entry" key={m.id}><p><strong>{cfg.icon} {cfg.label}</strong> · {m.detected_emotion}</p><small>{formatRelativeTime(m.created_at)} · {Math.round(m.confidence*100)}% confidence</small></div>}) :
                <div className="empty-state"><Compass size={20}/><strong>No mood sessions</strong><span>Your recent analyses will appear here.</span></div>}
            </div>
          </div>
        </div>

        {data.history.length>0 && <div className="section"><div className="section-title"><h3>Recently played</h3><Link to="/history">View history</Link></div><div className="song-list">{data.history.slice(0,4).map(h=><SongCard key={h.id} song={h.song} isFavorite={favIds.has(h.song?.id)} onFavoriteToggle={id=>setFavIds(prev=>{const n=new Set(prev);n.has(id)?n.delete(id):n.add(id);return n})}/>)}</div></div>}
      </div>
    </main>
  )
}
