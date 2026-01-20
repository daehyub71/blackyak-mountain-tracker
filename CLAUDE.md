# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**blackyak-mountain-tracker** - 블랙야크 100대 명산 챌린지를 도전하는 등산객들을 위한 종합 정보 플랫폼

### Target Users
- 블랙야크 100대 명산 챌린지 참여자
- 향후 한국의 산 전체 등산객으로 확장 예정

### Core Features
1. 100대 명산 리스트 및 기본 정보 (인증지, 주소, 의미)
2. 등산로 정보 (들머리, 코스, 주차장, 입장료)
3. 시간대별 코스 추천 (최단, 2-3시간, 4-5시간, 5시간+)
4. 추천 장소 및 등산로 이미지
5. GPX 파일 다운로드 (램블러, 트랭글 호환)
6. 개인 진행률 트래킹 (완등 현황, 인증샷)

## Tech Stack

### Backend
- **Runtime**: Python 3.11+
- **Framework**: FastAPI (필요시) or Supabase Edge Functions
- **Database**: Supabase (PostgreSQL + PostGIS)
- **Cache**: Upstash Redis (optional)

### Frontend
- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Map**: Kakao Map JavaScript SDK
- **State**: Zustand + TanStack Query

### Infrastructure
- **Database/Auth**: Supabase
- **Deployment**: Vercel
- **Image Storage**: Supabase Storage or Cloudinary
- **Domain**: TBD

## Project Structure

```
blackyak-mountain-tracker/
├── backend/                 # FastAPI backend (if needed)
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   └── services/
│   ├── requirements.txt
│   └── .env
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── .env
├── scripts/                 # Data collection scripts
│   ├── crawl_blackyak_100.py
│   ├── fetch_national_park_api.py
│   └── generate_gpx.py
├── data/                    # Raw and processed data
│   ├── raw/
│   └── processed/
├── docs/                    # Documentation
│   ├── 개발계획서.md
│   ├── db_schema.md
│   └── wireframes/
└── CLAUDE.md
```

## Development Commands

### Scripts (Data Collection)
```bash
cd scripts
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crawl Black Yak 100 mountains
python crawl_blackyak_100.py

# Fetch National Park API data
python fetch_national_park_api.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Development server (http://localhost:5173)
npm run build        # Production build
npm run lint         # ESLint
npm run type-check   # TypeScript check
```

### Backend (if needed)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Environment Variables

### Supabase
```bash
SUPABASE_URL=https://{project}.supabase.co
SUPABASE_ANON_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY={service_role_key}
```

### Kakao Map
```bash
VITE_KAKAO_MAP_API_KEY={javascript_key}
```

### Data APIs (Optional)
```bash
DATA_GO_KR_API_KEY={공공데이터포털_API_키}
```

## Database Tables

See `docs/db_schema.md` for detailed schema.

### Core Tables
- `mountains` - 산 기본 정보
- `trails` - 등산로/코스 정보
- `certification_points` - 인증 장소
- `parking_lots` - 주차장 정보
- `highlights` - 추천 장소/볼거리
- `user_completions` - 사용자 완등 기록

## Data Sources

1. **블랙야크 공식**: 100대 명산 리스트, 인증 장소
2. **국립공원공단 API**: 22개 국립공원 등산로
3. **산림청 공공데이터**: 전국 등산로 좌표 (data.go.kr)
4. **한국등산·트레킹지원센터**: 공식 등산로 정보
5. **네이버/구글 검색**: 보조 정보 수집

## MVP Scope (Phase 1)

- [ ] 100대 명산 리스트 DB 구축
- [ ] 산 기본 정보 페이지
- [ ] 등산로 정보 (최소 1개 코스/산)
- [ ] GPX 파일 다운로드
- [ ] 반응형 웹 UI

## Future Phases

**Phase 2**: 개인 진행률 트래킹, 로그인
**Phase 3**: 날씨/계절 정보, 접근성 강화
**Phase 4**: 커뮤니티/UGC, 후기 시스템
