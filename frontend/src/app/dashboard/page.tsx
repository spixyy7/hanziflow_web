'use client'
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { useStore } from '@/stores/useStore'
import { profileApi, coachApi } from '@/lib/api'
import { XPBar } from '@/components/ui/XPBar'
import { StreakCard } from '@/components/ui/StreakCard'
import { DailyXPChart } from '@/components/ui/DailyXPChart'
import { NavButton } from '@/components/layout/NavButton'
import type { UserProfile } from '@/types'

const MODES = [
  { id: 'quiz',       label: 'Quiz',       icon: '🧠', color: '#3b82f6', desc: 'Flashcard quiz' },
  { id: 'writing',    label: 'Writing',    icon: '✍️',  color: '#8b5cf6', desc: 'Translate sentences' },
  { id: 'grammar',    label: 'Grammar',    icon: '📝',  color: '#f59e0b', desc: 'Build sentences' },
  { id: 'speaking',   label: 'Speaking',   icon: '🎤',  color: '#ec4899', desc: 'Pronunciation' },
  { id: 'arena',      label: 'Arena',      icon: '⚔️',  color: '#ef4444', desc: 'Word battle' },
  { id: 'mistakes',   label: 'Mistakes',   icon: '📋',  color: '#64748b', desc: 'Review errors' },
  { id: 'leaderboard',label: 'Leaderboard',icon: '🏆',  color: '#ffd700', desc: 'Rankings' },
  { id: 'add-words',  label: 'Add Words',  icon: '📖',  color: '#22c55e', desc: 'Expand vocabulary' },
]

export default function DashboardPage() {
  const router = useRouter()
  const { profile, token, setProfile, logout } = useStore()
  const [coachMsg, setCoachMsg] = useState<string | null>(null)

  useEffect(() => {
    if (!token) { router.push('/auth'); return }
    profileApi.get().then(r => setProfile(r.data)).catch(() => { logout(); router.push('/auth') })
  }, [])

  useEffect(() => {
    if (!profile) return
    // AI Coach check once per day
    const today = new Date().toISOString().slice(0, 10)
    if (profile.last_goal_check !== today) {
      coachApi.check(profile.daily_goal, profile.daily_xp_history)
        .then(r => { if (r.data?.message) setCoachMsg(r.data.message) })
        .catch(() => {})
    }
  }, [profile?.username])

  if (!profile) return <div className="min-h-screen flex items-center justify-center">
    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-blue-500"/>
  </div>

  const { xp, level, streak, daily_xp, daily_goal, arena_score } = profile
  const rank = getRank(arena_score)
  const xpForNext = xpForLevel(level + 1)
  const xpForCurrent = xpForLevel(level)
  const xpPct = Math.min(100, ((xp - xpForCurrent) / (xpForNext - xpForCurrent)) * 100)

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg)' }}>
      {/* Header */}
      <header className="sticky top-0 z-40 px-4 py-3 flex items-center gap-3"
        style={{ background: 'var(--bg-sidebar)', borderBottom: '1px solid var(--border)' }}>
        <span className="text-2xl">🐉</span>
        <span className="font-bold text-lg">HanziFlow</span>
        <div className="flex-1"/>

        {/* Streak */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
          <span className="streak-fire">🔥</span>
          <span className="font-bold text-sm" style={{ color: '#f59e0b' }}>{streak}</span>
        </div>

        {/* XP */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
          <span>⚡</span>
          <span className="font-bold text-sm text-yellow-400">{xp.toLocaleString()}</span>
        </div>

        {/* Avatar */}
        <button onClick={() => router.push('/profile')}
          className="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm"
          style={{ background: 'var(--primary)', color: 'white' }}>
          {profile.avatar_url
            ? <img src={profile.avatar_url} className="w-full h-full rounded-full object-cover" />
            : profile.username[0].toUpperCase()}
        </button>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {/* AI Coach message */}
        {coachMsg && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
            className="rounded-xl p-4 flex items-start gap-3"
            style={{ background: '#0d2040', border: '1px solid #1e3a5f' }}>
            <span className="text-2xl">🤖</span>
            <div>
              <p className="text-sm font-medium text-blue-300">AI Coach</p>
              <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>{coachMsg}</p>
            </div>
            <button onClick={() => setCoachMsg(null)} className="ml-auto text-gray-600 hover:text-gray-400">✕</button>
          </motion.div>
        )}

        {/* Stats row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatCard icon="📊" label="Level" value={`${level}`} sub={rank.name} color={rank.color} />
          <StatCard icon="🔥" label="Streak" value={`${streak} days`} sub={`Best: ${profile.longest_streak}`} color="#f59e0b" />
          <StatCard icon="🎯" label="Daily XP" value={`${daily_xp}/${daily_goal}`}
            sub={daily_xp >= daily_goal ? '✅ Goal met!' : `${daily_goal - daily_xp} XP to go`}
            color={daily_xp >= daily_goal ? '#22c55e' : '#3b82f6'} />
          <StatCard icon="⚔️" label="Arena" value={arena_score.toLocaleString()} sub={rank.icon + ' ' + rank.name} color={rank.color} />
        </div>

        {/* XP Progress bar */}
        <div className="card p-4">
          <div className="flex justify-between text-xs mb-2" style={{ color: 'var(--text-muted)' }}>
            <span>Level {level}</span>
            <span>{xp.toLocaleString()} / {xpForNext.toLocaleString()} XP</span>
            <span>Level {level + 1}</span>
          </div>
          <div className="xp-bar">
            <motion.div className="xp-bar-fill" initial={{ width: 0 }}
              animate={{ width: `${xpPct}%` }} transition={{ duration: 0.6, ease: 'easeOut' }} />
          </div>
        </div>

        {/* Daily XP chart */}
        <DailyXPChart history={profile.daily_xp_history} goal={daily_goal} />

        {/* Mode grid */}
        <div>
          <h2 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>
            PRACTICE MODES
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {MODES.map((m, i) => (
              <motion.button key={m.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => router.push(`/${m.id}`)}
                className="card p-4 text-left hover:scale-[1.02] transition-transform cursor-pointer group"
                style={{ borderColor: 'var(--border)' }}>
                <div className="text-3xl mb-2">{m.icon}</div>
                <div className="font-semibold text-sm">{m.label}</div>
                <div className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{m.desc}</div>
                <div className="mt-2 h-0.5 rounded-full w-0 group-hover:w-full transition-all duration-300"
                  style={{ background: m.color }} />
              </motion.button>
            ))}
          </div>
        </div>

        {/* Vocab count */}
        <div className="text-center pb-4">
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            📚 {profile.vocab.length} words in your vocabulary
          </p>
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, sub, color }: any) {
  return (
    <div className="card p-4">
      <div className="text-xl mb-1">{icon}</div>
      <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{label}</div>
      <div className="font-bold text-lg" style={{ color }}>{value}</div>
      <div className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{sub}</div>
    </div>
  )
}

function getRank(score: number) {
  const RANKS = [
    { name: 'Word Rookie',     min: 0,     color: '#CD7F32', icon: '🥉' },
    { name: 'Stroke Student',  min: 500,   color: '#A8A9AD', icon: '⚔️' },
    { name: 'Hanzi Hunter',    min: 1500,  color: '#FFD700', icon: '🥇' },
    { name: 'Sentence Master', min: 4000,  color: '#50C8FF', icon: '💠' },
    { name: 'Fluency King',    min: 10000, color: '#B44FE8', icon: '👑' },
    { name: 'Dragon Scholar',  min: 25000, color: '#FF4F4F', icon: '🐉' },
  ]
  return RANKS.filter(r => score >= r.min).at(-1) || RANKS[0]
}

function xpForLevel(level: number) {
  return Math.floor(100 * Math.pow(level - 1, 1.6))
}
