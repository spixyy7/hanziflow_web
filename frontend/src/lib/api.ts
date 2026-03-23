// lib/api.ts — All API calls to FastAPI backend
import axios from 'axios'
import { useStore } from '@/stores/useStore'

const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({ baseURL: BASE })

api.interceptors.request.use((cfg) => {
  const token = useStore.getState().token
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) useStore.getState().logout()
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  register: (username: string, email: string, password: string) =>
    api.post('/auth/register', { username, email, password }),
  me: () => api.get('/auth/me'),
}

// ── Profile ───────────────────────────────────────────────────────────────────
export const profileApi = {
  get: () => api.get('/profile'),
  update: (data: object) => api.patch('/profile', data),
  uploadAvatar: (file: File) => {
    const fd = new FormData(); fd.append('file', file)
    return api.post('/profile/avatar', fd)
  },
}

// ── Vocabulary ────────────────────────────────────────────────────────────────
export const vocabApi = {
  list: () => api.get('/vocab'),
  add: (word: object) => api.post('/vocab', word),
  update: (hanzi: string, data: object) => api.patch(`/vocab/${hanzi}`, data),
  delete: (hanzi: string) => api.delete(`/vocab/${hanzi}`),
  extractFromFile: (file: File) => {
    const fd = new FormData(); fd.append('file', file)
    return api.post('/vocab/extract', fd)
  },
}

// ── Quiz ──────────────────────────────────────────────────────────────────────
export const quizApi = {
  getWords: (mode: string, count?: number) =>
    api.get('/quiz/words', { params: { mode, count } }),
  submitAnswer: (data: object) => api.post('/quiz/answer', data),
  sessionFeedback: (stats: object) => api.post('/quiz/feedback', stats),
}

// ── Writing ───────────────────────────────────────────────────────────────────
export const writingApi = {
  getSentences: () => api.get('/writing/sentences'),
  checkAnswer: (chinese: string, answer: string, refs: string[], lang: string) =>
    api.post('/writing/check', { chinese, answer, reference_answers: refs, lang }),
  generateSentence: (vocab: object[], weakHanzi: string[], lang: string) =>
    api.post('/writing/generate', { vocab, weak_hanzi: weakHanzi, lang }),
}

// ── Grammar ───────────────────────────────────────────────────────────────────
export const grammarApi = {
  generateSentence: (knownWords: string[], performance: string, lang: string) =>
    api.post('/grammar/generate', { known_words: knownWords, performance, lang }),
  submitAnswer: (correct: boolean, xp: number) =>
    api.post('/grammar/answer', { correct, xp }),
}

// ── Speaking ──────────────────────────────────────────────────────────────────
export const speakingApi = {
  evaluate: (audioBlob: Blob, hanzi: string, pinyin: string) => {
    const fd = new FormData()
    fd.append('audio', audioBlob, 'recording.wav')
    fd.append('hanzi', hanzi)
    fd.append('pinyin', pinyin)
    return api.post('/speaking/evaluate', fd)
  },
}

// ── Arena ─────────────────────────────────────────────────────────────────────
export const arenaApi = {
  getWords: () => api.get('/arena/words'),
  submitScore: (score: number, combo: number, correct: number, total: number) =>
    api.post('/arena/score', { score, combo, correct, total }),
  commentator: (score: number, combo: number, correct: number, total: number, timeLeft: number) =>
    api.post('/arena/comment', { score, combo, correct, total, time_left: timeLeft }),
}

// ── Audio / TTS ───────────────────────────────────────────────────────────────
export const audioApi = {
  tts: (text: string, lang: 'zh' | 'en') =>
    api.get('/audio/tts', { params: { text, lang }, responseType: 'blob' }),
}

// ── Leaderboard ───────────────────────────────────────────────────────────────
export const leaderboardApi = {
  global: () => api.get('/leaderboard/global'),
  weekly: () => api.get('/leaderboard/weekly'),
}

// ── AI Coach ──────────────────────────────────────────────────────────────────
export const coachApi = {
  check: (goal: number, history: Record<string, number>) =>
    api.post('/coach/check', { goal, history }),
}

// ── Mistakes ──────────────────────────────────────────────────────────────────
export const mistakesApi = {
  list: () => api.get('/mistakes'),
  resolve: (id: string) => api.delete(`/mistakes/${id}`),
}
