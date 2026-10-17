import { useEffect, useState } from 'react'
import { TrendingUp } from 'lucide-react'
import { getTrendingSongs } from '../services/songService'
import { getFavorites } from '../services/userService'
import SongCard from '../components/SongCard'
import EmptyState from '../components/EmptyState'
import { SongListSkeleton } from '../components/Skeletons'
import { TRENDING_CATEGORIES } from '../utils/constants'

export default function Trending() {
  const [songs,setSongs]=useState([])
  const [category,setCategory]=useState('trending')
  const [loading,setLoading]=useState(true)
  const [favIds,setFavIds]=useState(new Set())

  useEffect(()=>{
    setLoading(true)
    Promise.all([getTrendingSongs(category,30),getFavorites()]).then(([tracks,favs])=>{setSongs(tracks);setFavIds(new Set(favs.map(x=>x.song?.id).filter(Boolean)))}).catch(()=>setSongs([])).finally(()=>setLoading(false))
  },[category])

  return <main className="page"><div className="shell">
    <div className="page-head"><div><span className="eyebrow"><TrendingUp size={13}/> Discovery</span><h1 style={{marginTop:7}}>Trending now.</h1><p>Current Indian hits, famous old classics, and songs by language.</p></div></div>
    <div className="chips" style={{marginBottom:18}}>{TRENDING_CATEGORIES.map(item=><button key={item.key} className="chip" style={category===item.key?{borderColor:'var(--accent)',color:'var(--accent)'}:{}} onClick={()=>setCategory(item.key)}>{item.icon} {item.label}</button>)}</div>
    {loading?<SongListSkeleton count={8}/>:
      songs.length?<div className="song-list">{songs.map((song,i)=><div key={song.id} style={{display:'grid',gridTemplateColumns:'28px 1fr',gap:6,alignItems:'center'}}><span className="muted" style={{textAlign:'center',font:'500 .68rem "DM Mono",monospace'}}>{String(i+1).padStart(2,'0')}</span><SongCard song={song} queue={songs} isFavorite={favIds.has(song.id)} onFavoriteToggle={id=>setFavIds(prev=>{const n=new Set(prev);n.has(id)?n.delete(id):n.add(id);return n})}/></div>)}</div>:
      <EmptyState title="No tracks found" message="Try another category."/>}
  </div></main>
}
