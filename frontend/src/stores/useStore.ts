// stores/useStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { UserProfile, Lang } from '@/types'

interface AppState {
  profile: UserProfile | null
  token: string | null
  lang: Lang
  audioEnabled: boolean
  setProfile: (p: UserProfile | null) => void
  setToken: (t: string | null) => void
  setLang: (l: Lang) => void
  setAudioEnabled: (e: boolean) => void
  updateProfile: (partial: Partial<UserProfile>) => void
  logout: () => void
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      profile: null,
      token: null,
      lang: 'en',
      audioEnabled: true,

      setProfile: (p) => set({ profile: p }),
      setToken: (t) => set({ token: t }),
      setLang: (l) => set({ lang: l }),
      setAudioEnabled: (e) => set({ audioEnabled: e }),
      updateProfile: (partial) =>
        set((s) => ({
          profile: s.profile ? { ...s.profile, ...partial } : null,
        })),
      logout: () => set({ profile: null, token: null }),
    }),
    { name: 'hanziflow-store', partialize: (s) => ({ token: s.token, lang: s.lang }) }
  )
)
