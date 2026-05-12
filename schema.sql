-- ─────────────────────────────────────────────
-- The Architect 운명 챗봇 — Supabase DB Schema
-- Supabase SQL Editor에서 실행
-- ─────────────────────────────────────────────

-- 1. 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    birth_date TEXT,
    birth_time TEXT,
    gender TEXT,
    bricks INT DEFAULT 10,  -- 무료 벽돌 10개
    total_readings INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 벽돌 거래 내역
CREATE TABLE IF NOT EXISTS brick_transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount INT NOT NULL,  -- 양수=충전, 음수=사용
    reason TEXT NOT NULL,  -- 'purchase_1', 'purchase_10', 'purchase_20', 'reading_past_life', 'reading_keywords', 'reading_daily', 'reading_deep_dive', 'signup_bonus'
    stripe_session_id TEXT,  -- 결제 시 Stripe 세션 ID
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 리딩 기록
CREATE TABLE IF NOT EXISTS readings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    mode TEXT NOT NULL,  -- 'past_life', 'keywords', 'daily', 'deep_dive'
    content TEXT,  -- 리딩 결과 저장
    bricks_used INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 인덱스
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_brick_transactions_user ON brick_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_readings_user ON readings(user_id);

-- 5. updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- 6. RLS (Row Level Security) 정책
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE brick_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE readings ENABLE ROW LEVEL SECURITY;

-- Service role은 모든 접근 허용 (webhook에서 사용)
CREATE POLICY "Service role full access on users"
    ON users FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role full access on brick_transactions"
    ON brick_transactions FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role full access on readings"
    ON readings FOR ALL
    USING (true)
    WITH CHECK (true);
