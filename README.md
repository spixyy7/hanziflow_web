# HanziFlow Web

Identična web verzija HanziFlow desktop aplikacije.

## Tech Stack
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS + Framer Motion
- **Backend**: FastAPI (Python) 
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenRouter (Gemini 3 Flash Preview)
- **TTS**: gTTS + Gemini TTS

## Setup

### 1. Supabase
1. Napravi projekat na [supabase.com](https://supabase.com)
2. Idi u SQL Editor i pokreni `backend/supabase/schema.sql`
3. Uzmi `Project URL` i `service_role key`

### 2. Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Popuni .env sa tvojim ključevima
uvicorn main:app --reload --port 8000
```

### 3. Frontend (Next.js)
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Popuni .env.local
npm run dev
```

App se otvara na: **http://localhost:3000**

## Deploy

### Backend → Railway
1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Dodaj environment variables
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel
1. [vercel.com](https://vercel.com) → Import Git Repository
2. Set `NEXT_PUBLIC_API_URL` na Railway URL
3. Deploy

## Struktura
```
hanziflow-web/
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages (auth, dashboard, quiz, writing...)
│   │   ├── components/    # Reusable components
│   │   ├── lib/           # API client
│   │   ├── stores/        # Zustand state
│   │   └── types/         # TypeScript types
│   └── package.json
│
└── backend/
    ├── main.py            # FastAPI app
    ├── routers/           # auth, quiz, writing, grammar, speaking, arena...
    ├── core/              # DB, settings
    ├── supabase/          # SQL schema
    └── requirements.txt
```

## Features implementovane
- ✅ Auth (login/register)
- ✅ Dashboard sa stats, XP chart, AI Coach
- ✅ Writing mode sa AI provjером prijevoda
- ✅ Sentence Builder sa dnd-kit drag&drop
- ✅ Quiz sa SM2 spaced repetition algoritmom
- ✅ Grammar sentence generation
- ✅ Speaking AI evaluacija (Gemini)
- ✅ Arena word game
- ✅ Leaderboard (global + weekly)
- ✅ TTS audio (gTTS + Gemini)
- ✅ Vocabulary management + AI extract
- ✅ Mistakes review
- ✅ Achievements system
- ✅ Streak tracking sa shields
- ✅ Dark mode
