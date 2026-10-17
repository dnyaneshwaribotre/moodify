import { ExternalLink, Heart, Music, Pause, Play } from 'lucide-react'
import { usePlayer } from '../context/PlayerContext'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import {
  addFavorite,
  removeFavoriteBySong,
  recordInteraction,
} from '../services/userService'
import { formatDuration } from '../utils/constants'

export default function SongCard({ song, isFavorite, onFavoriteToggle, reason, queue }) {
  const { currentSong, isPlaying, playQueue, play, pause } = usePlayer()
  const { user } = useAuth()
  const { showToast } = useToast()

  const isCurrent = currentSong?.id === song.id
  const youtubeUrl = song.youtube_id
    ? `https://www.youtube.com/watch?v=${encodeURIComponent(song.youtube_id)}`
    : `https://www.youtube.com/results?search_query=${encodeURIComponent(`${song.title} ${song.artist} official audio`)}`
  const isThisPlaying = isCurrent && isPlaying

  async function handlePlay() {
    if (isCurrent) {
      isPlaying ? pause() : play()
      return
    }
    const list = queue?.length ? queue : [song]
    playQueue(list, Math.max(0, list.findIndex(item => item.id === song.id)))
    if (user) {
      try { await recordInteraction(song.id, 'play') } catch { /* non-blocking */ }
    }
  }

  async function handleFavorite(e) {
    e.stopPropagation()
    if (!user) return
    try {
      if (isFavorite) {
        await removeFavoriteBySong(song.id)
        showToast('Removed from favorites', 'info')
      } else {
        await addFavorite(song.id)
        await recordInteraction(song.id, 'favorite')
        showToast('Added to favorites', 'success')
      }
      onFavoriteToggle?.(song.id)
    } catch {
      showToast('Could not update favorite', 'error')
    }
  }

  return (
    <article className={`song-row ${isCurrent ? 'is-current' : ''}`}>
      <div className="song-art">
        {song.image_url
          ? <img src={song.image_url} alt="" />
          : <Music size={20} aria-hidden="true" />}
      </div>
      <div className="song-meta">
        <div className="song-title-line">
          <a className="song-title-link" href={youtubeUrl} target="_blank" rel="noopener noreferrer" title="Open on YouTube">
            <strong>{song.title}</strong>
          </a>
          {song.release_year && <span className="era-tag">{song.release_year}</span>}
          {isCurrent && <span className="playing-mark">NOW PLAYING</span>}
        </div>
        <span>{song.artist}{song.preview_url ? ` · ${formatDuration(song.duration)}` : ''}</span>
        {reason && <span className="song-reason">{reason}</span>}
      </div>
      <div className="song-actions">
        <button
          className={`icon-button ${isFavorite ? 'is-favorite' : ''}`}
          onClick={handleFavorite}
          aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          <Heart size={17} fill={isFavorite ? 'currentColor' : 'none'} />
        </button>
        <a
            href={youtubeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="icon-button"
            aria-label="Open on YouTube"
            title="Open on YouTube"
          >
            <ExternalLink size={17} />
          </a>
        <button
          className="play-button"
          onClick={handlePlay}
          aria-label={isThisPlaying ? 'Pause' : 'Play'}
        >
          {isThisPlaying ? <Pause size={17} fill="currentColor" /> : <Play size={17} fill="currentColor" />}
        </button>
      </div>
    </article>
  )
}
