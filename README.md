# 🏮 HanziFlow Web

A comprehensive full-stack web application for learning Chinese, featuring AI-powered tools, gamified progression, and spaced repetition systems.

---

## 🚀 Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Framer Motion.
- **Backend**: FastAPI (Python 3.13), Uvicorn, Pydantic.
- **Database**: Supabase (PostgreSQL) with RLS.
- **AI Integration**: OpenRouter (Gemini 3 Flash), Google Gemini API.
- **State Management**: Zustand.
- **Speech/Audio**: gTTS & Gemini-powered TTS.

---

## ✨ Key Features

- **🔐 Secure Auth**: Custom JWT-based authentication with salted password hashing.
- **📊 Interactive Dashboard**: Real-time XP tracking, daily goals, and an AI Language Coach.
- **🧠 Smart Quiz**: Vocabulary retention powered by the **SM2 Spaced Repetition** algorithm.
- **✍️ AI Writing**: Real-time stroke and translation validation using LLMs.
- **🎮 Language Arena**: Competitive word games and sentence builders with drag-and-drop.
- **🗣️ Speaking Evaluation**: AI-driven pronunciation feedback and speaking exercises.
- **🏆 Gamification**: Global/Weekly leaderboards, achievement system, and streak protection.
- **🌑 Modern UI**: Fully responsive design with native Dark Mode support.

---

## 🛠 Setup & Installation

### 1. Database Setup
1. Create a project at [supabase.com](https://supabase.com).
2. Execute the schema found in `backend/supabase/schema.sql` using the Supabase SQL Editor.
3. Obtain your `Project URL` and `service_role` key.

### 2. Backend Configuration
```bash
cd backend
python -m venv venv

# Activate venv:
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Fill in your credentials in .env
uvicorn main:app --reload --port 8000
3. Frontend Configuration
Bash
cd frontend
npm install
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL to http://localhost:8000
npm run dev
📂 Project Structure
Plaintext
hanziflow-web/
├── frontend/
│   ├── src/
│   │   ├── app/            # Pages (auth, dashboard, quiz, arena)
│   │   ├── components/     # UI & Logic components
│   │   ├── lib/            # API clients (Axios)
│   │   └── stores/         # Zustand global state
│   └── package.json
└── backend/
    ├── main.py             # FastAPI entry point
    ├── routers/            # Auth, Vocab, Quiz, AI modules
    ├── core/               # Security & DB settings
    └── requirements.txt
🚢 Deployment
Backend (Railway)
Link your GitHub repo to Railway.app.

Add environment variables (copied from .env).

Set start command: uvicorn main:app --host 0.0.0.0 --port $PORT

Frontend (Vercel)
Import the repository to Vercel.

Set NEXT_PUBLIC_API_URL to your production Railway URL.

Deploy.

📝 License
Distributed under the MIT License.

Developed with ❤️ by Josh