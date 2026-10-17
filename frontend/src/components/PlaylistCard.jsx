import { Music2 } from 'lucide-react'
import { MOOD_CONFIG, formatTotalDuration } from '../utils/constants'

export default function PlaylistCard({ playlist, onClick }) {
  const mood = MOOD_CONFIG[playlist.mood] || MOOD_CONFIG.chill
  return (
    <article className="playlist-card" onClick={()=>onClick?.(playlist)}>
      <div className="playlist-cover" style={{background: playlist.cover_gradient || '#26312c'}}>
        <Music2 size={38} />
      </div>
      <div className="playlist-card-body">
        <strong>{playlist.name}</strong>
        <span>{playlist.song_count || 0} songs · {formatTotalDuration(playlist.total_duration || 0)}</span>
        <span style={{color:'var(--accent)',marginTop:7}}>{mood.icon} {mood.label}</span>
      </div>
    </article>
  )
}
