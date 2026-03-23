'use client'
import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { useStore } from '@/stores/useStore'
import { writingApi } from '@/lib/api'
import toast from 'react-hot-toast'

export default function WritingPage() {
  const router = useRouter()
  const { profile, updateProfile } = useStore()
  const [sentence, setSentence] = useState<any>(null)
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [checking, setChecking] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [showSuccess, setShowSuccess] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => { loadSentence() }, [])

  async function loadSentence() {
    if (!profile) return
    setLoading(true); setResult(null); setAnswer('')
    try {
      const weak = profile.vocab
        .filter(w => (w.total_correct / Math.max(w.total_seen, 1)) < 0.5)
        .map(w => w.hanzi)
      const { data } = await writingApi.generateSentence(
        profile.vocab.slice(0, 22), weak, profile.lang
      )
      setSentence(data)
    } catch { toast.error('Failed to generate sentence') }
    finally { setLoading(false) }
  }

  async function playAudio(text: string) {
    try {
      const lang = /[\u4e00-\u9fff]/.test(text) ? 'zh' : 'en'
      const res = await fetch(`/api/audio/tts?text=${encodeURIComponent(text)}&lang=${lang}`)
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      if (audioRef.current) { audioRef.current.src = url; audioRef.current.play() }
    } catch {}
  }

  async function checkAnswer() {
    if (!sentence || !answer.trim()) return
    setChecking(true)
    try {
      const refs = sentence.answers?.[profile?.lang || 'en'] || []
      const { data } = await writingApi.checkAnswer(sentence.chinese, answer, refs, profile?.lang || 'en')
      setResult(data)
      if (data.correct) {
        setShowSuccess(true)
        playAudio(sentence.chinese)
        // XP gain
        const xp = data.score >= 90 ? 20 : data.score >= 75 ? 15 : 10
        updateProfile({ daily_xp: (profile?.daily_xp || 0) + xp, xp: (profile?.xp || 0) + xp })
      }
    } catch { toast.error('Check failed') }
    finally { setChecking(false) }
  }

  const lang = profile?.lang || 'en'

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg)' }}>
      <audio ref={audioRef} />

      {/* Header */}
      <header className="px-4 py-3 flex items-center gap-3"
        style={{ background: 'var(--bg-sidebar)', borderBottom: '1px solid var(--border)' }}>
        <button onClick={() => router.back()} className="text-sm px-3 py-1.5 rounded-lg hover:bg-white/10 transition-colors">
          ← Back
        </button>
        <span className="font-bold">✍️  Writing</span>
      </header>

      <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
        {/* Sentence card */}
        {loading ? (
          <div className="card p-8 text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-blue-500 mx-auto mb-3"/>
            <p style={{ color: 'var(--text-muted)' }}>Generating sentence...</p>
          </div>
        ) : sentence ? (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card p-6">
            {/* Chinese sentence */}
            <div className="text-center py-4 px-6 rounded-xl mb-4"
              style={{ background: '#0d1526', border: '1px solid #1e3a5f' }}>
              <p className="hanzi text-4xl font-bold" style={{ color: '#FFD700', lineHeight: 1.6 }}>
                {sentence.chinese}
              </p>
            </div>

            {/* Listen + Pinyin */}
            <div className="flex items-center justify-center gap-3 mb-2">
              <button onClick={() => playAudio(sentence.chinese)}
                className="flex items-center gap-2 text-sm px-3 py-1.5 rounded-lg transition-colors hover:bg-white/10"
                style={{ color: 'var(--primary)' }}>
                🔊 Listen
              </button>
            </div>
            <p className="text-center italic text-sm mb-4" style={{ color: 'var(--text-muted)' }}>
              {sentence.pinyin}
            </p>

            {/* Hover word hints */}
            {sentence.words && (
              <div className="flex flex-wrap gap-2 justify-center mb-4">
                {Object.entries(sentence.words as Record<string, any>).map(([hanzi, info]: [string, any]) => (
                  <div key={hanzi} className="group relative">
                    <span className="hanzi px-2 py-1 rounded cursor-pointer text-sm"
                      style={{ background: 'var(--bg-hover)', color: '#93c5fd' }}>
                      {hanzi}
                    </span>
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10"
                      style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text)' }}>
                      {lang === 'sr' ? info.sr : info.en}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        ) : null}

        {/* Input section */}
        {sentence && !showSuccess && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-3">
            <label className="text-xs font-semibold" style={{ color: 'var(--text-muted)' }}>
              {lang === 'sr' ? 'PREVOD:' : 'ENGLISH TRANSLATION:'}
            </label>
            <textarea
              ref={inputRef}
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              onKeyDown={e => { if (e.ctrlKey && e.key === 'Enter') checkAnswer() }}
              placeholder={lang === 'sr' ? 'Unesite prevod...' : 'Enter translation...'}
              rows={3}
              className="w-full rounded-xl p-4 resize-none text-sm transition-all outline-none"
              style={{
                background: '#1a2235',
                border: '1.5px solid',
                borderColor: result ? (result.correct ? '#22c55e' : '#ef4444') : '#2a3a5a',
                color: 'var(--text)',
                boxShadow: result ? undefined : 'none',
              }}
              autoFocus
            />

            {/* Result feedback */}
            <AnimatePresence>
              {result && !result.correct && (
                <motion.div initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }}
                  className="rounded-xl p-4" style={{ background: '#1a0a0a', border: '1px solid #7f1d1d' }}>
                  <p className="font-bold text-sm" style={{ color: '#ef4444' }}>
                    {result.feedback || 'Incorrect.'}
                  </p>
                  {result.suggestion && (
                    <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                      ✓ {result.suggestion}
                    </p>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            <div className="flex gap-3">
              <button onClick={checkAnswer} disabled={checking || !answer.trim()} className="btn-success flex-1 py-3">
                {checking ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                    </svg>
                    🤖 Checking...
                  </span>
                ) : '✔  Check'}
              </button>
              <button onClick={loadSentence}
                className="px-6 py-3 rounded-lg text-sm font-medium transition-colors"
                style={{ background: 'var(--bg-card)', color: 'var(--text-muted)', border: '1px solid var(--border)' }}>
                Skip
              </button>
            </div>
          </motion.div>
        )}

        {/* Success overlay */}
        <AnimatePresence>
          {showSuccess && (
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="rounded-2xl p-8 text-center"
              style={{ background: '#0a1f10', border: '2px solid #22c55e' }}>
              <div className="text-5xl mb-3">🎉</div>
              <p className="text-xl font-bold" style={{ color: '#22c55e' }}>
                {result?.score >= 90 ? 'Perfect! ✓' : result?.score >= 75 ? 'Great! Same meaning ✓' : 'Accepted! Close enough ✓'}
              </p>
              <p className="text-sm mt-2 mb-6" style={{ color: 'var(--text-muted)' }}>
                Score: {result?.score}/100
              </p>
              <button onClick={() => { setShowSuccess(false); loadSentence() }} className="btn-primary px-8 py-3">
                Next Sentence →
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
