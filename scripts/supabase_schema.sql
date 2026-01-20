-- ============================================
-- 블랙야크 100대 명산 트래커 - Supabase Schema
-- ============================================
-- 실행 방법: Supabase Dashboard > SQL Editor에서 실행

-- 1. PostGIS 확장 활성화 (위치 기반 쿼리용)
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================
-- 핵심 테이블
-- ============================================

-- 1. mountains (산 기본 정보)
CREATE TABLE IF NOT EXISTS mountains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 기본 정보
    name VARCHAR(100) NOT NULL,                    -- 산 이름 (예: "팔공산", "가야산(경상)")
    name_origin VARCHAR(100),                      -- 원래 산 이름 (괄호 제거)
    altitude INTEGER,                              -- 해발고도 (m)

    -- 위치 정보
    region VARCHAR(50) NOT NULL,                   -- 시/도 (예: 경상북도)
    address TEXT,                                  -- 상세 주소
    latitude DECIMAL(10, 7),                       -- 위도
    longitude DECIMAL(10, 7),                      -- 경도

    -- 분류
    category VARCHAR(50)[] DEFAULT ARRAY['blackyak_100'],  -- 분류 태그
    first_char VARCHAR(10),                        -- 한글 초성 (ㄱ, ㄴ, ...)

    -- 인증 정보
    certification_point VARCHAR(200),              -- 인증지 이름 (정상, 비로봉 등)

    -- 이미지
    image_url TEXT,                                -- 대표 이미지 URL

    -- 설명
    description TEXT,                              -- 산 소개
    significance TEXT,                             -- 명산으로서의 의미

    -- 메타
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_mountains_name ON mountains(name);
CREATE INDEX IF NOT EXISTS idx_mountains_region ON mountains(region);
CREATE INDEX IF NOT EXISTS idx_mountains_first_char ON mountains(first_char);
CREATE INDEX IF NOT EXISTS idx_mountains_category ON mountains USING GIN(category);

-- 2. trails (등산로/코스)
CREATE TABLE IF NOT EXISTS trails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mountain_id UUID REFERENCES mountains(id) ON DELETE CASCADE,

    -- 기본 정보
    name VARCHAR(200) NOT NULL,                    -- 코스명 (예: "갓바위 코스")
    trail_head VARCHAR(200),                       -- 들머리
    trail_end VARCHAR(200),                        -- 날머리

    -- 코스 특성
    distance_km DECIMAL(5,2),                      -- 거리 (km)
    estimated_time_minutes INTEGER,                -- 예상 소요 시간 (분)
    difficulty VARCHAR(20),                        -- 난이도: easy, moderate, hard, expert
    elevation_gain INTEGER,                        -- 누적 상승고도 (m)

    -- 시간대 분류
    time_category VARCHAR(20),                     -- shortest, 2-3h, 4-5h, 5h+

    -- 코스 유형
    is_circular BOOLEAN DEFAULT FALSE,             -- 원점회귀 여부
    is_recommended BOOLEAN DEFAULT FALSE,          -- 추천 코스 여부

    -- 상세 정보
    description TEXT,                              -- 코스 설명
    cautions TEXT,                                 -- 주의사항

    -- GPX 데이터
    gpx_file_url TEXT,                             -- GPX 파일 URL

    -- 메타
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_trails_mountain ON trails(mountain_id);
CREATE INDEX IF NOT EXISTS idx_trails_time_category ON trails(time_category);
CREATE INDEX IF NOT EXISTS idx_trails_difficulty ON trails(difficulty);

-- 3. parking_lots (주차장)
CREATE TABLE IF NOT EXISTS parking_lots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mountain_id UUID REFERENCES mountains(id) ON DELETE CASCADE,

    name VARCHAR(200) NOT NULL,                    -- 주차장 이름
    address TEXT,                                  -- 주소

    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),

    -- 요금 정보
    fee_type VARCHAR(20),                          -- free, paid, mixed
    fee_description TEXT,                          -- 요금 상세

    -- 운영 정보
    capacity INTEGER,                              -- 수용 대수
    operating_hours TEXT,                          -- 운영 시간

    -- 편의시설
    has_restroom BOOLEAN DEFAULT FALSE,
    has_store BOOLEAN DEFAULT FALSE,

    -- 관련 등산로
    nearby_trail_head TEXT,                        -- 연결되는 들머리

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_parking_mountain ON parking_lots(mountain_id);

-- 4. highlights (추천 장소/볼거리)
CREATE TABLE IF NOT EXISTS highlights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mountain_id UUID REFERENCES mountains(id) ON DELETE CASCADE,

    name VARCHAR(200) NOT NULL,                    -- 장소 이름
    category VARCHAR(50),                          -- viewpoint, temple, waterfall, rock, etc.
    description TEXT,                              -- 설명

    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),

    image_url TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_highlights_mountain ON highlights(mountain_id);

-- ============================================
-- 사용자 관련 테이블 (Phase 2)
-- ============================================

-- 5. user_profiles (사용자 프로필) - Supabase Auth 연동
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    nickname VARCHAR(50),
    avatar_url TEXT,

    -- 통계
    total_completions INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. user_completions (완등 기록)
CREATE TABLE IF NOT EXISTS user_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    mountain_id UUID REFERENCES mountains(id) ON DELETE CASCADE,

    completed_at DATE NOT NULL,                    -- 완등 날짜
    trail_id UUID REFERENCES trails(id),           -- 이용한 코스

    memo TEXT,                                     -- 메모
    weather VARCHAR(50),                           -- 날씨

    -- 블랙야크 인증
    blackyak_certified BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, mountain_id, completed_at)
);

CREATE INDEX IF NOT EXISTS idx_completions_user ON user_completions(user_id);
CREATE INDEX IF NOT EXISTS idx_completions_mountain ON user_completions(mountain_id);

-- 7. user_completion_photos (인증샷)
CREATE TABLE IF NOT EXISTS user_completion_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    completion_id UUID REFERENCES user_completions(id) ON DELETE CASCADE,

    image_url TEXT NOT NULL,
    thumbnail_url TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_completion_photos ON user_completion_photos(completion_id);

-- ============================================
-- Row Level Security (RLS)
-- ============================================

-- mountains, trails, parking_lots, highlights: Public Read
ALTER TABLE mountains ENABLE ROW LEVEL SECURITY;
ALTER TABLE trails ENABLE ROW LEVEL SECURITY;
ALTER TABLE parking_lots ENABLE ROW LEVEL SECURITY;
ALTER TABLE highlights ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Mountains are viewable by everyone" ON mountains
    FOR SELECT USING (true);

CREATE POLICY "Trails are viewable by everyone" ON trails
    FOR SELECT USING (true);

CREATE POLICY "Parking lots are viewable by everyone" ON parking_lots
    FOR SELECT USING (true);

CREATE POLICY "Highlights are viewable by everyone" ON highlights
    FOR SELECT USING (true);

-- user_profiles: 본인만 수정 가능
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public profiles are viewable by everyone" ON user_profiles
    FOR SELECT USING (true);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- user_completions: 본인만 CRUD 가능
ALTER TABLE user_completions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own completions" ON user_completions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own completions" ON user_completions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own completions" ON user_completions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own completions" ON user_completions
    FOR DELETE USING (auth.uid() = user_id);

-- user_completion_photos: completion 소유자만 접근
ALTER TABLE user_completion_photos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own completion photos" ON user_completion_photos
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_completions uc
            WHERE uc.id = completion_id AND uc.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own completion photos" ON user_completion_photos
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM user_completions uc
            WHERE uc.id = completion_id AND uc.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own completion photos" ON user_completion_photos
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM user_completions uc
            WHERE uc.id = completion_id AND uc.user_id = auth.uid()
        )
    );

-- ============================================
-- Triggers
-- ============================================

-- updated_at 자동 업데이트 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 각 테이블에 트리거 적용
CREATE TRIGGER update_mountains_updated_at BEFORE UPDATE ON mountains
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trails_updated_at BEFORE UPDATE ON trails
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parking_lots_updated_at BEFORE UPDATE ON parking_lots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_completions_updated_at BEFORE UPDATE ON user_completions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 새 사용자 가입 시 프로필 자동 생성
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id)
    VALUES (NEW.id)
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ language 'plpgsql' SECURITY DEFINER;

-- 기존 트리거 삭제 후 재생성
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- ============================================
-- 완료 메시지
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '블랙야크 100대 명산 트래커 스키마 생성 완료!';
    RAISE NOTICE '테이블: mountains, trails, parking_lots, highlights, user_profiles, user_completions, user_completion_photos';
END $$;
