'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { authApi } from '@/lib/api'
import { useStore } from '@/stores/useStore'
import toast from 'react-hot-toast'

export default function AuthPage() {
  const router = useRouter()
  const { setToken, setProfile } = useStore()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '' })

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      if (mode === 'register') {
        if (form.password !== form.confirm) { toast.error('Passwords do not match'); return }
        await authApi.register(form.username, form.email, form.password)
        toast.success('Account created!')
        setMode('login')
        return
      }
      const { data } = await authApi.login(form.username, form.password)
      setToken(data.token)
      setProfile(data.profile)
      router.push('/dashboard')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'var(--bg)' }}>
      {/* Background glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] rounded-full opacity-10"
          style={{ background: 'radial-gradient(circle, #3b82f6, transparent)' }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🐉</div>
          <h1 className="text-3xl font-bold text-white">HanziFlow</h1>
          <p className="mt-1" style={{ color: 'var(--text-muted)' }}>Learn Chinese with AI</p>
        </div>

        {/* Card */}
        <div className="card p-8">
          {/* Tabs */}
          <div className="flex mb-6 gap-1 p-1 rounded-lg" style={{ background: 'var(--bg)' }}>
            {(['login', 'register'] as const).map(m => (
              <button key={m} onClick={() => setMode(m)}
                className="flex-1 py-2 rounded-md text-sm font-medium transition-all"
                style={{
                  background: mode === m ? 'var(--bg-card)' : 'transparent',
                  color: mode === m ? 'white' : 'var(--text-muted)',
                  border: mode === m ? '1px solid var(--border)' : 'none',
                }}>
                {m === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            ))}
          </div>

          <form onSubmit={submit} className="space-y-4">
            <AnimatePresence mode="wait">
              <motion.div key={mode} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                <div>
                  <label className="text-xs mb-1 block" style={{ color: 'var(--text-muted)' }}>Username</label>
                  <input className="input-base" placeholder="spasoje" value={form.username}
                    onChange={e => set('username', e.target.value)} required autoFocus />
                </div>

                {mode === 'register' && (
                  <div>
                    <label className="text-xs mb-1 block" style={{ color: 'var(--text-muted)' }}>Email</label>
                    <input className="input-base" type="email" placeholder="you@example.com"
                      value={form.email} onChange={e => set('email', e.target.value)} required />
                  </div>
                )}

                <div>
                  <label className="text-xs mb-1 block" style={{ color: 'var(--text-muted)' }}>Password</label>
                  <input className="input-base" type="password" placeholder="••••••••"
                    value={form.password} onChange={e => set('password', e.target.value)} required />
                </div>

                {mode === 'register' && (
                  <div>
                    <label className="text-xs mb-1 block" style={{ color: 'var(--text-muted)' }}>Confirm Password</label>
                    <input className="input-base" type="password" placeholder="••••••••"
                      value={form.confirm} onChange={e => set('confirm', e.target.value)} required />
                  </div>
                )}
              </motion.div>
            </AnimatePresence>

            <button type="submit" className="btn-primary w-full mt-2" disabled={loading}>
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                  </svg>
                  {mode === 'login' ? 'Signing in...' : 'Creating account...'}
                </span>
              ) : (
                mode === 'login' ? 'Sign In' : 'Create Account'
              )}
            </button>
          </form>
        </div>

        <p className="text-center mt-4 text-xs" style={{ color: 'var(--text-muted)' }}>
          HanziFlow v1.0 • AI-powered Chinese learning
        </p>
      </motion.div>
    </div>
  )
}
