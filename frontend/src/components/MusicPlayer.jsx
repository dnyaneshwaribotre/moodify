import { Loader2, Music2, Pause, Play, Repeat, Repeat1, Shuffle, SkipBack, SkipForward, Tv, Volume2, VolumeX } from 'lucide-react'
import { usePlayer } from '../context/PlayerContext'
import { formatDuration } from '../utils/constants'

export default function MusicPlayer() {
  const { currentSong, isPlaying, loadingTrack, source, progress, clipSeconds, volume, shuffle, repeat, showVideo, play, pause, next, prev, seek, setVolume, toggleShuffle, cycleRepeat, toggleVideo } = usePlayer()
  if (!currentSong) return null
  const label = ''

  return (
    <div className="player-bar">
      <div className="player-song-info">
        <div className="player-art">{currentSong.image_url ? <img src={currentSong.image_url} alt="" /> : <Music2 size={19} />}</div>
        <div className="player-copy"><strong>{currentSong.title}</strong><span>{currentSong.artist}{label && ` · ${label}`}</span></div>
      </div>
      <div className="player-controls">
        <button className="icon-button" onClick={toggleShuffle} aria-label="Shuffle" style={shuffle ? { color: 'var(--accent)' } : {}}><Shuffle size={15} /></button>
        <button className="icon-button" onClick={prev} aria-label="Previous"><SkipBack size={15} /></button>
        <button className="play-button" onClick={isPlaying ? pause : play} aria-label={isPlaying ? 'Pause' : 'Play'}>
          {loadingTrack ? <Loader2 size={16} className="spin" /> : isPlaying ? <Pause size={16} /> : <Play size={16} />}
        </button>
        <button className="icon-button" onClick={next} aria-label="Next"><SkipForward size={15} /></button>
        <button className="icon-button" onClick={cycleRepeat} aria-label="Repeat" style={repeat !== 'off' ? { color: 'var(--accent)' } : {}}>{repeat === 'one' ? <Repeat1 size={15} /> : <Repeat size={15} />}</button>
      </div>
      <div className="player-progress">
        <span className="player-time">{formatDuration(Math.floor((progress / 100) * clipSeconds))}</span>
        <div className="progress-track" onClick={e => { const r = e.currentTarget.getBoundingClientRect(); seek(((e.clientX - r.left) / r.width) * 100) }}><div className="progress-fill" style={{ width: `${progress}%` }} /></div>
        <span className="player-time">{formatDuration(Math.floor(clipSeconds))}</span>
        <div className="player-volume">
          <button className="icon-button" onClick={() => setVolume(volume > 0 ? 0 : 0.7)} aria-label="Mute">{volume > 0 ? <Volume2 size={15} /> : <VolumeX size={15} />}</button>
          <div className="volume-track" onClick={e => { const r = e.currentTarget.getBoundingClientRect(); setVolume(Math.min(1, Math.max(0, (e.clientX - r.left) / r.width))) }}><div className="volume-fill" style={{ width: `${volume * 100}%` }} /></div>
        </div>
      </div>
    </div>
  )
}
