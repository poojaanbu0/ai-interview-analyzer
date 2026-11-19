-- Full schema creation for Kyra Nova
-- Run this in Supabase SQL Editor

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(15),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL CHECK (role IN ('hr', 'candidate')),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);

-- 2. Interview Rooms (NEW)
CREATE TABLE IF NOT EXISTS interview_rooms (
    id SERIAL PRIMARY KEY,
    hr_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_title VARCHAR(200) NOT NULL,
    job_description TEXT NOT NULL,
    requirements TEXT,
    location VARCHAR(150),
    employment_type VARCHAR(50),
    experience_level VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_interview_rooms_hr_id ON interview_rooms(hr_id);

-- 3. Interviews
CREATE TABLE IF NOT EXISTS interviews (
    id SERIAL PRIMARY KEY,
    hr_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_id INTEGER REFERENCES interview_rooms(id) ON DELETE CASCADE,
    job_title VARCHAR(200) NOT NULL,
    job_description TEXT NOT NULL,
    requirements TEXT,
    location VARCHAR(150),
    employment_type VARCHAR(50),
    experience_level VARCHAR(50),
    candidate_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    candidate_summary TEXT,
    resume_url TEXT,
    scheduled_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_interviews_hr_id ON interviews(hr_id);
CREATE INDEX IF NOT EXISTS ix_interviews_room_id ON interviews(room_id);
CREATE INDEX IF NOT EXISTS ix_interviews_candidate_id ON interviews(candidate_id);

-- 4. Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL,
    question TEXT NOT NULL,
    transcript TEXT,
    speech_metrics JSONB,
    answer_analysis JSONB,
    UNIQUE (interview_id, sequence_number)
);
CREATE INDEX IF NOT EXISTS ix_conversations_interview_id ON conversations(interview_id);

-- 5. Interview Reports
CREATE TABLE IF NOT EXISTS interview_reports (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL UNIQUE REFERENCES interviews(id) ON DELETE CASCADE,
    report_data JSONB NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT now()
);
