import { useEffect, useState } from 'react'
import { getHealth, type HealthResponse } from './api'

type ConnectionState = 'checking' | 'connected' | 'unavailable'

export default function App() {
  const [connection, setConnection] = useState<ConnectionState>('checking')
  const [health, setHealth] = useState<HealthResponse | null>(null)

  useEffect(() => {
    let active = true
    getHealth()
      .then((result) => {
        if (!active) return
        setHealth(result)
        setConnection(result.status === 'ok' ? 'connected' : 'unavailable')
      })
      .catch(() => {
        if (active) setConnection('unavailable')
      })
    return () => {
      active = false
    }
  }, [])

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="RailSwift home">
          <span className="brand-mark" aria-hidden="true">R</span>
          <span>railswift</span>
        </a>
        <span className="topbar-note">A clearer way to plan your rail journey</span>
        <button className="profile-button" type="button" aria-label="Profile">K</button>
      </header>

      <section className="hero" aria-labelledby="welcome-title">
        <div className="hero-copy">
          <p className="eyebrow"><span className="eyebrow-dot" /> YOUR JOURNEY, THOUGHTFULLY PLANNED</p>
          <h1 id="welcome-title">A little more certainty<br />for the journey ahead.</h1>
          <p className="hero-description">
            Find the right train, understand your options, and feel ready when it is time to book.
          </p>
          <button className="primary-button" type="button" disabled>
            Plan a journey <span aria-hidden="true">↗</span>
          </button>
          <p className="coming-note">Journey search arrives in the next phase</p>
        </div>
        <div className="journey-art" aria-label="Illustration of a railway crossing a green landscape">
          <div className="sun" />
          <div className="hill hill-back" />
          <div className="hill hill-front" />
          <div className="track track-one" />
          <div className="track track-two" />
          <div className="train-card"><span className="train-icon">↗</span><span>Ready when you are</span><span className="train-spark">✳</span></div>
          <span className="art-label label-one">A better way forward</span>
          <span className="art-label label-two">From here to there</span>
        </div>
      </section>

      <section className="status-row" aria-label="Project status">
        <div className="status-copy">
          <span className={`status-indicator ${connection}`} />
          <div>
            <strong>{connection === 'connected' ? 'Your RailSwift foundation is ready' : connection === 'checking' ? 'Connecting to RailSwift…' : 'Getting things ready'}</strong>
            <p>{connection === 'connected' ? 'The shared API is responding.' : 'Journey search and live railway data will arrive in upcoming phases.'}</p>
          </div>
        </div>
        <div className="service-list">
          <span><i className={connection === 'connected' ? 'service-dot online' : 'service-dot'} /> API {connection === 'connected' ? 'online' : 'starting'}</span>
          <span><i className={health?.database === 'ok' ? 'service-dot online' : 'service-dot'} /> Database {health?.database === 'ok' ? 'online' : 'pending'}</span>
        </div>
      </section>

      <footer className="footer"><span>RAILSWIFT · BUILT FOR THE WAY AHEAD</span><span>Booking is always completed by you on the official railway platform.</span></footer>
    </main>
  )
}
