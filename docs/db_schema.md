# Database Schema Design

## Overview

Supabase (PostgreSQL + PostGIS) 기반 스키마 설계
- 확장성: 블랙야크 100대 명산 → 한국 전체 산으로 확장 가능
- 위치 기반: PostGIS를 활용한 지리 정보 저장 및 쿼리

## ERD (Entity Relationship Diagram)

```
mountains (1) ──── (N) trails
    │                    │
    │                    └──── (N) trail_points (GPX 좌표)
    │
    ├──── (N) certification_points
    │
    ├──── (N) parking_lots
    │
    ├──── (N) highlights
    │
    └──── (N) mountain_images

users (1) ──── (N) user_completions ──── (1) mountains
    │
    └──── (N) user_completion_photos
```

## Tables

### 1. mountains (산 기본 정보)

```sql
CREATE TABLE mountains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,                    -- 산 이름
    name_hanja VARCHAR(100),                       -- 한자명
    altitude INTEGER,                              -- 해발고도 (m)

    -- 위치 정보
    region VARCHAR(50) NOT NULL,                   -- 시/도 (예: 경상북도)
    sub_region VARCHAR(50),                        -- 시/군/구 (예: 군위군)
    address TEXT,                                  -- 상세 주소
    location GEOGRAPHY(POINT, 4326),               -- PostGIS 좌표 (정상 기준)

    -- 분류
    category VARCHAR(50)[] DEFAULT '{}',           -- ['blackyak_100', 'national_park', 'forest_service_300']
    national_park_name VARCHAR(100),               -- 국립공원명 (해당시)

    -- 설명
    description TEXT,                              -- 산 소개
    significance TEXT,                             -- 명산으로서의 의미
    best_season VARCHAR(50)[],                     -- 추천 계절 ['봄', '가을']

    -- 메타
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_mountains_name ON mountains(name);
CREATE INDEX idx_mountains_region ON mountains(region);
CREATE INDEX idx_mountains_category ON mountains USING GIN(category);
CREATE INDEX idx_mountains_location ON mountains USING GIST(location);
```

### 2. trails (등산로/코스)

```sql
CREATE TABLE trails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mountain_id UUID REFERENCES mountains(id) ON DELETE CASCADE,

    -- 기본 정보
    name VARCHAR(200) NOT NULL,                    -- 코스명 (예: "갓바위 코스")
    trail_head VARCHAR(200),                       -- 들머리 (예: "갓바위 주차장")
    trail_end VARCHAR(200),                        -- 날머리

    -- 코스 특성
    distance_km DECIMAL(5,2),                      -- 거리 (km)
    estimated_time_minutes INTEGER,                -- 예상 소요 시간 (분)
    difficulty VARCHAR(20),                        -- 난이도: easy, moderate, hard, expert
    elevation_gain INTEGER,                        -- 누적 상승고도 (m)
    elevation_loss INTEGER,                        -- 누적 하강고도 (m)

    -- 시간대 분류
    time_category VARCHAR(20),                     -- shortest, 2-3h, 4-5h, 5h+

    -- 코스 유형
    is_circular BOOLEAN DEFAULT FALSE,             -- 원점회귀 여부
    is_recommended BOOLEAN DEFAULT FALSE,          -- 추천 코스 여부

    -- 상세 정보
    description TEXT,                              -- 코스 설명
    cautions TEXT,                                 -- 주의사항 (위험 구간 등)

    -- GPX 데이터
    gpx_file_url TEXT,                             -- GPX 파일 URL
    route_geometry GEOGRAPHY(LINESTRING, 4326),   -- 경로 좌표 (PostGIS)

    -- 메타
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_trails_mountain ON trails(mountain_id);
CREATE INDEX idx_trails_time_category ON trails(time_category);
CREATE INDEX idx_trails_difficulty ON trails(difficulty);
```

### 3. trail_points (GPX 좌표 포인트)

```sql
CREATE TABLE trail_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trail_id UUID REFERENCES trails(id) ON DELETE CASCADE,

    sequence INTEGER NOT NULL,                     -- 순서
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    elevation DECIMAL(7, 2),                       -- 고도 (m)

    point_type VARCHAR(20) DEFAULT 'waypoint',     -- waypoint, danger, rest, view
    description TEXT,                              -- 포인트 설명

    location GEOGRAPHY(POINT, 4326),               -- PostGIS 좌표

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_trail_points_trail ON trail_points(trail_id);
CREATE INDEX idx_trail_points_sequence ON trail_points(trail_id, sequence);
```

### 4. certification_points (인증 장소)

```sql
CREATE TABLE certification_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mountain_id UUID REFERENCES mountains(id) ON DELETE CASCADE,

    name VARCHAR(200) NOT NULL,                    -- 인증지 이름
    description TEXT,                              -- 설명

    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    location GEOGRAPHY(POINT, 4326),

    -- 블랙야크 관련
    is_blackyak_official BOOLEAN DEFAULT FALSE,    -- 블랙야크 공식 인증지 여부
    blackyak_stamp_available BOOLEAN DEFAULT FALSE, -- 스탬프 가능 여부

    image_url TEXT,                                -- 인증지 사진

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_cert_points_mountain ON certification_points(mountain_id);
```

### 5. parking_lots (주차장)

```sql
CREATE TABLE parking_lots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mountain_id UUID REFERENCES mountains(id) ON DELETE CASCADE,

    name VARCHAR(200) NOT NULL,                    -- 주차장 이름
    address TEXT,                                  -- 주소

    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    location GEOGRAPHY(POINT, 4326),

    -- 요금 정보
    fee_type VARCHAR(20),                          -- free, paid, mixed
    fee_description TEXT,                          -- 요금 상세 (예: "소형 2,000원/일")

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

-- 인덱스
CREATE INDEX idx_parking_mountain ON parking_lots(mountain_id);
CREATE INDEX idx_parking_location ON parking_lots USING GIST(location);
```

### 6. highlights (추천 장소/볼거리)

```sql
CREATE TABLE highlights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mountain_id UUID REFERENCES mountains(id) ON DELETE CASCADE,
    trail_id UUID REFERENCES trails(id) ON DELETE SET NULL,

    name VARCHAR(200) NOT NULL,                    -- 장소 이름
    category VARCHAR(50),                          -- viewpoint, temple, waterfall, rock, etc.
    description TEXT,                              -- 설명

    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    location GEOGRAPHY(POINT, 4326),

    best_season VARCHAR(50)[],                     -- 추천 계절
    image_url TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_highlights_mountain ON highlights(mountain_id);
CREATE INDEX idx_highlights_category ON highlights(category);
```

### 7. mountain_images (산 이미지)

```sql
CREATE TABLE mountain_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mountain_id UUID REFERENCES mountains(id) ON DELETE CASCADE,
    trail_id UUID REFERENCES trails(id) ON DELETE SET NULL,

    image_url TEXT NOT NULL,
    thumbnail_url TEXT,

    image_type VARCHAR(50),                        -- trail_map, photo, panorama
    caption TEXT,
    source TEXT,                                   -- 출처

    display_order INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_mountain_images_mountain ON mountain_images(mountain_id);
```

### 8. users (사용자) - Supabase Auth 연동

```sql
-- Supabase Auth의 auth.users와 연동되는 프로필 테이블
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    nickname VARCHAR(50),
    avatar_url TEXT,

    -- 통계
    total_completions INTEGER DEFAULT 0,
    blackyak_completions INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 9. user_completions (완등 기록)

```sql
CREATE TABLE user_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    mountain_id UUID REFERENCES mountains(id) ON DELETE CASCADE,

    completed_at DATE NOT NULL,                    -- 완등 날짜
    trail_id UUID REFERENCES trails(id),           -- 이용한 코스

    memo TEXT,                                     -- 메모
    weather VARCHAR(50),                           -- 날씨
    companion_count INTEGER DEFAULT 1,             -- 동행 인원

    -- 블랙야크 인증
    blackyak_certified BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, mountain_id, completed_at)     -- 같은 날 같은 산 중복 방지
);

-- 인덱스
CREATE INDEX idx_completions_user ON user_completions(user_id);
CREATE INDEX idx_completions_mountain ON user_completions(mountain_id);
CREATE INDEX idx_completions_date ON user_completions(completed_at);
```

### 10. user_completion_photos (인증샷)

```sql
CREATE TABLE user_completion_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    completion_id UUID REFERENCES user_completions(id) ON DELETE CASCADE,

    image_url TEXT NOT NULL,
    thumbnail_url TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_completion_photos_completion ON user_completion_photos(completion_id);
```

## Row Level Security (RLS)

```sql
-- user_profiles: 본인만 수정 가능, 조회는 모두 가능
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public profiles are viewable by everyone"
ON user_profiles FOR SELECT
USING (true);

CREATE POLICY "Users can update own profile"
ON user_profiles FOR UPDATE
USING (auth.uid() = id);

-- user_completions: 본인만 CRUD 가능
ALTER TABLE user_completions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own completions"
ON user_completions FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own completions"
ON user_completions FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own completions"
ON user_completions FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own completions"
ON user_completions FOR DELETE
USING (auth.uid() = user_id);
```

## Useful Queries

### 블랙야크 100대 명산 목록
```sql
SELECT * FROM mountains
WHERE 'blackyak_100' = ANY(category)
ORDER BY name;
```

### 특정 시간대 코스 검색
```sql
SELECT m.name as mountain_name, t.*
FROM trails t
JOIN mountains m ON t.mountain_id = m.id
WHERE t.time_category = '2-3h'
ORDER BY m.name;
```

### 사용자 완등 현황
```sql
SELECT
    m.name,
    m.region,
    uc.completed_at,
    uc.blackyak_certified
FROM user_completions uc
JOIN mountains m ON uc.mountain_id = m.id
WHERE uc.user_id = '{user_id}'
ORDER BY uc.completed_at DESC;
```

### 근처 주차장 검색 (반경 5km)
```sql
SELECT * FROM parking_lots
WHERE ST_DWithin(
    location,
    ST_GeogFromText('POINT(128.123 35.456)'),
    5000  -- 5km in meters
)
ORDER BY ST_Distance(location, ST_GeogFromText('POINT(128.123 35.456)'));
```
