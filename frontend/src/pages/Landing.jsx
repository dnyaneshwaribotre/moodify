import { ArrowRight, Compass, Heart, Headphones, Music2, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'

const tracks = [
  ['01', 'Tum Hi Ho', 'Arijit Singh · trending', '96%'],
  ['02', 'Lag Jaa Gale', 'Lata Mangeshkar · classic', '93%'],
  ['03', 'Die With A Smile', 'Lady Gaga & Bruno Mars · trending', '91%'],
  ['04', 'Hotel California', 'Eagles · classic', '88%'],
]

export default function Landing() {
  return (
    <main>
      <section className="hero">
        <div className="shell hero-grid">
          <div className="hero-copy">
            <span className="eyebrow"><Headphones size={13} /> Music that meets you where you are</span>
            <h1>Listen to the mood, not the algorithm.</h1>
            <p>
              Describe how your day feels. Moodify turns that context into a focused
              music session, with recommendations shaped by your preferences and listening history.
            </p>
            <div className="hero-actions">
              <Link to="/register" className="solid-button">Start a session <ArrowRight size={17} /></Link>
              <Link to="/login" className="text-button">I already have an account</Link>
            </div>
            <p className="hero-note">Trending hits and famous old songs · AI mood analysis · voice input · playlists you can keep</p>
          </div>

          <div className="hero-panel">
            <div className="eyebrow">A sample session</div>
            {tracks.map(([n, title, artist, score]) => (
              <div className="signal" key={n}>
                <span className="signal-index">{n}</span>
                <div className="signal-art"><Music2 size={17} /></div>
                <div>
                  <strong>{title}</strong>
                  <span>{artist}</span>
                </div>
                <span className="signal-score">{score}</span>
              </div>
            ))}
            <div style={{paddingTop:14, color:'var(--muted)', fontSize:'.76rem'}}>
              Built for intentional listening — not endless scrolling.
            </div>
          </div>
        </div>
      </section>

      <section className="shell section" style={{paddingBottom:90}}>
        <div className="eyebrow">The essentials</div>
        <div className="quick-grid">
          <div className="quick-card"><Compass size={18}/><strong>Mood studio</strong><span>Turn a feeling into a session.</span></div>
          <div className="quick-card"><TrendingUp size={18}/><strong>Trending</strong><span>See what is moving right now.</span></div>
          <div className="quick-card"><Heart size={18}/><strong>Saved</strong><span>Keep the tracks worth returning to.</span></div>
          <div className="quick-card"><Headphones size={18}/><strong>History</strong><span>Pick up where you left off.</span></div>
        </div>
      </section>
    </main>
  )
}
