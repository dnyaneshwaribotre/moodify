import { useEffect, useRef, useState } from 'react'
import { ArrowRight, Loader2, Mic, Sparkles } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { analyzeMood } from '../services/backendApi'
import { saveMoodAnalysis } from '../services/userService'
import { useToast } from '../context/ToastContext'
import { QUICK_MOODS, MOOD_CONFIG, LANGUAGE_CHOICES } from '../utils/constants'

export default function MoodInput() {
  const { showToast } = useToast()
  const navigate = useNavigate()
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [listening, setListening] = useState(false)
  const [language, setLanguage] = useState('indian')
  const recognitionRef = useRef(null)
  const SpeechRecognition = typeof window !== 'undefined' ? (window.SpeechRecognition || window.webkitSpeechRecognition) : null

  useEffect(() => () => recognitionRef.current?.stop(), [])

  // AI tool: speak your mood (browser speech recognition - works in Chrome/Edge/Safari)
  function toggleVoice() {
    if (!SpeechRecognition) { showToast('Voice input is not supported in this browser. Try Chrome or Edge.', 'info'); return }
    if (listening) { recognitionRef.current?.stop(); return }
    const recognition = new SpeechRecognition()
    recognition.lang = navigator.language || 'en-IN'
    recognition.interimResults = false
    recognition.onresult = event => setText(prev => `${prev} ${event.results[0][0].transcript}`.trim())
    recognition.onerror = () => showToast('Could not hear you. Check microphone permission.', 'warning')
    recognition.onend = () => setListening(false)
    recognitionRef.current = recognition
    setListening(true)
    recognition.start()
  }

  async function handleAnalyze(value = text) {
    if (!value.trim()) { showToast('Tell us a little about your mood first.', 'warning'); return }
    setLoading(true)
    try {
      const result = await analyzeMood(value)
      try {
        await saveMoodAnalysis({
          input_text: value,
          detected_emotion: result.emotion,
          detected_mood: result.mood,
          energy_level: result.energy_level,
          confidence: result.confidence,
        })
      } catch { /* history is non-blocking */ }
      navigate('/ai-result', { state: { text: value, ...result, language_choice: language } })
    } catch {
      showToast('Could not analyze that mood. Please try again.', 'error')
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <div className="page-narrow">
        <div className="page-head">
          <div>
            <span className="eyebrow"><Sparkles size={13}/> Mood studio</span>
            <h1 style={{margin:'8px 0 10px', fontSize:'clamp(2.5rem,7vw,4.7rem)'}}>What should this moment sound like?</h1>
            <p>Use your own words. Short, specific context usually gives the clearest result.</p>
          </div>
        </div>

        <div className="surface-card">
          <textarea className="mood-input" maxLength={2000} value={text} onChange={e=>setText(e.target.value)} disabled={loading} placeholder="e.g. I had a long day and want something warm, quiet and a little nostalgic…" />
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:12,marginTop:12}}>
            <span className="muted" style={{fontSize:'.72rem'}}>{text.length}/2000</span>
            <span style={{display:'flex',gap:8}}>
            <button type="button" className={`icon-button ${listening ? 'mic-active' : ''}`} onClick={toggleVoice} disabled={loading} aria-label={listening ? 'Stop listening' : 'Speak your mood'} title="Speak your mood"><Mic size={16}/></button>
            <button className="solid-button" onClick={()=>handleAnalyze()} disabled={loading || !text.trim()}>
              {loading ? <><Loader2 size={16} className="spin"/> Reading…</> : <>Build my session <ArrowRight size={16}/></>}
            </button>
            </span>
          </div>
          <div className="chips">
            {QUICK_MOODS.map(item => {
              const cfg = MOOD_CONFIG[item.mood] || {}
              return <button className="chip" key={item.mood} onClick={()=>{setText(item.text); handleAnalyze(item.text)}} disabled={loading}>{cfg.icon} {cfg.label}</button>
            })}
          </div>
        </div>

        <div className="section">
          <div className="eyebrow">Song language</div>
          <div className="chips">
            {LANGUAGE_CHOICES.map(item => <button key={item.key} className="chip" style={language===item.key?{borderColor:'var(--accent)',color:'var(--accent)'}:{}} onClick={()=>setLanguage(item.key)}>{item.label}</button>)}
          </div>
        </div>

        <div className="section">
          <div className="eyebrow">Try a prompt</div>
          <div className="chips">
            {[
              'I need calm music after a stressful workday.',
              'I am getting ready for a lively evening with friends.',
              'I feel nostalgic and want something familiar.',
              'I need focused music for a long study session.',
              'Play some famous old Hindi songs, I feel nostalgic.',
              'Latest trending Marathi songs for a party!',
              'aaj bahut udaas hoon 😢',
            ].map(example => <button className="chip" key={example} onClick={()=>setText(example)}>{example}</button>)}
          </div>
        </div>
      </div>
    </main>
  )
}
