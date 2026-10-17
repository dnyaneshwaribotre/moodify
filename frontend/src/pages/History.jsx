import { useEffect, useState } from 'react'
import { Clock3, History as HistoryIcon } from 'lucide-react'
import { getListeningHistory, getMoodHistory } from '../services/userService'
import SongCard from '../components/SongCard'
import EmptyState from '../components/EmptyState'
import { SongListSkeleton } from '../components/Skeletons'
import { MOOD_CONFIG, formatRelativeTime } from '../utils/constants'

export default function History() {
  const [history,setHistory]=useState([])
  const [moods,setMoods]=useState([])
  const [tab,setTab]=useState('songs')
  const [loading,setLoading]=useState(true)
  const [favIds,setFavIds]=useState(new Set())

  useEffect(()=>{
    Promise.all([getListeningHistory(50),getMoodHistory(30)]).then(([h,m])=>{setHistory(h);setMoods(m)}).catch(()=>{}).finally(()=>setLoading(false))
  },[])

  return <main className="page"><div className="shell">
    <div className="page-head"><div><span className="eyebrow"><HistoryIcon size={13}/> Archive</span><h1 style={{marginTop:7}}>Your history.</h1><p>A simple record of what you have been listening to.</p></div></div>
    <div className="chips" style={{marginBottom:20}}>
      <button className="chip" style={tab==='songs'?{borderColor:'var(--accent)',color:'var(--accent)'}:{}} onClick={()=>setTab('songs')}>Listening</button>
      <button className="chip" style={tab==='moods'?{borderColor:'var(--accent)',color:'var(--accent)'}:{}} onClick={()=>setTab('moods')}>Mood sessions</button>
    </div>
    {loading?<SongListSkeleton count={6}/>:
      tab==='songs'?
        (history.length?<div className="history-list">{history.map(item=><div key={item.id}><small className="muted" style={{display:'block',margin:'0 0 4px 2px'}}>{formatRelativeTime(item.played_at)}{item.completed?' · Completed':''}</small><SongCard song={item.song} isFavorite={favIds.has(item.song?.id)} onFavoriteToggle={id=>setFavIds(prev=>{const n=new Set(prev);n.has(id)?n.delete(id):n.add(id);return n})}/></div>)}</div>:<EmptyState icon={Clock3} title="No listening history" message="Play a track and it will appear here."/>)
      : moods.length ?
        <div className="history-list">{moods.map(m=>{const cfg=MOOD_CONFIG[m.detected_mood]||MOOD_CONFIG.chill; return <div className="history-entry" key={m.id}><p><strong>{cfg.icon} {cfg.label}</strong> · {m.detected_emotion}</p><small>{m.input_text?.slice(0,120)}{m.input_text?.length>120?'…':''}</small><div style={{marginTop:8,color:'var(--muted)',fontSize:'.7rem'}}>{formatRelativeTime(m.created_at)} · {Math.round(m.confidence*100)}% confidence · {m.energy_level} energy</div></div>})}</div>
        : <EmptyState icon={HistoryIcon} title="No mood sessions" message="Your mood analyses will appear here."/>}
  </div></main>
}
