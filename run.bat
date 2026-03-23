@echo off
title HanziFlow Launcher

echo Pokretanje Backenda...
start cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

echo Pokretanje Frontenda...
start cmd /k "cd frontend && npm run dev"

echo Oba servera se podizu. Uzivaj u kodiranju!