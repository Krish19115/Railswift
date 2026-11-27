import { useState, type FormEvent } from 'react'
import { apiRequest, saveTokens, type Tokens } from './api'

type Props = { onComplete: () => void; onClose: () => void }

export default function AuthPanel({ onComplete, onClose }: Props) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setError('')
    const form = new FormData(event.currentTarget)
    try {
      let tokens: Tokens
      if (mode === 'register') {
        const result = await apiRequest<{ tokens: Tokens }>('/auth/register/', {
          method: 'POST',
          body: JSON.stringify({
            username: form.get('username'),
            email: form.get('email'),
            password: form.get('password'),
          }),
        })
        tokens = result.tokens
      } else {
        tokens = await apiRequest<Tokens>('/auth/login/', {
          method: 'POST',
          body: JSON.stringify({ username: form.get('identifier'), password: form.get('password') }),
        })
      }
      saveTokens(tokens)
      onComplete()
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Unable to sign in right now.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}>
      <section className="auth-panel" role="dialog" aria-modal="true" aria-labelledby="auth-title">
        <button className="auth-close" type="button" onClick={onClose} aria-label="Close sign in">×</button>
        <span className="auth-mark">R</span>
        <p className="eyebrow auth-eyebrow">YOUR RAILSWIFT ACCOUNT</p>
        <h2 id="auth-title">{mode === 'login' ? 'Welcome back.' : 'Let’s get you going.'}</h2>
        <p className="auth-intro">{mode === 'login' ? 'Sign in to keep your favourite journeys close.' : 'Create an account to save routes and journey plans.'}</p>
        <form onSubmit={submit} className="auth-form">
          {mode === 'register' ? <>
            <label>Username<input name="username" autoComplete="username" minLength={3} required /></label>
            <label>Email<input name="email" type="email" autoComplete="email" required /></label>
          </> : <label>Email or username<input name="identifier" autoComplete="username" required /></label>}
          <label>Password<input name="password" type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} minLength={8} required /></label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="primary-button auth-submit" disabled={busy} type="submit">{busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'} <span aria-hidden="true">↗</span></button>
        </form>
        <p className="auth-switch">{mode === 'login' ? 'New to RailSwift?' : 'Already have an account?'}{' '}
          <button type="button" onClick={() => { setError(''); setMode(mode === 'login' ? 'register' : 'login') }}>{mode === 'login' ? 'Create an account' : 'Sign in'}</button>
        </p>
      </section>
    </div>
  )
}
