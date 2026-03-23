# HanziFlow Web

The web version of the HanziFlow desktop application.

## Tech Stack
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS + Framer Motion
- **Backend**: FastAPI (Python) 
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenRouter (Gemini 3 Flash Preview)
- **TTS**: gTTS + Gemini TTS

## Setup

### 1. Supabase
1. Create a project on [supabase.com](https://supabase.com)
2. Go to SQL Editor and run `backend/supabase/schema.sql`
3. Copy the `Project URL` and `service_role key`

### 2. Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Fill in your keys in .env
uvicorn main:app --reload --port 8000
```

### 3. Frontend (Next.js)
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Fill in your environment variables
npm run dev
```

The app will open at: **http://localhost:3000**

## Deploy

### Backend → Railway
1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Add environment variables
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel
1. Go to [vercel.com](https://vercel.com) → Import Git Repository
2. Set `NEXT_PUBLIC_API_URL` to your Railway URL
3. Deploy

## Structure
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

## Implemented Features
- ✅ Auth (login/register)
- ✅ Dashboard with stats, XP chart, AI Coach
- ✅ Writing mode with AI translation check
- ✅ Sentence Builder with dnd-kit drag & drop
- ✅ Quiz with SM2 spaced repetition algorithm
- ✅ Grammar sentence generation
- ✅ Speaking AI evaluation (Gemini)
- ✅ Arena word game
- ✅ Leaderboard (global + weekly)
- ✅ TTS audio (gTTS + Gemini)
- ✅ Vocabulary management + AI extraction
- ✅ Mistakes review
- ✅ Achievements system
- ✅ Streak tracking w