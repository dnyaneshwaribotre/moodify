import { useEffect, useState } from 'react'
import { Heart, Search } from 'lucide-react'
import { getFavorites } from '../services/userService'
import SongCard from '../components/SongCard'
import EmptyState from '../components/EmptyState'
import { SongListSkeleton } from '../components/Skeletons'

export default function Favorites() {
  const [favorites,setFavorites]=useState([])
  const [search,setSearch]=useState('')
  const [loading,setLoading]=useState(true)

  useEffect(()=>{
    getFavorites().then(setFavorites).catch(()=>setFavorites([])).finally(()=>setLoading(false))
  },[])

  const filtered=favorites.filter(item=>{
    const q=search.toLowerCase()
    return item.song?.title?.toLowerCase().includes(q) || item.song?.artist?.toLowerCase().includes(q)
  })

  return <main className="page"><div className="shell">
    <div className="page-head"><div><span className="eyebrow"><Heart size={13}/> Your library</span><h1 style={{marginTop:7}}>Saved tracks.</h1><p>Keep the songs that you want to hear again.</p></div><span className="muted" style={{fontSize:'.75rem'}}>{favorites.length} saved</span></div>
    {loading?<SongListSkeleton count={6}/>:
      favorites.length===0?<EmptyState icon={Heart} title="Nothing saved yet" message="Use the heart on a track to keep it here."/>:
      <>
        <div style={{position:'relative',maxWidth:430,marginBottom:14}}><Search size={16} style={{position:'absolute',left:12,top:12,color:'var(--muted)'}}/><input className="form-input" style={{paddingLeft:37}} placeholder="Search saved tracks" value={search} onChange={e=>setSearch(e.target.value)}/></div>
        <div className="song-list">{filtered.map(item=><SongCard key={item.id} song={item.song} isFavorite onFavoriteToggle={id=>setFavorites(prev=>prev.filter(x=>x.song?.id!==id))}/>)}</div>
        {!filtered.length && <div className="empty-state" style={{marginTop:12}}><span>No saved tracks match that search.</span></div>}
      </>}
  </div></main>
}
