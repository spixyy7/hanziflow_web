-- supabase/schema.sql
-- Run this in Supabase SQL Editor

create table if not exists profiles (
  id                uuid primary key default gen_random_uuid(),
  created_at        timestamptz default now(),
  username          text unique not null,
  email             text unique not null,
  password_hash     text not null,

  -- Progress
  xp                int default 0,
  level             int default 1,
  streak            int default 0,
  daily_xp          int default 0,
  daily_goal        int default 100,
  last_date         text default '',
  streak_earned_today text default '',
  longest_streak    int default 0,
  streak_shields    int default 2,
  total_correct     int default 0,
  total_answered    int default 0,
  grammar_completed int default 0,
  arena_score       int default 0,

  -- JSON data
  vocab             jsonb default '[]',
  mistakes          jsonb default '{"words": [], "sentences": []}',
  achievements      jsonb default '[]',
  daily_xp_history  jsonb default '{}',
  completed_days    jsonb default '[]',
  preferred_quiz_modes jsonb default '{"type": 3, "draw": 2, "listen": 2, "meaning": 2}',

  -- Settings
  lang              text default 'en',
  audio_enabled     bool default true,
  theme             text default 'system',
  show_rank         bool default true,
  show_nickname     bool default true,
  goal_setup_done   bool default false,

  -- Profile
  avatar_url        text default '',
  banner_url        text default '',

  -- AI Coach cache
  last_goal_check   text default '',
  cached_coach_msg  text default '',
  last_gemini_ach_check text default ''
);

-- Leaderboard view
create or replace view leaderboard_global as
  select id, username, xp, level, streak, arena_score, avatar_url
  from profiles
  order by xp desc
  limit 100;

-- RLS: users can only read/write their own data
alter table profiles enable row level security;

create policy "Users read own profile"
  on profiles for select using (true);  -- public leaderboard

create policy "Users update own profile"
  on profiles for update using (auth.uid()::text = id::text);

-- Storage bucket for avatars
insert into storage.buckets (id, name, public) 
  values ('avatars', 'avatars', true)
  on conflict do nothing;
