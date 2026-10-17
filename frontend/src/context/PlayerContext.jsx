import { createContext, useContext, useState, useRef, useCallback, useEffect } from 'react'
import api from '../services/api'
import { useToast } from './ToastContext'

const PlayerContext = createContext(null)

// Loads the official YouTube IFrame API once.
let ytApiPromise = null
function loadYouTubeApi() {
  if (window.YT?.Player) return Promise.resolve(window.YT)
  if (!ytApiPromise) {
    ytApiPromise = new Promise((resolve, reject) => {
      const previous = window.onYouTubeIframeAPIReady
      window.onYouTubeIframeAPIReady = () => { previous?.(); resolve(window.YT) }
      const script = document.createElement('script')
      script.src = 'https://www.youtube.com/iframe_api'
      script.onerror = () => { ytApiPromise = null; reject(new Error('YouTube player could not load')) }
      document.head.appendChild(script)
    })
  }
  return ytApiPromise
}

export function PlayerProvider({ children }) {
  const { showToast } = useToast()
  const [queue, setQueue] = useState([])
  const [currentIndex, setCurrentIndex] = useState(-1)
  const [isPlaying, setIsPlaying] = useState(false)
  const [loadingTrack, setLoadingTrack] = useState(false)
  const [playback, setPlayback] = useState(null)     // { source: 'youtube' | 'preview' | 'none', ... }
  const [progress, setProgress] = useState(0)
  const [clipSeconds, setClipSeconds] = useState(0)
  const [volume, setVolume] = useState(0.7)
  const [shuffle, setShuffle] = useState(false)
  const [repeat, setRepeat] = useState('off')
  const [showVideo, setShowVideo] = useState(false)
  const audioRef = useRef(null)
  const ytRef = useRef(null)
  const ytReadyRef = useRef(false)
  const pendingVideoRef = useRef(null)
  const latest = useRef({})

  const currentSong = currentIndex >= 0 ? queue[currentIndex] : null
  const source = playback?.source || null

  const playQueue = useCallback((songs, startIndex = 0) => {
    if (!songs || songs.length === 0) return
    setQueue(songs); setCurrentIndex(Math.max(0, startIndex)); setIsPlaying(true)
  }, [])
  const play = useCallback(() => setIsPlaying(true), [])
  const pause = useCallback(() => setIsPlaying(false), [])

  const next = useCallback(() => {
    setCurrentIndex(prev => {
      if (shuffle && queue.length > 1) { let r; do { r = Math.floor(Math.random() * queue.length) } while (r === prev); return r }
      if (prev >= queue.length - 1) return repeat === 'all' ? 0 : prev
      return prev + 1
    })
    setIsPlaying(true)
  }, [shuffle, queue.length, repeat])
  const prev = useCallback(() => { setCurrentIndex(p => (p <= 0 ? queue.length - 1 : p - 1)); setIsPlaying(true) }, [queue.length])
  const stop = useCallback(() => { setQueue([]); setCurrentIndex(-1); setIsPlaying(false); setProgress(0); setPlayback(null) }, [])
  const toggleShuffle = useCallback(() => setShuffle(s => !s), [])
  const cycleRepeat = useCallback(() => setRepeat(r => (r === 'off' ? 'all' : r === 'all' ? 'one' : 'off')), [])
  const toggleVideo = useCallback(() => setShowVideo(v => !v), [])

  const seek = useCallback((percent) => {
    if (source === 'youtube' && ytRef.current?.getDuration) {
      ytRef.current.seekTo((percent / 100) * ytRef.current.getDuration(), true)
      setProgress(percent)
    } else if (audioRef.current?.duration) {
      audioRef.current.currentTime = (percent / 100) * audioRef.current.duration
      setProgress(percent)
    }
  }, [source])

  // What to do when a track finishes.
  const handleEnded = useCallback(() => {
    const { repeat: rep, currentIndex: idx, queue: q, source: src } = latest.current
    if (rep === 'one') {
      if (src === 'youtube') { ytRef.current?.seekTo(0, true); ytRef.current?.playVideo() }
      else if (audioRef.current) { audioRef.current.currentTime = 0; audioRef.current.play().catch(() => {}) }
      return
    }
    if (idx >= q.length - 1 && rep === 'off') { setIsPlaying(false); setProgress(0); return }
    next()
  }, [next])
  latest.current = { repeat, currentIndex, queue, source, handleEnded, isPlaying, volume, showToast }

  // 1) A new song was chosen: ask the backend what to play (YouTube id and/or 30s preview).
  useEffect(() => {
    if (!currentSong) return
    let cancelled = false
    setPlayback(null); setProgress(0); setClipSeconds(0); setLoadingTrack(true)
    api.get(`/songs/${currentSong.id}/playback/`)
      .then(({ data }) => { if (!cancelled) setPlayback(data) })
      .catch(() => { if (!cancelled) setPlayback({ source: 'none', external_url: currentSong.external_url }) })
      .finally(() => { if (!cancelled) setLoadingTrack(false) })
    return () => { cancelled = true }
  }, [currentSong?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  // 2) Create the YouTube player on demand.
  const ensureYouTube = useCallback(async () => {
    if (ytRef.current) return ytRef.current
    const YT = await loadYouTubeApi()
    return new Promise(resolve => {
      ytRef.current = new YT.Player('moodify-yt-player', {
        width: '356', height: '200',
        playerVars: { playsinline: 1, controls: 1, rel: 0, modestbranding: 1, origin: window.location.origin },
        events: {
          onReady: () => {
            ytReadyRef.current = true
            ytRef.current.setVolume(latest.current.volume * 100)
            if (pendingVideoRef.current) { ytRef.current.loadVideoById(pendingVideoRef.current); pendingVideoRef.current = null }
            resolve(ytRef.current)
          },
          onStateChange: (e) => { if (e.data === 0) latest.current.handleEnded() },
          onError: () => {
            // Video blocked from embedding or removed: use the 30-second preview if we have one, else skip.
            setPlayback(p => {
              if (p?.preview_url) return { ...p, source: 'preview' }
              latest.current.showToast("Couldn't play that track here. Skipping.", 'warning')
              setTimeout(() => latest.current.handleEnded(), 0)
              return { ...p, source: 'none' }
            })
          },
        },
      })
    })
  }, [])

  // 3) Start the right engine when the playback info arrives.
  useEffect(() => {
    if (!playback) return
    const audio = audioRef.current
    if (playback.source === 'youtube') {
      audio?.pause()
      ensureYouTube().then(yt => {
        if (ytReadyRef.current) yt.loadVideoById(playback.youtube_id)
        else pendingVideoRef.current = playback.youtube_id
        if (!latest.current.isPlaying) yt.pauseVideo?.()
      }).catch(() => {
        setPlayback(p => (p?.preview_url ? { ...p, source: 'preview' } : { ...p, source: 'none' }))
      })
    } else if (playback.source === 'preview') {
      ytRef.current?.stopVideo?.()
      if (audio) {
        audio.src = playback.preview_url
        if (latest.current.isPlaying) audio.play().catch(() => {})
      }
    } else if (playback.source === 'none') {
      ytRef.current?.stopVideo?.(); audioRef.current?.pause()
      const { showToast: toast, queue: q } = latest.current
      if (q.length > 1) { toast('No audio found for that track. Skipping.', 'info'); setTimeout(() => latest.current.handleEnded(), 300) }
      else {
        toast('No audio found for that track.', 'info')
        setIsPlaying(false)
      }
    }
  }, [playback, ensureYouTube])

  // 4) Play / pause.
  useEffect(() => {
    if (!playback) return
    if (playback.source === 'youtube' && ytReadyRef.current) {
      isPlaying ? ytRef.current.playVideo() : ytRef.current.pauseVideo()
    } else if (playback.source === 'preview' && audioRef.current) {
      isPlaying ? audioRef.current.play().catch(() => {}) : audioRef.current.pause()
    }
  }, [isPlaying, playback])

  // 5) Progress bar.
  useEffect(() => {
    const timer = setInterval(() => {
      if (source === 'youtube' && ytReadyRef.current && ytRef.current?.getDuration) {
        const d = ytRef.current.getDuration()
        if (d) { setClipSeconds(d); setProgress((ytRef.current.getCurrentTime() / d) * 100) }
      } else if (source === 'preview' && audioRef.current?.duration) {
        setClipSeconds(audioRef.current.duration)
        setProgress((audioRef.current.currentTime / audioRef.current.duration) * 100)
      }
    }, 400)
    return () => clearInterval(timer)
  }, [source])

  // 6) Volume.
  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume
    if (ytReadyRef.current) ytRef.current?.setVolume?.(volume * 100)
  }, [volume])

  const videoVisible = source === 'youtube' && showVideo

  return (
    <PlayerContext.Provider value={{ currentSong, queue, currentIndex, isPlaying, loadingTrack, source, progress, clipSeconds, volume, shuffle, repeat, showVideo, playQueue, play, pause, next, prev, stop, seek, setVolume, toggleShuffle, cycleRepeat, toggleVideo }}>
      {children}
      <audio ref={audioRef} onEnded={handleEnded} />
      <div className={`yt-panel ${videoVisible ? '' : 'is-hidden'}`} aria-hidden={!videoVisible}>
        <div id="moodify-yt-player" />
      </div>
    </PlayerContext.Provider>
  )
}

export function usePlayer() {
  const ctx = useContext(PlayerContext)
  if (!ctx) throw new Error('usePlayer must be used within PlayerProvider')
  return ctx
}
