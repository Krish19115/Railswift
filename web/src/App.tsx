import { useEffect, useState, type FormEvent } from 'react'
import AuthPanel from './AuthPanel'
import {
  apiRequest,
  clearTokens,
  createSavedJourney,
  getHealth,
  getSavedJourneys,
  hasSession,
  searchStations,
  searchTrains,
  type HealthResponse,
  type SavedJourney,
  type Station,
  type TrainMatch,
} from './api'

type ConnectionState = 'checking' | 'connected' | 'unavailable'

function localDateString() {
  const date = new Date()
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000)
  return local.toISOString().slice(0, 10)
}

function StationField({ label, placeholder, value, onChange }: {
  label: string
  placeholder: string
  value: Station | null
  onChange: (station: Station | null) => void
}) {
  const [query, setQuery] = useState(value ? `${value.name} (${value.code})` : '')
  const [suggestions, setSuggestions] = useState<Station[]>([])

  useEffect(() => {
    if (value && query === `${value.name} (${value.code})`) return
    if (query.trim().length < 2) { setSuggestions([]); return }
    let current = true
    const timer = window.setTimeout(() => {
      searchStations(query.trim()).then((items) => { if (current) setSuggestions(items) }).catch(() => { if (current) setSuggestions([]) })
    }, 180)
    return () => { current = false; window.clearTimeout(timer) }
  }, [query, value])

  return (
    <label className="station-field">
      <span className="field-label">{label}</span>
      <span className="station-input-wrap">
        <span className="station-pin" aria-hidden="true">{label === 'From' ? '○' : '⌖'}</span>
        <input
          autoComplete="off"
          value={query}
          placeholder={placeholder}
          onChange={(event) => { setQuery(event.target.value); onChange(null) }}
          aria-label={label}
          aria-autocomplete="list"
        />
      </span>
      {suggestions.length > 0 && !value && <span className="station-suggestions" role="listbox">
        {suggestions.map((station) => <button
          type="button"
          role="option"
          key={station.code}
          onClick={() => { onChange(station); setQuery(`${station.name} (${station.code})`); setSuggestions([]) }}
        ><strong>{station.name}</strong><span>{station.city} · {station.code}</span></button>)}
      </span>}
    </label>
  )
}

function formatDuration(minutes: number | null) {
  if (minutes === null) return '—'
  const days = Math.floor(minutes / 1440)
  const hours = Math.floor((minutes % 1440) / 60)
  const mins = minutes % 60
  return `${days ? `${days}d ` : ''}${hours}h ${mins.toString().padStart(2, '0')}m`
}

function TrainCard({ train, onSave, saved }: { train: TrainMatch; onSave: () => void; saved: boolean }) {
  return <article className="train-result">
    <div className="train-result-head">
      <div className="train-avatar"><span>↗</span></div>
      <div><strong>{train.train.name}</strong><p>{train.train.number} <i>·</i> {train.train.is_demo ? 'Demo timetable' : 'Schedule'}</p></div>
      <span className="demo-tag">SAMPLE DATA</span>
    </div>
    <div className="route-line">
      <div><strong>{train.from.departure_time ?? '—'}</strong><span>{train.from.station}</span></div>
      <div className="route-duration"><span>{formatDuration(train.duration_minutes)}</span><i /></div>
      <div className="route-destination"><strong>{train.to.arrival_time ?? '—'}</strong><span>{train.to.station}</span></div>
    </div>
    <div className="train-result-foot"><span>{train.from.name} <b>→</b> {train.to.name}</span><button type="button" className={saved ? 'save-button is-saved' : 'save-button'} onClick={onSave}>{saved ? 'Saved ✓' : '♡ Save route'}</button></div>
  </article>
}

export default function App() {
  const [connection, setConnection] = useState<ConnectionState>('checking')
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [signedIn, setSignedIn] = useState(hasSession())
  const [profileName, setProfileName] = useState('')
  const [showAuth, setShowAuth] = useState(false)
  const [from, setFrom] = useState<Station | null>(null)
  const [to, setTo] = useState<Station | null>(null)
  const [date, setDate] = useState(localDateString())
  const [results, setResults] = useState<TrainMatch[]>([])
  const [notice, setNotice] = useState('')
  const [searchError, setSearchError] = useState('')
  const [searching, setSearching] = useState(false)
  const [searched, setSearched] = useState(false)
  const [savedJourneys, setSavedJourneys] = useState<SavedJourney[]>([])
  const [savedMessage, setSavedMessage] = useState('')

  useEffect(() => {
    let active = true
    getHealth().then((result) => {
      if (!active) return
      setHealth(result)
      setConnection(result.status === 'ok' ? 'connected' : 'unavailable')
    }).catch(() => { if (active) setConnection('unavailable') })
    return () => { active = false }
  }, [])

  useEffect(() => {
    if (!signedIn) { setSavedJourneys([]); setProfileName(''); return }
    let active = true
    Promise.all([
      apiRequest<{ username: string }>('/auth/profile/'),
      getSavedJourneys(),
    ]).then(([profile, journeys]) => {
      if (!active) return
      setProfileName(profile.username)
      setSavedJourneys(journeys)
    }).catch(() => { if (active) setSavedJourneys([]) })
    return () => { active = false }
  }, [signedIn])

  async function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSearchError('')
    setSavedMessage('')
    if (!from || !to) { setSearchError('Choose a station from each suggestion list.'); return }
    if (from.code === to.code) { setSearchError('Choose a different destination station.'); return }
    setSearching(true)
    setSearched(true)
    try {
      const response = await searchTrains(from.code, to.code, date)
      setResults(response.results)
      setNotice(response.notice)
    } catch (cause) {
      setResults([])
      setSearchError(cause instanceof Error ? cause.message : 'Train search is unavailable right now.')
    } finally { setSearching(false) }
  }

  async function saveRoute() {
    if (!from || !to) return
    if (!signedIn) { setShowAuth(true); return }
    try {
      const saved = await createSavedJourney(from.code, to.code, date)
      setSavedJourneys((current) => [saved, ...current.filter((item) => item.id !== saved.id)])
      setSavedMessage(`${from.code} to ${to.code} is in your saved journeys.`)
    } catch (cause) {
      setSavedMessage(cause instanceof Error ? cause.message : 'Unable to save this journey.')
    }
  }

  async function signOut() {
    await clearTokens()
    setSignedIn(false)
  }

  function authCompleted() {
    setSignedIn(true)
    setShowAuth(false)
  }

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="RailSwift home"><span className="brand-mark" aria-hidden="true">R</span><span>railswift</span></a>
        <nav className="topbar-nav"><a href="#search">Find a train</a><a href="#saved">Saved journeys</a></nav>
        {signedIn ? <button className="account-chip" type="button" onClick={signOut} title="Sign out"><span>{(profileName || 'K').slice(0, 1).toUpperCase()}</span>{profileName || 'Account'} <small>Sign out</small></button> : <button className="signin-button" type="button" onClick={() => setShowAuth(true)}>Sign in <span aria-hidden="true">↗</span></button>}
      </header>

      <section className="hero" aria-labelledby="welcome-title">
        <div className="hero-copy">
          <p className="eyebrow"><span className="eyebrow-dot" /> YOUR JOURNEY, THOUGHTFULLY PLANNED</p>
          <h1 id="welcome-title">A little more certainty<br />for the journey ahead.</h1>
          <p className="hero-description">Find a train, explore the route, and keep your favourite journeys close.</p>
          <a className="hero-link" href="#search">Start with a train search <span>↓</span></a>
        </div>
        <div className="journey-art" aria-label="Illustration of a railway crossing a green landscape">
          <div className="sun" /><div className="hill hill-back" /><div className="hill hill-front" /><div className="track track-one" /><div className="track track-two" />
          <div className="train-card"><span className="train-icon">↗</span><span>Ready when you are</span><span className="train-spark">✳</span></div>
          <span className="art-label label-one">A better way forward</span><span className="art-label label-two">From here to there</span>
        </div>
      </section>

      <section className="search-section" id="search" aria-labelledby="search-title">
        <div className="section-heading"><div><p className="eyebrow">YOUR NEXT JOURNEY</p><h2 id="search-title">Find your train</h2></div><span className="phase-badge">PHASE 2 · TRAIN SEARCH</span></div>
        <form className="search-form" onSubmit={submitSearch}>
          <StationField label="From" placeholder="City or station" value={from} onChange={setFrom} />
          <span className="swap-mark" aria-hidden="true">⇄</span>
          <StationField label="To" placeholder="Where to?" value={to} onChange={setTo} />
          <label className="date-field"><span className="field-label">Journey date</span><input type="date" min={localDateString()} value={date} onChange={(event) => setDate(event.target.value)} required /></label>
          <button className="search-button" type="submit" disabled={searching}>{searching ? 'Searching…' : 'Search trains'} <span aria-hidden="true">↗</span></button>
        </form>
        {searchError && <p className="form-error search-feedback" role="alert">{searchError}</p>}
        {savedMessage && <p className="success-feedback" role="status">{savedMessage}</p>}
        {searched && <div className="results-area" aria-live="polite">
          <div className="results-heading"><div><p className="eyebrow">SCHEDULE OPTIONS</p><h3>{from?.city || 'Origin'} <span>→</span> {to?.city || 'Destination'}</h3></div><span>{results.length} {results.length === 1 ? 'train' : 'trains'}</span></div>
          {notice && <p className="data-notice"><span>ⓘ</span>{notice}</p>}
          {searching ? <div className="empty-results">Looking for trains on this route…</div> : results.length ? <div className="train-results">{results.map((train) => <TrainCard key={`${train.train.number}-${train.from.station}`} train={train} onSave={saveRoute} saved={savedJourneys.some((item) => item.source_station.code === from?.code && item.destination_station.code === to?.code && item.journey_date === date)} />)}</div> : <div className="empty-results">{searchError ? 'Try again when the API is available.' : 'No sample trains found for this route yet.'}</div>}
        </div>}
      </section>

      <section className="status-row" aria-label="Project status">
        <div className="status-copy"><span className={`status-indicator ${connection}`} /><div><strong>{connection === 'connected' ? 'RailSwift API is ready' : connection === 'checking' ? 'Connecting to RailSwift…' : 'Getting things ready'}</strong><p>{connection === 'connected' ? 'Search demo routes and save journeys to your account.' : 'Make sure the API and database are running locally.'}</p></div></div>
        <div className="service-list"><span><i className={connection === 'connected' ? 'service-dot online' : 'service-dot'} /> API {connection === 'connected' ? 'online' : 'starting'}</span><span><i className={health?.database === 'ok' ? 'service-dot online' : 'service-dot'} /> Database {health?.database === 'ok' ? 'online' : 'pending'}</span></div>
      </section>

      <section className="saved-section" id="saved" aria-labelledby="saved-title">
        <div className="section-heading"><div><p className="eyebrow">KEEP THE ROUTES YOU LOVE</p><h2 id="saved-title">Saved journeys</h2></div><span className="saved-count">{signedIn ? `${savedJourneys.length} saved` : 'Your personal list'}</span></div>
        {!signedIn ? <div className="saved-empty"><span className="saved-icon">♡</span><div><strong>Your journeys, all in one place</strong><p>Sign in to save a route and find it again when you need it.</p></div><button type="button" onClick={() => setShowAuth(true)}>Sign in to save <span>↗</span></button></div> : savedJourneys.length ? <div className="saved-list">{savedJourneys.map((journey) => <article className="saved-item" key={journey.id}><span className="saved-icon">↗</span><div><strong>{journey.label || `${journey.source_station.city} to ${journey.destination_station.city}`}</strong><p>{journey.source_station.code} → {journey.destination_station.code}{journey.journey_date ? ` · ${journey.journey_date}` : ' · Favourite route'}</p></div><button type="button" className="remove-saved" title="Remove saved journey" onClick={async () => { await apiRequest(`/saved-journeys/${journey.id}/`, { method: 'DELETE' }); setSavedJourneys((items) => items.filter((item) => item.id !== journey.id)) }}>×</button></article>)}</div> : <div className="saved-empty"><span className="saved-icon">♡</span><div><strong>No saved journeys yet</strong><p>Search for a route and save it for next time.</p></div><a href="#search">Find a train <span>↗</span></a></div>}
      </section>

      <footer className="footer"><span>RAILSWIFT · BUILT FOR THE WAY AHEAD</span><span>Schedules shown here are sample data. Booking is completed by you on the official railway platform.</span></footer>
      {showAuth && <AuthPanel onComplete={authCompleted} onClose={() => setShowAuth(false)} />}
    </main>
  )
}
