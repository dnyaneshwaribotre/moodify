import { useEffect, useMemo, useState } from 'react'
import { ArrowLeft, Bot, Gauge, Loader2, Music2, Save, Sparkles } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { usePlayer } from '../context/PlayerContext'
import { getFavorites } from '../services/userService'
import { getRecommendations } from '../services/backendApi'
import { createPlaylist } from '../services/playlistService'
import { MOOD_CONFIG } from '../utils/constants'
import SongCard from '../components/SongCard'

export default function AIResult() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const { playQueue } = usePlayer()
  const result = location.state
  const [session, setSession] = useState(null)
  const [favIds, setFavIds] = useState(new Set())
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!result) { navigate('/mood', { replace: true }); return }
    let active = true
    async function load() {
      try {
        const chosen = result.language_choice
        const language = chosen && chosen !== 'indian' ? chosen : (result.requested_language || (result.language !== 'english' ? result.language : 'indian'))
        const [data, favorites] = await Promise.all([
          getRecommendations({
            mood: result.mood, energy_level: result.energy_level,
            language, era_preference: result.era_preference,
          }),
          user ? getFavorites() : Promise.resolve([]),
        ])
        if (!active) return
        setSession(data)
        setFavIds(new Set(favorites.map(item => item.song?.id).filter(Boolean)))
      } catch { if (active) showToast('Could not load recommendations.', 'error') }
      finally { if (active) setLoading(false) }
    }
    load()
    return () => { active = false }
  }, [result, user, navigate, showToast])

  const allSongs = useMemo(() => (session?.sections || []).flatMap(section => section.songs), [session])

  if (!result) return null
  const cfg = MOOD_CONFIG[result.mood] || MOOD_CONFIG.chill
  const toggleFav = id => setFavIds(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n })

  function playAll() { playQueue(allSongs, 0) }

  async function savePlaylist() {
    if (!allSongs.length || !user) return
    setSaving(true)
    try {
      const playlist = await createPlaylist({
        name: result.playlist_name || 'Mood Session',
        mood: result.mood, emotion: result.emotion, energy_level: result.energy_level,
        confidence: result.confidence,
        description: `Created from “${result.text?.slice(0, 100)}${result.text?.length > 100 ? '…' : ''}”`,
        songs: allSongs,
      })
      showToast('Playlist saved.', 'success')
      navigate(`/playlist/${playlist.id}`)
    } catch { showToast('Could not save the playlist.', 'error') }
    finally { setSaving(false) }
  }

  return (
    <main className="page">
      <div className="shell">
        <Link to="/mood" className="text-button" style={{ display: 'inline-flex', gap: 6, alignItems: 'center', padding: 0, marginBottom: 20 }}><ArrowLeft size={15} /> New mood</Link>
        <div className="result-panel">
          <span className="eyebrow"><Sparkles size={13} /> Session profile</span>
          <h1 style={{ fontSize: 'clamp(2.3rem,6vw,4.3rem)', margin: '8px 0' }}>{result.playlist_name || `Your ${cfg.label.toLowerCase()} set`}.</h1>
          <p className="muted" style={{ maxWidth: 700, marginBottom: 0 }}>“{result.text}”</p>
          {result.summary && <p className="ai-summary"><span className="badge"><Bot size={12} /> {result.engine === 'claude' ? 'Claude AI' : 'Moodify AI'}</span> {result.summary}</p>}
          <div className="result-grid">
            <div className="result-item"><span>Mood</span><strong>{cfg.icon} {cfg.label}</strong></div>
            <div className="result-item"><span>Emotion</span><strong>{result.emotion}</strong></div>
            <div className="result-item"><span>Energy</span><strong><Gauge size={14} style={{ verticalAlign: '-2px' }} /> {result.energy_level}</strong></div>
            <div className="result-item"><span>Confidence</span><strong>{Math.round(result.confidence * 100)}%</strong></div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', margin: '18px 0 28px' }}>
          <button className="solid-button" onClick={playAll} disabled={!allSongs.length}><Music2 size={16} /> Play all</button>
          {user && <button className="icon-button" style={{ width: 'auto', padding: '0 13px', display: 'inline-flex', gap: 7 }} onClick={savePlaylist} disabled={saving || !allSongs.length}>{saving ? <Loader2 size={16} className="spin" /> : <Save size={16} />} {saving ? 'Saving…' : 'Save playlist'}</button>}
        </div>

        {loading
          ? <div className="surface-card" style={{ textAlign: 'center', padding: 50 }}><Loader2 className="spin" /><p className="muted" style={{ marginTop: 8 }}>Matching tracks to the session…</p></div>
          : session?.sections?.map(section => (
            <section className="section" key={section.key} style={{ marginTop: 0, marginBottom: 28 }}>
              <div className="section-title" style={{ alignItems: 'flex-end' }}>
                <div><h3>{section.title}</h3><p className="section-sub">{section.subtitle}</p></div>
                <span className="muted" style={{ fontSize: '.75rem' }}>{section.songs.length} tracks</span>
              </div>
              <div className="song-list">
                {section.songs.map(song => <SongCard key={song.id} song={song} queue={allSongs} reason={song.reasons?.slice(0, 2).join(' · ')} isFavorite={favIds.has(song.id)} onFavoriteToggle={toggleFav} />)}
              </div>
            </section>
          ))}
        {!loading && !allSongs.length && <div className="empty-state"><strong>No songs found</strong><span>Run <code>python manage.py seed_songs</code> to load the catalog.</span></div>}
      </div>
    </main>
  )
}
