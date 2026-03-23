// types/index.ts — Matching Python models exactly

export interface Word {
  hanzi: string
  pinyin: string
  meaning_sr: string
  meaning_en: string
  xp: number
  interval: number
  step: number
  ease: number
  next_review: string
  total_seen: number
  total_correct: number
  consecutive_wrong: number
  avg_response_time: number
}

export interface Mistake {
  type: 'word' | 'sentence'
  hanzi: string
  pinyin: string
  meaning_sr: string
  meaning_en: string
  xp: number
  correct: string
  scrambled: string
  count: number
  last_seen: string
}

export interface UserProfile {
  id: string
  username: string
  email: string
  xp: number
  level: number
  streak: number
  daily_xp: number
  last_date: string
  daily_goal: number
  goal_setup_done: boolean
  completed_days: string[]
  daily_xp_history: Record<string, number>
  vocab: Word[]
  mistakes: { words: Mistake[]; sentences: Mistake[] }
  lang: 'en' | 'sr'
  arena_score: number
  total_correct: number
  total_answered: number
  grammar_completed: number
  achievements: string[]
  audio_enabled: boolean
  theme: 'light' | 'dark' | 'system'
  longest_streak: number
  streak_shields: number
  avatar_url: string
  show_rank: boolean
  show_nickname: boolean
  preferred_quiz_modes: Record<string, number>
  streak_earned_today: string
}

export interface Achievement {
  id: string
  name: string
  desc: string
  icon: string
  xp: number
  hidden: boolean
}

export interface Rank {
  name: string
  min_score: number
  color: string
  icon: string
}

export type QuizMode = 'type' | 'draw' | 'listen' | 'meaning'
export type Lang = 'en' | 'sr'

export interface SessionStats {
  total: number
  correct: number
  xp_gained: number
  response_times: number[]
  start_time: string
}

export interface LeaderboardEntry {
  username: string
  xp: number
  level: number
  streak: number
  arena_score: number
  rank: Rank
  avatar_url: string
}
